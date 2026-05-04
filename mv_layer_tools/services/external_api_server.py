import json
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import bpy

from . import external_control_service


HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}"

_SERVER = None
_SERVER_THREAD = None
_TASK_QUEUE = queue.Queue()
_TIMER_RUNNING = False
_LOCK = threading.Lock()


def _json_response(handler, status_code, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _run_on_main_thread(func):
    done = threading.Event()
    result = {}

    def wrapped():
        try:
            result["value"] = func()
        except Exception as exc:
            result["error"] = str(exc)
        finally:
            done.set()

    _TASK_QUEUE.put(wrapped)
    done.wait(timeout=2.0)
    if "error" in result:
        return False, {"ok": False, "error": result["error"]}
    if "value" not in result:
        return False, {"ok": False, "error": "Main-thread operation timed out"}
    return True, result["value"]


def _process_task_queue():
    global _TIMER_RUNNING
    while True:
        try:
            task = _TASK_QUEUE.get_nowait()
        except queue.Empty:
            break
        task()
    if is_running():
        return 0.05
    _TIMER_RUNNING = False
    return None


def _ensure_timer():
    global _TIMER_RUNNING
    with _LOCK:
        if _TIMER_RUNNING:
            return
        bpy.app.timers.register(_process_task_queue, first_interval=0.05, persistent=False)
        _TIMER_RUNNING = True


def _clear_timer_flag():
    global _TIMER_RUNNING
    if not is_running():
        _TIMER_RUNNING = False
    return None


class _Handler(BaseHTTPRequestHandler):
    server_version = "MVLTExternalAPI/0.1"

    def do_GET(self):
        if self.path == "/health":
            _json_response(self, 200, {"ok": True, "status": "running", "url": URL})
            return
        if self.path == "/state":
            ok, payload = _run_on_main_thread(lambda: external_control_service.get_layer_state(bpy.context))
            _json_response(self, 200 if ok else 500, payload if ok else payload)
            return
        if self.path == "/direct_edit":
            ok, payload = _run_on_main_thread(lambda: external_control_service.get_direct_edit_state(bpy.context))
            _json_response(self, 200 if ok else 500, payload if ok else payload)
            return
        _json_response(self, 404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            _json_response(self, 400, {"ok": False, "error": "Invalid JSON"})
            return

        if self.path == "/select":
            name = data.get("name")
            if not isinstance(name, str) or not name:
                _json_response(self, 400, {"ok": False, "error": "name is required"})
                return
            ok, payload = _run_on_main_thread(
                lambda: _wrap_result(external_control_service.select_layer_by_name(bpy.context, name))
            )
            _json_response(self, 200 if ok and payload.get("ok") else 400, payload)
            return

        if self.path == "/location":
            name = data.get("name")
            if not isinstance(name, str) or not name:
                _json_response(self, 400, {"ok": False, "error": "name is required"})
                return
            ok, payload = _run_on_main_thread(
                lambda: _wrap_result(
                    external_control_service.set_layer_location(
                        bpy.context,
                        name,
                        x=data.get("x"),
                        y=data.get("y"),
                        depth=data.get("depth"),
                    )
                )
            )
            _json_response(self, 200 if ok and payload.get("ok") else 400, payload)
            return

        _json_response(self, 404, {"ok": False, "error": "Not found"})

    def log_message(self, _format, *_args):
        return


def _wrap_result(result):
    success, message = result
    return {"ok": bool(success), "message": message}


def start_server():
    global _SERVER, _SERVER_THREAD
    with _LOCK:
        if _SERVER is not None:
            return False, "External API server is already running"
        _SERVER = ThreadingHTTPServer((HOST, PORT), _Handler)
        _SERVER_THREAD = threading.Thread(target=_SERVER.serve_forever, name="mvlt-external-api", daemon=True)
        _SERVER_THREAD.start()
    _ensure_timer()
    return True, f"External API server started at {URL}"


def stop_server():
    global _SERVER, _SERVER_THREAD
    with _LOCK:
        if _SERVER is None:
            return False, "External API server is not running"
        server = _SERVER
        thread = _SERVER_THREAD
        _SERVER = None
        _SERVER_THREAD = None
    server.shutdown()
    server.server_close()
    if thread is not None:
        thread.join(timeout=2.0)
    bpy.app.timers.register(_clear_timer_flag, first_interval=0.0, persistent=False)
    return True, "External API server stopped"


def is_running():
    return _SERVER is not None


def get_status():
    return {"running": is_running(), "url": URL}
