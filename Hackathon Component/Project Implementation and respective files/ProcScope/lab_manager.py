"""Safe, allow-listed lifecycle management for ProcScope's C lab experiments."""
from __future__ import annotations
import os
import shutil
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LAB_DIR = HERE / "lab"
SOURCE = LAB_DIR / "lab_experiments.c"
BUILD_DIR = LAB_DIR / "build"
BINARY = BUILD_DIR / "procscope-lab"
MAX_ACTIVE = 4
ALLOWED = {
    "zombie": {"title": "Zombie process", "summary": "A child finishes, but its parent delays collecting its exit status.", "expected": "A short-lived child may appear with state Z while the lab parent remains alive.", "duration": 25},
    "orphan": {"title": "Orphan re-parenting", "summary": "A parent exits while its child continues running.", "expected": "The child may be re-parented to the system's configured subreaper or init process.", "duration": 25},
    "pipeline": {"title": "Pipeline processes", "summary": "A controlled parent creates two children and connects them through a pipe.", "expected": "The parent and two child processes should be visible while the experiment runs.", "duration": 20},
    "threads": {"title": "Threads in one process", "summary": "A C program starts three worker threads using pthreads.", "expected": "The process thread count should temporarily increase; thread display depends on collector support.", "duration": 20},
    "fork-exec": {"title": "Fork and exec", "summary": "A parent creates a child that replaces its program image with sleep.", "expected": "A child process should appear; its command/executable details may change after exec.", "duration": 20},
}

class LabError(RuntimeError): pass

class LabManager:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: dict[str, dict[str, Any]] = {}
        self._last_start = 0.0

    def _compile(self) -> None:
        compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        if not compiler:
            raise LabError("A C compiler (cc, gcc, or clang) is required to run Process Lab experiments.")
        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        command = [compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(SOURCE), "-pthread", "-o", str(BINARY)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False, cwd=HERE)
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "Compiler failed.")[-2500:]
            raise LabError("Could not compile the lab experiments: " + message)

    def list_experiments(self) -> dict[str, Any]:
        return {"experiments": [{"id": key, **value} for key, value in ALLOWED.items()], "active_runs": self.status()["runs"], "compiler_available": bool(shutil.which("cc") or shutil.which("gcc") or shutil.which("clang"))}

    def start(self, experiment: str) -> dict[str, Any]:
        if experiment not in ALLOWED:
            raise LabError("Unknown experiment. Choose one of the listed experiments.")
        with self._lock:
            self._prune()
            active = [r for r in self._runs.values() if r["status"] == "running"]
            if len(active) >= MAX_ACTIVE:
                raise LabError(f"At most {MAX_ACTIVE} experiments may be active at once.")
            if time.monotonic() - self._last_start < 1.0:
                raise LabError("Please wait a moment before starting another experiment.")
            self._compile()
            run_id = uuid.uuid4().hex[:12]
            try:
                proc = subprocess.Popen([str(BINARY), experiment], cwd=HERE, stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                    start_new_session=True, close_fds=True)
            except OSError as exc:
                raise LabError(f"Could not start the experiment: {exc}") from exc
            self._runs[run_id] = {"id": run_id, "experiment": experiment, "title": ALLOWED[experiment]["title"],
                "pid": proc.pid, "pgid": proc.pid, "process": proc, "started_at": time.time(),
                "status": "running", "output": "", "output_thread": None}
            reader = threading.Thread(target=self._read_output, args=(run_id, proc), daemon=True)
            self._runs[run_id]["output_thread"] = reader
            reader.start()
            self._last_start = time.monotonic()
            return self._public(self._runs[run_id])

    def _read_output(self, run_id: str, proc: subprocess.Popen[str]) -> None:
        try:
            if proc.stdout:
                for line in proc.stdout:
                    with self._lock:
                        run = self._runs.get(run_id)
                        if run:
                            run["output"] = (run["output"] + line[-500:])[-3000:]
        except (OSError, ValueError):
            pass

    @staticmethod
    def _group_exists(pgid: int) -> bool:
        try:
            os.killpg(pgid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True

    def _prune(self) -> None:
        for run in self._runs.values():
            proc = run["process"]
            # A leader may exit while a tracked child (the orphan demo) remains.
            # Keep the run active until its dedicated process group has vanished.
            if run["status"] == "running" and proc.poll() is not None and not self._group_exists(run["pgid"]):
                run["status"] = "finished"
                run["finished_at"] = time.time()
        # Retain a bounded history; never discard active runs.
        finished = [key for key, run in self._runs.items() if run["status"] != "running"]
        for key in finished[:-40]:
            self._runs.pop(key, None)

    def _public(self, run: dict[str, Any]) -> dict[str, Any]:
        exp = ALLOWED[run["experiment"]]
        return {"id": run["id"], "experiment": run["experiment"], "title": run["title"], "pid": run["pid"],
            "status": run["status"], "started_at": run["started_at"], "output": run["output"],
            "summary": exp["summary"], "expected": exp["expected"], "duration_seconds": exp["duration"]}

    def status(self) -> dict[str, Any]:
        with self._lock:
            self._prune()
            return {"runs": [self._public(run) for run in sorted(self._runs.values(), key=lambda r: r["started_at"], reverse=True)], "max_active": MAX_ACTIVE}

    def stop(self, run_id: str) -> dict[str, Any]:
        with self._lock:
            self._prune()
            run = self._runs.get(run_id)
            if not run:
                raise LabError("That experiment run was not found. It may have already been cleaned up.")
            if run["status"] != "running":
                return self._public(run)
            # Each experiment gets its own session/process group. Only signal that group.
            try:
                os.killpg(run["pgid"], signal.SIGTERM)
            except ProcessLookupError:
                pass
            proc = run["process"]
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try: os.killpg(run["pgid"], signal.SIGKILL)
                except ProcessLookupError: pass
                try: proc.wait(timeout=2)
                except subprocess.TimeoutExpired: pass
            run["status"] = "stopped"
            run["finished_at"] = time.time()
            return self._public(run)

    def cleanup_all(self) -> None:
        with self._lock:
            ids = [r["id"] for r in self._runs.values() if r["status"] == "running"]
        for run_id in ids:
            try: self.stop(run_id)
            except LabError: pass

LAB = LabManager()
