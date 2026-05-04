import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

WORK_DIR = Path(r"C:\mvlt_c1_live")
PREVIEW_FILE = WORK_DIR / "preview.jpg"
STATE_FILE = WORK_DIR / "state.json"
COMMAND_FILE = WORK_DIR / "command.json"
STOP_FILE = WORK_DIR / "stop.txt"
HOST = "127.0.0.1"
PORT = 8765

HTML = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>C1 Drag MVP v3</title>
<style>
  html, body { margin: 0; height: 100%; background: #17181c; color: #e8e8e8; font-family: system-ui, sans-serif; }
  #root { display: grid; grid-template-columns: 1fr 330px; height: 100vh; }
  #stageWrap { display: flex; align-items: center; justify-content: center; overflow: hidden; background: #101114; }
  canvas { background: #050506; box-shadow: 0 10px 30px rgba(0,0,0,.45); image-rendering: auto; cursor: default; }
  canvas.dragging { cursor: grabbing; }
  #side { border-left: 1px solid #333640; padding: 14px; box-sizing: border-box; background: #20222a; }
  h1 { font-size: 16px; margin: 0 0 12px; }
  .kv { display: grid; grid-template-columns: 140px 1fr; gap: 4px 8px; font-size: 12px; margin: 10px 0; }
  .label { color: #9ca3af; }
  button { width: 100%; padding: 8px; margin: 6px 0; background: #2f3542; color: #f4f4f5; border: 1px solid #4b5563; border-radius: 8px; cursor: pointer; }
  button:hover { background: #3a4252; }
  code { color: #cbd5e1; font-size: 12px; word-break: break-all; }
  .hint { color: #b8bfcc; font-size: 12px; line-height: 1.55; margin-top: 12px; }
  .good { color: #86efac; }
  .warn { color: #fde68a; }
  .bad { color: #fca5a5; }
</style>
</head>
<body>
<div id="root">
  <div id="stageWrap"><canvas id="stage" width="960" height="540"></canvas></div>
  <aside id="side">
    <h1>C1 JPEG Drag MVP v3</h1>
    <div class="kv">
      <div class="label">Preview FPS</div><div id="previewFps">-</div>
      <div class="label">Mouse FPS</div><div id="mouseFps">-</div>
      <div class="label">Command FPS</div><div id="cmdFps">-</div>
      <div class="label">Preview age</div><div id="age">-</div>
      <div class="label">Render ms</div><div id="renderMs">-</div>
      <div class="label">Dragging</div><div id="dragging">false</div>
      <div class="label">Layer</div><div id="layer">-</div>
      <div class="label">World X</div><div id="wx">-</div>
      <div class="label">World Z</div><div id="wz">-</div>
      <div class="label">Mode</div><div><code>screen_rect from Blender</code></div>
    </div>
    <button id="centerBtn">Center Layer</button>
    <button id="stopBtn">Stop Backend</button>
    <p class="hint">
      v3は、操作枠をBlender側が返す投影矩形に合わせます。<br>
      ドラッグ中は枠だけ即時追従し、Blenderプレビューは遅れて追従します。<br><br>
      見る点: 枠と青いPlaneのズレ、Preview age、Render ms、ドラッグ中の体感。
    </p>
  </aside>
</div>
<script>
const canvas = document.getElementById('stage');
const ctx = canvas.getContext('2d');

const previewFpsEl = document.getElementById('previewFps');
const mouseFpsEl = document.getElementById('mouseFps');
const cmdFpsEl = document.getElementById('cmdFps');
const ageEl = document.getElementById('age');
const renderMsEl = document.getElementById('renderMs');
const draggingEl = document.getElementById('dragging');
const layerEl = document.getElementById('layer');
const wxEl = document.getElementById('wx');
const wzEl = document.getElementById('wz');
const centerBtn = document.getElementById('centerBtn');
const stopBtn = document.getElementById('stopBtn');

let state = null;
let localLayer = null;

let img = new Image();
let hasImage = false;
let previewInFlight = false;
let lastImageSeq = 0;

let dragging = false;
let dragOffsetWorld = {x: 0, z: 0};

let previewTimes = [];
let mouseTimes = [];
let commandTimes = [];

let pendingCommand = null;
let commandSeq = 0;
let lastSentX = null;
let lastSentZ = null;

const STATE_INTERVAL_MS = 45;
const PREVIEW_INTERVAL_MS = 25;
const COMMAND_INTERVAL_MS = 33;

function fitCanvas() {
  const wrap = document.getElementById('stageWrap');
  const maxW = wrap.clientWidth - 32;
  const maxH = wrap.clientHeight - 32;
  const aspect = 16 / 9;
  let w = maxW;
  let h = w / aspect;
  if (h > maxH) { h = maxH; w = h * aspect; }
  canvas.style.width = Math.round(w) + 'px';
  canvas.style.height = Math.round(h) + 'px';
}
window.addEventListener('resize', fitCanvas);
fitCanvas();

function pushTime(list) {
  const now = performance.now();
  list.push(now);
  while (list.length > 60) list.shift();
  if (list.length < 3) return 0;
  const span = list[list.length - 1] - list[0];
  if (span <= 0) return 0;
  return (list.length - 1) / span * 1000;
}

function getLayer() {
  if (localLayer) return localLayer;
  return state && state.layers && state.layers[0] ? state.layers[0] : null;
}

function cloneLayer(layer) {
  return JSON.parse(JSON.stringify(layer));
}

function worldToScreen(x, z) {
  const p = state.preview;
  return {
    x: (x / p.world_width + 0.5) * canvas.width,
    y: (0.5 - z / p.world_height) * canvas.height,
  };
}

function screenToWorld(px, py) {
  const p = state.preview;
  return {
    x: (px / canvas.width - 0.5) * p.world_width,
    z: (0.5 - py / canvas.height) * p.world_height,
  };
}

function layerRect(layer) {
  if (layer.screen_rect) {
    const sr = layer.screen_rect;
    const w = (sr.x2 - sr.x1) * canvas.width;
    const h = (sr.y2 - sr.y1) * canvas.height;

    if (dragging && localLayer && state && state.layers && state.layers[0]) {
      const base = state.layers[0];
      const baseC = worldToScreen(base.x, base.z);
      const localC = worldToScreen(localLayer.x, localLayer.z);
      const dx = localC.x - baseC.x;
      const dy = localC.y - baseC.y;
      return {
        x: sr.x1 * canvas.width + dx,
        y: sr.y1 * canvas.height + dy,
        w: w,
        h: h,
        cx: (sr.cx * canvas.width) + dx,
        cy: (sr.cy * canvas.height) + dy,
      };
    }

    return {
      x: sr.x1 * canvas.width,
      y: sr.y1 * canvas.height,
      w: w,
      h: h,
      cx: sr.cx * canvas.width,
      cy: sr.cy * canvas.height,
    };
  }

  const p = state.preview;
  const c = worldToScreen(layer.x, layer.z);
  const w = layer.width / p.world_width * canvas.width;
  const h = layer.height / p.world_height * canvas.height;
  return {x: c.x - w / 2, y: c.y - h / 2, w, h, cx: c.x, cy: c.y};
}

function hitLayer(px, py) {
  const layer = getLayer();
  if (!state || !layer) return false;
  const r = layerRect(layer);
  return px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h;
}

async function fetchState() {
  try {
    const res = await fetch('/state.json?ts=' + Date.now(), {cache: 'no-store'});
    if (!res.ok) return;
    const nextState = await res.json();
    state = nextState;

    if (!dragging) {
      const layer = state && state.layers && state.layers[0] ? state.layers[0] : null;
      localLayer = layer ? cloneLayer(layer) : null;
    }

    if (state && state.updated_at) {
      const ageMs = Math.max(0, Date.now() - state.updated_at * 1000);
      ageEl.textContent = ageMs.toFixed(0) + ' ms';
      ageEl.className = ageMs < 120 ? 'good' : (ageMs < 300 ? 'warn' : 'bad');
    }

    if (state && state.last_render_ms !== undefined) {
      renderMsEl.textContent = state.last_render_ms.toFixed(1) + ' ms';
    }
  } catch (e) {}
}

function loadPreview() {
  if (previewInFlight) return;
  previewInFlight = true;

  const next = new Image();
  next.onload = () => {
    img = next;
    hasImage = true;
    previewInFlight = false;
    const fps = pushTime(previewTimes);
    if (fps > 0) previewFpsEl.textContent = fps.toFixed(1);
  };
  next.onerror = () => {
    previewInFlight = false;
  };
  next.src = '/preview.jpg?seq=' + (++lastImageSeq) + '&ts=' + Date.now();
}

async function postCommandNow(cmd) {
  try {
    await fetch('/command', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(cmd),
    });
    const fps = pushTime(commandTimes);
    if (fps > 0) cmdFpsEl.textContent = fps.toFixed(1);
  } catch (e) {}
}

function queueLatestCommand(x, z, force = false) {
  lastSentX = x;
  lastSentZ = z;
  pendingCommand = true;

  if (force) {
    flushLatestCommand();
  }
}

function flushLatestCommand() {
  if (!pendingCommand || !localLayer) return;
  commandSeq += 1;
  pendingCommand = false;

  postCommandNow({
    type: 'set_transform',
    layer_id: localLayer.id,
    x: lastSentX,
    z: lastSentZ,
    seq: commandSeq,
    sent_at: Date.now() / 1000
  });
}

setInterval(() => {
  if (dragging && pendingCommand) {
    flushLatestCommand();
  }
}, COMMAND_INTERVAL_MS);

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (hasImage) {
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  } else {
    ctx.fillStyle = '#050506';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#d1d5db';
    ctx.fillText('Waiting for preview.jpg...', 24, 32);
  }

  const layer = getLayer();
  if (state && layer) {
    const r = layerRect(layer);

    ctx.save();

    ctx.strokeStyle = dragging ? '#ffcc33' : '#4ade80';
    ctx.lineWidth = dragging ? 4 : 3;
    ctx.strokeRect(r.x, r.y, r.w, r.h);

    ctx.fillStyle = dragging ? 'rgba(255,204,51,0.10)' : 'rgba(74,222,128,0.10)';
    ctx.fillRect(r.x, r.y, r.w, r.h);

    ctx.fillStyle = '#ffffff';
    ctx.font = '16px system-ui';
    ctx.fillText(layer.name, r.x + 8, r.y - 8);

    ctx.fillStyle = '#ffcc33';
    ctx.beginPath();
    ctx.arc(r.cx, r.cy, 5, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();

    layerEl.textContent = layer.name;
    wxEl.textContent = layer.x.toFixed(3);
    wzEl.textContent = layer.z.toFixed(3);
  }

  draggingEl.textContent = dragging ? 'true' : 'false';
  requestAnimationFrame(draw);
}

function canvasPos(ev) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (ev.clientX - rect.left) / rect.width * canvas.width,
    y: (ev.clientY - rect.top) / rect.height * canvas.height,
  };
}

canvas.addEventListener('pointerdown', (ev) => {
  if (!state) return;
  const p = canvasPos(ev);
  if (!hitLayer(p.x, p.y)) return;

  const layer = getLayer();
  if (!layer) return;

  localLayer = cloneLayer(layer);
  const w = screenToWorld(p.x, p.y);
  dragging = true;
  canvas.classList.add('dragging');
  canvas.setPointerCapture(ev.pointerId);

  dragOffsetWorld.x = localLayer.x - w.x;
  dragOffsetWorld.z = localLayer.z - w.z;

  ev.preventDefault();
});

canvas.addEventListener('pointermove', (ev) => {
  if (!dragging || !state || !localLayer) return;

  const fps = pushTime(mouseTimes);
  if (fps > 0) mouseFpsEl.textContent = fps.toFixed(1);

  const p = canvasPos(ev);
  const w = screenToWorld(p.x, p.y);

  const nx = w.x + dragOffsetWorld.x;
  const nz = w.z + dragOffsetWorld.z;

  localLayer.x = nx;
  localLayer.z = nz;

  queueLatestCommand(nx, nz, false);

  ev.preventDefault();
});

canvas.addEventListener('pointerup', (ev) => {
  if (!dragging) return;
  dragging = false;
  canvas.classList.remove('dragging');
  flushLatestCommand();
  try { canvas.releasePointerCapture(ev.pointerId); } catch (e) {}
});

canvas.addEventListener('pointercancel', (ev) => {
  dragging = false;
  canvas.classList.remove('dragging');
  flushLatestCommand();
  try { canvas.releasePointerCapture(ev.pointerId); } catch (e) {}
});

centerBtn.addEventListener('click', () => {
  const layer = getLayer();
  if (!layer) return;

  localLayer = cloneLayer(layer);
  localLayer.x = 0;
  localLayer.z = 0;

  queueLatestCommand(0, 0, true);
});

stopBtn.addEventListener('click', async () => {
  await fetch('/stop', {method: 'POST'});
});

setInterval(fetchState, STATE_INTERVAL_MS);
setInterval(loadPreview, PREVIEW_INTERVAL_MS);
fetchState();
loadPreview();
draw();
</script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status, content_type, data):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_bytes(200, "text/html; charset=utf-8", HTML.encode("utf-8"))
            return

        if parsed.path == "/preview.jpg":
            try:
                data = PREVIEW_FILE.read_bytes()
                self.send_bytes(200, "image/jpeg", data)
            except FileNotFoundError:
                self.send_bytes(404, "text/plain; charset=utf-8", b"preview not ready")
            except PermissionError:
                self.send_bytes(503, "text/plain; charset=utf-8", b"preview busy")
            return

        if parsed.path == "/state.json":
            try:
                data = STATE_FILE.read_bytes()
                self.send_bytes(200, "application/json; charset=utf-8", data)
            except FileNotFoundError:
                self.send_bytes(404, "application/json; charset=utf-8", b"{}")
            except PermissionError:
                self.send_bytes(503, "application/json; charset=utf-8", b"{}")
            return

        self.send_bytes(404, "text/plain; charset=utf-8", b"not found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/command":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode("utf-8"))
                WORK_DIR.mkdir(parents=True, exist_ok=True)
                tmp = COMMAND_FILE.with_suffix(".tmp")
                tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                os.replace(tmp, COMMAND_FILE)
                self.send_bytes(200, "application/json; charset=utf-8", b"{\"ok\":true}")
            except Exception as exc:
                msg = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
                self.send_bytes(500, "application/json; charset=utf-8", msg)
            return

        if parsed.path == "/stop":
            WORK_DIR.mkdir(parents=True, exist_ok=True)
            STOP_FILE.write_text("stop", encoding="utf-8")
            self.send_bytes(200, "application/json; charset=utf-8", b"{\"ok\":true}")
            return

        self.send_bytes(404, "text/plain; charset=utf-8", b"not found")

    def log_message(self, fmt, *args):
        return

def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    print(f"C1 Drag UI server v3: http://{HOST}:{PORT}")
    print(f"Work dir: {WORK_DIR}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

if __name__ == "__main__":
    main()
