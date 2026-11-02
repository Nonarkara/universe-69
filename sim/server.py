"""UNIVERSE 69 — runtime.

- Ticks both universes by quarter-days, anchored to a persistent wall clock.
  If the laptop sleeps or the process dies, the engine catches up on restart.
- Serves the pixel viewer + JSON state on http://localhost:6969
- Appends notable events to data/events.ndjson
- Optionally mirrors a snapshot to the web (data/web.json: {"url", "token"}).

Run:  python3 sim/server.py
      python3 sim/server.py --genesis   # archive the old world, start over
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
import research
import historian

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The live run keeps its state in ./data. A development instance can be pointed
# somewhere else with UNIVERSE69_DATA so it can never touch the live world.
DATA = os.environ.get("UNIVERSE69_DATA") or os.path.join(ROOT, "data")
WEB = os.path.join(ROOT, "web")
STATE_PATH = os.path.join(DATA, "state.json")
EVENTS_PATH = os.path.join(DATA, "events.ndjson")
WEBCFG_PATH = os.path.join(DATA, "web.json")
PORT = int(os.environ.get("UNIVERSE69_PORT", "6969"))
# How long one part of a day takes in real seconds. A day is four parts, so
# this sets how fast the year goes by: default 100 model years of 360 days
# per real day, retaining dawn/day/dusk/night as separate ticks.
SEC_PER_PART = float(os.environ.get("UNIVERSE69_SEC_PER_PART", engine.SEC_PER_PART))
# Real-Time: a day actually takes a day. Dawn, day, dusk and night each take
# a real six hours, so the people move at the pace they would move at if you
# were standing there — nothing sped up to make it watchable. That is the
# point: the default pace is the one that needs the apology, not this one.
REALTIME_SEC_PER_PART = 6.0 * 3600.0
EVENTS_IN_VIEW = 500          # how much of the record the console is given

os.makedirs(DATA, exist_ok=True)

lock = threading.Lock()
recent_events = deque(maxlen=4000)
status = {"catching_up": False, "behind_days": 0, "started": time.time(),
          "time_mode": "default"}

# `--genesis` starts both worlds over from the shared founders. The old world
# is archived, never deleted: its numbers belong to the engine that made them.
# A fresh start is the Nth attempt, derived from the archive, and LAGOON
# inherits the lessons the dead iterations hold — EDEN never does, because
# each of its runs must repeat the fatal conditions innocent (the asymmetry
# is the experiment).
attempt = 1
if "--genesis" in sys.argv:
    archived = historian.archive_run(DATA)
    if archived:
        print(f"[universe69] archived the old run to {archived}")
    attempt = historian.count_runs(DATA) + 1
    print(f"[universe69] fresh start — attempt {attempt}")

if os.path.exists(STATE_PATH):
    try:
        world = engine.load_state(STATE_PATH)
        print(f"[universe69] resumed state at day {world['eden']['day']}")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        # A corrupt state must never kill the service: archive what was
        # there and start again. The old file is kept, never destroyed.
        stamp = time.strftime("%Y%m%d-%H%M%S")
        bad = STATE_PATH + f".corrupt-{stamp}"
        try:
            os.replace(STATE_PATH, bad)
            print(f"[universe69] state.json unreadable ({exc}); archived to {bad}")
        except OSError:
            print(f"[universe69] state.json unreadable ({exc})")
        world = engine.genesis(seed=69, attempt=attempt)
        print("[universe69] GENESIS — two universes created")
else:
    world = engine.genesis(seed=69, attempt=attempt)
    print(f"[universe69] GENESIS — two universes created (attempt {attempt})")
    if attempt > 1:
        lessons = historian.lessons_from_archive(archived) if archived else []
        if lessons:
            world["lagoon"]["lessons"] = lessons
            print(f"[universe69] LAGOON carries the dead attempts' lessons: "
                  f"{', '.join(lessons)}")

engine.set_clock_pace(world, SEC_PER_PART)

# preload the tail of the event log so the ticker survives restarts.
# A hard kill replays the days since the last save; those lines are already
# in the file, so remember them and do not write them twice.
seen_events = set()
if os.path.exists(EVENTS_PATH):
    with open(EVENTS_PATH) as f:
        tail = list(deque(f, maxlen=4000))
    parsed = []
    for line in tail:
        try:
            parsed.append(json.loads(line))
        except ValueError:
            pass
    for rec in parsed:
        seen_events.add((rec.get("d"), rec.get("u"), rec.get("msg")))
    for rec in parsed[-EVENTS_IN_VIEW:]:
        recent_events.append(rec)


def log_events(evts):
    if not evts:
        return
    with open(EVENTS_PATH, "a") as f:
        for (day, uni, kind, msg) in evts:
            key = (day, uni, kind, msg)
            if key in seen_events:
                continue
            seen_events.add(key)
            rec = {"d": day, "y": day // engine.DAYS_PER_YEAR, "u": uni,
                   "t": kind, "msg": msg, "wall": time.time()}
            recent_events.append(rec)
            f.write(json.dumps(rec) + "\n")


def target_part():
    """How many parts of the day the wall clock says we should be at.

    The world advances one part per tick, so this is the clock the engine
    is caught up to, not the calendar day."""
    return engine.target_parts(world)


def dump_postmortems():
    """Write any new postmortems to data/postmortems/ for the record."""
    pmdir = os.path.join(DATA, "postmortems")
    os.makedirs(pmdir, exist_ok=True)
    with lock:
        for key in ("eden", "lagoon"):
            u = world[key]
            for pm in u.get("postmortems", []):
                path = os.path.join(
                    pmdir, f"u{'6' if key == 'eden' else '9'}-iteration-{pm['iteration']:03d}.json")
                if not os.path.exists(path):
                    pending = path + ".tmp"
                    try:
                        with open(pending, "w") as f:
                            json.dump(pm, f, indent=2)
                        os.replace(pending, path)
                    finally:
                        if os.path.exists(pending):
                            os.unlink(pending)


def update_histories():
    """Keep observer I/O failures outside the simulation's failure boundary."""
    global observations
    try:
        dump_postmortems()
        with lock:
            observations = historian.observe(world, DATA, observations)
            historian.compile_book(world, data=DATA)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        with lock:
            observations = dict(observations, error='History unavailable: ' + str(exc))


