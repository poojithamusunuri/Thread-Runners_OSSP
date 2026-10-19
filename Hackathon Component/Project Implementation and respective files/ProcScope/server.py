#!/usr/bin/env python3
"""ProcScope local server: Explorer, snapshot Timeline, and controlled Process Lab."""
from __future__ import annotations
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
STATIC = (HERE / "static").resolve()
sys.path.insert(0, str(HERE))
from proc_collector import ProcCollector, ProcCollectorError  # noqa: E402
from timeline_tracker import TimelineTracker  # noqa: E402
from lab_manager import LAB, LabError  # noqa: E402
from event_collector import EVENTS  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
TIMELINE = TimelineTracker()

class Handler(BaseHTTPRequestHandler):
    server_version = "ProcScope/1.0"
    def send_bytes(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        try: self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError): pass

    def send_json(self, status: int, value: object) -> None:
        self.send_bytes(status, json.dumps(value, separators=(",", ":")).encode(), "application/json; charset=utf-8")

    def _valid_local_origin(self) -> bool:
        origin = self.headers.get("Origin")
        return not origin or origin in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}")

    def _valid_local_host(self) -> bool:
        # Reject unexpected Host values to reduce DNS-rebinding exposure.
        host = self.headers.get("Host", "").lower().strip()
        return host in (f"{HOST}:{PORT}", f"localhost:{PORT}")

    def do_GET(self) -> None:
        if not self._valid_local_host():
            self.send_json(403, {"error": "Host header rejected; use the local ProcScope address."})
            return
        parsed = urlsplit(self.path)
        if parsed.path == "/api/snapshot":
            try:
                snapshot_data = ProcCollector().collect().as_dict()
                TIMELINE.observe(snapshot_data)
                self.send_json(200, snapshot_data)
            except ProcCollectorError as exc:
                self.send_json(503, {"error": str(exc)})
            return
        if parsed.path == "/api/timeline":
            timeline = TIMELINE.as_dict()
            event_status = EVENTS.status()
            combined = list(timeline["events"]) + list(event_status.get("events", []))
            combined.sort(key=lambda event: event.get("timestamp", 0), reverse=True)
            timeline["events"] = combined[:500]
            timeline["event_count"] = len(combined[:500])
            timeline["event_mode"] = {"status": event_status["status"], "message": event_status["message"], "events_dropped_or_overwritten": event_status["events_dropped_or_overwritten"]}
            timeline["limitations"] = list(timeline.get("limitations", [])) + list(event_status.get("limitations", []))
            self.send_json(200, timeline); return
        if parsed.path == "/api/lab/experiments":
            self.send_json(200, LAB.list_experiments()); return
        if parsed.path == "/api/lab/status":
            self.send_json(200, LAB.status()); return
        if parsed.path == "/api/events/status":
            self.send_json(200, EVENTS.status()); return
        if parsed.path == "/api/reports/summary":
            try:
                snap = ProcCollector().collect().as_dict()
                self.send_json(200, {"captured_at_unix": snap["captured_at_unix"], "process_count": len(snap["processes"]), "root_count": len(snap["roots"]), "skipped_processes": snap["skipped_processes"], "warning_count": len(snap["warnings"]), "boot_id": snap["boot_id"], "snapshot_mode": "available", "event_mode": EVENTS.status()["status"]})
            except ProcCollectorError as exc:
                self.send_json(503, {"error": str(exc)}); return
            return
        if parsed.path == "/api/health":
            self.send_json(200, {"status":"ok", "collector":"procfs-snapshot", "timeline":"snapshot-comparison", "event_mode": EVENTS.status()["status"], "lab":"allow-listed-c-experiments"}); return
        requested = unquote(parsed.path)
        if requested in ("", "/"): requested = "/index.html"
        candidate = (STATIC / requested.lstrip("/")).resolve()
        if not candidate.is_relative_to(STATIC) or not candidate.is_file():
            self.send_bytes(404, b"Not found", "text/plain; charset=utf-8"); return
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in ("application/javascript", "application/json"):
            content_type += "; charset=utf-8"
        self.send_bytes(200, candidate.read_bytes(), content_type)

    def do_POST(self) -> None:
        if not self._valid_local_host():
            self.send_json(403, {"error": "Host header rejected; use the local ProcScope address."})
            return
        parsed = urlsplit(self.path)
        if parsed.path not in ("/api/lab/run", "/api/events/start", "/api/events/stop") and not (parsed.path.startswith("/api/lab/stop/") and len(parsed.path.rsplit("/", 1)[-1]) <= 32):
            self.send_json(404, {"error":"Endpoint not found"}); return
        if not self._valid_local_origin():
            self.send_json(403, {"error":"Request origin rejected"}); return
        if parsed.path == "/api/events/start":
            self.send_json(200, EVENTS.start()); return
        if parsed.path == "/api/events/stop":
            self.send_json(200, EVENTS.stop()); return
        if parsed.path == "/api/lab/run":
            if self.headers.get_content_type() != "application/json":
                self.send_json(415, {"error":"Send a JSON request body"}); return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 2048: raise ValueError("Request body must be between 1 and 2048 bytes")
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict) or not isinstance(body.get("experiment"), str): raise ValueError("Provide an experiment ID")
                result = LAB.start(body["experiment"])
                self.send_json(201, result)
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error":str(exc)})
            except LabError as exc:
                self.send_json(400, {"error":str(exc)})
            return
        run_id = parsed.path.rsplit("/", 1)[-1]
        try:
            self.send_json(200, LAB.stop(run_id))
        except LabError as exc:
            self.send_json(404, {"error":str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print("[ProcScope] " + (fmt % args))


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"ProcScope is running at http://{HOST}:{PORT}")
    print("Explorer, Timeline, Lab, and Reports are available. Bound to localhost only.")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nStopping ProcScope.")
    finally:
        LAB.cleanup_all()
        EVENTS.stop()
        server.server_close()

if __name__ == "__main__": main()
