"""Optional Linux CN_PROC event listener.

This experimental collector uses NETLINK_CONNECTOR and CN_PROC where the running
kernel supports it and the current process has permission. It is deliberately
opt-in. Snapshot collection remains the reliable baseline. Events can be lost and
are not a complete historical record.
"""
from __future__ import annotations
import os
import socket
import struct
import threading
import time
from collections import deque
from typing import Any

NETLINK_CONNECTOR = 11
NLMSG_DONE = 3
CN_IDX_PROC = 1
CN_VAL_PROC = 1
PROC_CN_MCAST_LISTEN = 1
PROC_CN_MCAST_IGNORE = 2

class EventCollector:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._events: deque[dict[str, Any]] = deque(maxlen=500)
        self._status = "stopped"
        self._message = "Event collection has not been started."
        self._dropped = False

    def _send_control(self, sock: socket.socket, operation: int) -> None:
        # nlmsghdr + cn_msg + enum proc_cn_mcast_op (native-endian Linux ABI)
        payload = struct.pack("=IIIIHHI", CN_IDX_PROC, CN_VAL_PROC, 0, 0, 4, 0, operation)
        header = struct.pack("=IHHII", 16 + len(payload), NLMSG_DONE, 0, 1, os.getpid())
        sock.send(header + payload)

    def start(self) -> dict[str, Any]:
        with self._lock:
            if self._status == "listening":
                return self.status()
            if not hasattr(socket, "AF_NETLINK"):
                self._status, self._message = "unavailable", "This platform does not expose Linux netlink sockets."
                return self.status()
            try:
                sock = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, NETLINK_CONNECTOR)
            except OSError as exc:
                self._status = "unavailable"
                self._message = f"This kernel/runtime does not provide the required netlink connector: {exc}. Continue using snapshot mode."
                return self.status()
            try:
                sock.bind((os.getpid(), CN_IDX_PROC))
                sock.settimeout(0.5)
                self._send_control(sock, PROC_CN_MCAST_LISTEN)
            except OSError as exc:
                sock.close()
                self._status = "unavailable"
                self._message = f"Kernel event subscription was not available: {exc}. Continue using snapshot mode."
                return self.status()
            self._socket = sock
            self._stop.clear()
            self._status = "listening"
            self._message = "Listening for supported kernel process events. Events may be lost; snapshots remain the baseline."
            self._thread = threading.Thread(target=self._receive, name="procscope-cn-proc", daemon=True)
            self._thread.start()
            return self.status()

    def _decode(self, data: bytes) -> dict[str, Any] | None:
        # netlink header (16), connector header (20), proc_event header (16)
        if len(data) < 52:
            return None
        try:
            nl_len, nl_type, _flags, _seq, _pid = struct.unpack_from("=IHHII", data, 0)
            if nl_len > len(data) or nl_len < 52:
                return None
            idx, val, _cseq, _ack, cn_len, _cn_flags = struct.unpack_from("=IIIIHH", data, 16)
            if idx != CN_IDX_PROC or val != CN_VAL_PROC or cn_len < 16:
                return None
            what, cpu, timestamp_ns = struct.unpack_from("=IIQ", data, 36)
            payload = data[52:16 + 20 + cn_len]
            labels = {1: "fork", 2: "exec", 0x80000000: "exit", 0x40000000: "uid-change", 0x20000000: "gid-change", 0x10000000: "sid-change"}
            kind = labels.get(what)
            if not kind:
                return None
            item: dict[str, Any] = {"timestamp": time.time(), "kind": kind, "source": "kernel event", "confidence": "observed", "cpu": cpu, "kernel_timestamp_ns": timestamp_ns}
            if kind == "fork" and len(payload) >= 16:
                ppid, ptgid, child_pid, child_tgid = struct.unpack_from("=IIII", payload, 0)
                item.update({"pid": child_pid, "ppid": ppid, "parent_tgid": ptgid, "child_tgid": child_tgid, "title": "Process created", "detail": f"Kernel reported child PID {child_pid} created by parent PID {ppid}."})
            elif kind == "exec" and len(payload) >= 8:
                pid, tgid = struct.unpack_from("=II", payload, 0)
                item.update({"pid": pid, "tgid": tgid, "title": "Program executed", "detail": f"Kernel reported an exec event for PID {pid}."})
            elif kind == "exit" and len(payload) >= 16:
                pid, tgid, code, sig = struct.unpack_from("=IIII", payload, 0)
                item.update({"pid": pid, "tgid": tgid, "exit_code": code, "exit_signal": sig, "title": "Process exited", "detail": f"Kernel reported an exit event for PID {pid}."})
            else:
                return None
            return item
        except (struct.error, ValueError):
            return None

    def _receive(self) -> None:
        sock = self._socket
        if sock is None:
            return
        while not self._stop.is_set():
            try:
                data = sock.recv(65536)
            except socket.timeout:
                continue
            except OSError as exc:
                if not self._stop.is_set():
                    with self._lock:
                        self._status, self._message = "error", f"Event listener stopped: {exc}. Snapshots remain available."
                break
            item = self._decode(data)
            if item:
                with self._lock:
                    if len(self._events) == self._events.maxlen:
                        self._dropped = True
                    self._events.append(item)

    def stop(self) -> dict[str, Any]:
        with self._lock:
            sock = self._socket
            if sock is None:
                if self._status == "listening": self._status = "stopped"
                return self.status()
            try:
                self._send_control(sock, PROC_CN_MCAST_IGNORE)
            except OSError:
                pass
            self._stop.set()
            self._socket = None
            try: sock.close()
            except OSError: pass
            self._status = "stopped"
            self._message = "Event collection stopped. Snapshot collection remains available."
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        return self.status()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {"status": self._status, "message": self._message, "event_count": len(self._events), "events_dropped_or_overwritten": self._dropped, "events": list(reversed(self._events)), "limitations": ["Kernel and permission support varies; root alone does not guarantee availability.", "Events may be lost or missed; this is not a complete audit log.", "Snapshots remain the baseline and can be used independently."]}

EVENTS = EventCollector()