def engine_loop():
    last_save = time.time()
    last_test = world.get("research", {}).get("last_day", -research.CADENCE) // research.CADENCE
    while True:
        target = target_part()
        behind = target - max(world["eden"].get("parts", 0), world["lagoon"].get("parts", 0))
        status["behind_days"] = max(0, behind) // engine.PARTS_PER_DAY
        status["catching_up"] = behind > 60 * engine.PARTS_PER_DAY
        if behind > 0:
            # A batch is how long the viewer's lock is held at a stretch.
            # 8000 parts (2000 days) froze the page for over a minute on the
            # 2016 MacBook; 2000 parts (500 days) keeps each freeze under
            # ten seconds. The tick sequence is identical either way.
            batch = min(behind, 2000)
            evts = []
            with lock:
                for _ in range(batch):
                    engine.tick_world(world, evts)
                    # Record at the same calendar boundaries during catch-up
                    # and normal operation, including across process restarts.
                    day = world["eden"]["day"]
                    if day // research.CADENCE > last_test:
                        last_test = day // research.CADENCE
                        research.record(world, research.evaluate(world))
            log_events(evts)
            if any(e[2] in ("extinction", "lesson") for e in evts):
                update_histories()
            if status["catching_up"]:
                print(f"[universe69] fast-forwarding, {behind - batch} parts to go")
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
                snap = snapshot(with_world=True)
                body = json.dumps(snap, separators=(",", ":"))
                if cfg.get("mode") == "gist":
                    gh = next((g for g in ("/usr/local/bin/gh",
                                           "/opt/homebrew/bin/gh", "gh")
                               if g == "gh" or os.path.exists(g)))
                    patch = json.dumps(
                        {"files": {"snapshot.json": {"content": body}}})
                    subprocess.run(
                        [gh, "api", "gists/" + cfg["gist_id"],
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
    terrain = (engine.terrain_of(lag)
               if lag["kind"] == "LAGOON" else None)
    return {"eden_size": engine.EDEN_SIZE, "lagoon_size": engine.LAGOON_SIZE,
            "lagoon_iter": lag["iteration"], "terrain": terrain}


def snapshot(with_world=False):
    """The whole payload the viewer and the web mirror read.

    One place, so the local page and the published page can never disagree
    about what the record says. The terrain map is big, so it is only
    carried for the mirror, which has no other way to fetch it.
    """
    with lock:
        snap = engine.summarize(world)
        snap["events"] = list(recent_events)[-EVENTS_IN_VIEW:]
        snap["status"] = dict(status)
        snap["research"] = research.report(world)
        snap["observations"] = observations
        if with_world:
            snap["world"] = world_payload()
    return snap


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(data)))
        self.send_header("access-control-allow-origin", "*")
        self.send_header("cache-control", "no-cache, no-store, must-revalidate")
        self.send_header("pragma", "no-cache")
        self.send_header("expires", "0")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/" or path == "/index.html":
            with open(os.path.join(WEB, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif path == "/vr.html":
            with open(os.path.join(WEB, "vr.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif path == "/three.module.min.js":
            with open(os.path.join(WEB, "three.module.min.js"), "rb") as f:
                self._send(200, f.read(), "text/javascript; charset=utf-8")
        elif path == "/config.js":
            self._send(200, "// local mode\n", "text/javascript")
        elif path == "/state":
            self._send(200, json.dumps(snapshot(), separators=(",", ":")))
        elif path == "/world":
            with lock:
                payload = world_payload()
            self._send(200, json.dumps(payload, separators=(",", ":")))
        elif path == "/research":
            with lock:
                payload = research.report(world)
            self._send(200, json.dumps(payload, separators=(",", ":")))
        elif path.startswith(("/book/", "/archive/", "/fonts/")):
            # Read-only assets, confined to their real static directory.
            top = path.split("/", 2)[1]
            base = os.path.realpath(os.path.join(WEB, top))
            target = os.path.realpath(os.path.join(base, path[len(top) + 2:]))
            kinds = {".json": "application/json", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                     ".png": "image/png", ".svg": "image/svg+xml", ".html": "text/html; charset=utf-8",
                     ".md": "text/plain; charset=utf-8"}
            if top == "fonts":
                kinds = {".woff2": "font/woff2", ".txt": "text/plain; charset=utf-8"}
            kind = kinds.get(os.path.splitext(target)[1].lower())
            if kind and target.startswith(base + os.sep) and os.path.isfile(target):
                with open(target, "rb") as f:
                    self._send(200, f.read(), kind)
            else:
                self._send(404, '{"err":"not found"}')
        else:
            self._send(404, '{"err":"not found"}')

    def do_POST(self):
        path = self.path.split("?")[0]
        if path != "/pace":
            self._send(404, '{"err":"not found"}')
            return
        length = int(self.headers.get("content-length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except ValueError:
            self._send(400, '{"err":"bad json"}')
            return
        mode = body.get("mode")
        if mode not in ("default", "realtime"):
            self._send(400, '{"err":"mode must be default or realtime"}')
            return
        seconds = REALTIME_SEC_PER_PART if mode == "realtime" else SEC_PER_PART
        with lock:
            engine.set_clock_pace(world, seconds)
            status["time_mode"] = mode
        print(f"[universe69] time mode -> {mode} ({seconds}s/part)")
        self._send(200, json.dumps(snapshot(), separators=(",", ":")))

    def log_message(self, *a):
        pass


def shutdown(*_):
    with lock:
        engine.save_state(world, STATE_PATH)
    print("[universe69] state saved, goodbye")
    os._exit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# If the run was already over when we booted, make sure the book exists.
observations = {"schema": 1, "records": []}
update_histories()

threading.Thread(target=engine_loop, daemon=True).start()
threading.Thread(target=uploader_loop, daemon=True).start()

print(f"[universe69] observing on http://localhost:{PORT}")
ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
