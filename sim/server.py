"""UNIVERSE 69 — runtime.

- Ticks both universes, anchored to the wall clock: day N always corresponds to
  epoch + N * sec_per_day. If the laptop sleeps or the process dies, the engine
  fast-forwards the missed days on the next start (Tamagotchi semantics).
- Serves the pixel viewer + JSON state on http://localhost:6969
- Appends notable events to data/events.ndjson
- Optionally mirrors a snapshot to the web (data/web.json: {"url", "token"}).

Run:  python3 sim/server.py
"""

import json
import os
import signal
import sys
import threading
import time
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
WEB = os.path.join(ROOT, "web")
STATE_PATH = os.path.join(DATA, "state.json")
EVENTS_PATH = os.path.join(DATA, "events.ndjson")
WEBCFG_PATH = os.path.join(DATA, "web.json")
PORT = 6969

os.makedirs(DATA, exist_ok=True)

lock = threading.Lock()
recent_events = deque(maxlen=120)
status = {"catching_up": False, "behind_days": 0, "started": time.time()}

if os.path.exists(STATE_PATH):
    world = engine.load_state(STATE_PATH)
    print(f"[universe69] resumed state at day {world['eden']['day']}")
else:
    world = engine.genesis(seed=69)
    print("[universe69] GENESIS — two universes created")

# preload the tail of the event log so the ticker survives restarts
if os.path.exists(EVENTS_PATH):
    with open(EVENTS_PATH) as f:
        for line in f.readlines()[-120:]:
            try:
                recent_events.append(json.loads(line))
            except ValueError:
                pass


def log_events(evts):
    if not evts:
        return
    with open(EVENTS_PATH, "a") as f:
        for (day, uni, kind, msg) in evts:
            rec = {"d": day, "y": day // engine.DAYS_PER_YEAR, "u": uni,
                   "t": kind, "msg": msg, "wall": time.time()}
            recent_events.append(rec)
            f.write(json.dumps(rec) + "\n")


def target_day():
    return int((time.time() - world["epoch"]) / world["sec_per_day"])


def engine_loop():
    last_save = time.time()
    while True:
        behind = target_day() - world["eden"]["day"]
        status["behind_days"] = max(0, behind)
        status["catching_up"] = behind > 60
        if behind > 0:
            batch = min(behind, 8000)
            evts = []
            with lock:
                for _ in range(batch):
                    engine.tick_world(world, evts)
            log_events(evts)
            if status["catching_up"]:
                print(f"[universe69] fast-forwarding, {behind - batch} days to go")
        if time.time() - last_save > 60:
            with lock:
                engine.save_state(world, STATE_PATH)
            last_save = time.time()
        time.sleep(0.2 if behind > 1 else 0.5)


def uploader_loop():
    """Mirror the latest snapshot to the web. Best-effort, never kills the sim.

    data/web.json selects the mode:
      {"mode": "gist", "gist_id": "...", "interval": 600}   -> gh api PATCH
      {"mode": "put", "url": "...", "token": "...", "interval": 120}
    """
    import subprocess
    while True:
        interval = 600
        try:
            if os.path.exists(WEBCFG_PATH):
                with open(WEBCFG_PATH) as f:
                    cfg = json.load(f)
                interval = int(cfg.get("interval", 600))
                with lock:
                    snap = engine.summarize(world)
                snap["events"] = list(recent_events)[-60:]
                snap["world"] = world_payload()
                body = json.dumps(snap, separators=(",", ":"))
                if cfg.get("mode") == "gist":
                    patch = json.dumps(
                        {"files": {"snapshot.json": {"content": body}}})
                    subprocess.run(
                        ["gh", "api", "gists/" + cfg["gist_id"],
                         "-X", "PATCH", "--input", "-"],
                        input=patch.encode(), capture_output=True,
                        timeout=60, check=True)
                elif cfg.get("mode") == "put":
                    req = urllib.request.Request(cfg["url"],
                                                 data=body.encode(),
                                                 method="PUT")
                    req.add_header("authorization", "Bearer " + cfg["token"])
                    req.add_header("content-type", "application/json")
                    urllib.request.urlopen(req, timeout=20)
                status["last_upload"] = time.time()
                status.pop("upload_error", None)
        except Exception as e:
            status["upload_error"] = str(e)[:200]
        time.sleep(interval)


def world_payload():
    lag = world["lagoon"]
    terrain = (engine.make_lagoon_terrain(lag.get("terrain_seed", lag["seed"]))
               if lag["kind"] == "LAGOON" else None)
    return {"eden_size": engine.EDEN_SIZE, "lagoon_size": engine.LAGOON_SIZE,
            "lagoon_iter": lag["iteration"], "terrain": terrain}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(data)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/" or path == "/index.html":
            with open(os.path.join(WEB, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif path == "/config.js":
            self._send(200, "// local mode\n", "text/javascript")
        elif path == "/state":
            with lock:
                snap = engine.summarize(world)
            snap["events"] = list(recent_events)[-60:]
            snap["status"] = status
            self._send(200, json.dumps(snap, separators=(",", ":")))
        elif path == "/world":
            with lock:
                payload = world_payload()
            self._send(200, json.dumps(payload, separators=(",", ":")))
        else:
            self._send(404, '{"err":"not found"}')

    def log_message(self, *a):
        pass


def shutdown(*_):
    with lock:
        engine.save_state(world, STATE_PATH)
    print("[universe69] state saved, goodbye")
    os._exit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

threading.Thread(target=engine_loop, daemon=True).start()
threading.Thread(target=uploader_loop, daemon=True).start()

print(f"[universe69] observing on http://localhost:{PORT}")
ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
