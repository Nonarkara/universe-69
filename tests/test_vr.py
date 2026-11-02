"""The VR viewer: the same record, two worlds, two clocks.

`web/vr.html` is the Meta Quest build. It is deliberately not a game and not
a second simulation: it reads the same `/state` snapshot as the 2D viewer
(or the published gist), draws both worlds from the record's own terrain,
settlements and people, and adds a viewing clock on top.

The clock is the part easiest to get wrong. TIMELAPSE is the record's own
hundred-years-a-day pace, with people shown moving briskly the way a
timelapse shows them. REAL-TIME holds the record and plays the held moment at
human speed; CONTINUE applies the newest snapshot. It never writes to the
server and never touches `/pace`.

These pins are static on purpose: the test suite must stay standard-library
only and must not need a headset, a browser, or Playwright.
"""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DOCS = os.path.join(ROOT, "docs")
VR = os.path.join(WEB, "vr.html")
VR_MIRROR = os.path.join(DOCS, "vr.html")
THREE = os.path.join(WEB, "three.module.min.js")
THREE_MIRROR = os.path.join(DOCS, "three.module.min.js")
SERVER = os.path.join(ROOT, "sim", "server.py")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestTheVRViewerIsSelfContained(unittest.TestCase):
    """It ships from the repository. No CDN, no bundler, no build step."""

    def test_the_docs_mirror_is_identical(self):
        self.assertEqual(read(VR), read(VR_MIRROR),
                         "web/vr.html and docs/vr.html have diverged")

    def test_three_is_vendored_in_both_places(self):
        self.assertTrue(os.path.exists(THREE), "the vendored three.js build is missing")
        self.assertEqual(read(THREE), read(THREE_MIRROR),
                         "web/three.module.min.js and docs/three.module.min.js have diverged")

    def test_three_is_the_pinned_revision(self):
        src = read(THREE)
        self.assertIn("SPDX-License-Identifier: MIT", src[:400])
        self.assertRegex(src, r'\bconst t="160"',
                         "the vendored three.js is no longer r160; update this pin on purpose")

    def test_assets_are_all_local(self):
        src = read(VR)
        for attr, value in re.findall(r'<(?:script|link)\b[^>]*?\b(src|href)="([^"]+)"', src):
            self.assertFalse(value.startswith(("http://", "https://", "//")),
                             f"the VR page loads an external asset: {attr}={value}")
        self.assertIn("from './three.module.min.js'", src)
        for cdn in ("unpkg.com", "cdn.jsdelivr.net", "threejs.org", "esm.sh"):
            self.assertNotIn(cdn, src)

    def test_the_only_network_reads_are_the_record(self):
        src = read(VR)
        self.assertIn("getJSON(SNAP)", src)
        self.assertIn("getJSON(\"/state\")", src)
        self.assertIn("getJSON(\"/world\")", src)
        self.assertNotIn("\"POST\"", src)
        self.assertNotIn("/pace", src)


class TestTheVRViewerIsWebXR(unittest.TestCase):
    """It has to enter a real immersive session on a Quest, not just fullscreen."""

    def test_an_immersive_session_can_be_requested(self):
        src = read(VR)
        self.assertIn("renderer.xr.enabled = true", src)
        self.assertRegex(src, r'navigator\.xr\.requestSession\(\s*"immersive-vr"')
        self.assertRegex(src, r'isSessionSupported\(\s*"immersive-vr"\s*\)')
        self.assertIn('setReferenceSpaceType("local-floor")', src)

    def test_the_session_loop_is_the_xr_loop(self):
        src = read(VR)
        self.assertIn("renderer.setAnimationLoop(frame)", src)
        self.assertNotIn("requestAnimationFrame(frame)", src)

    def test_controllers_teleport_and_turn(self):
        src = read(VR)
        self.assertIn("renderer.xr.getController(i)", src)
        self.assertIn('addEventListener("selectstart"', src)
        self.assertIn("function teleportFrom(", src)
        self.assertIn("function xrInput(", src)
        self.assertIn("gamepad", src)

    def test_the_slate_is_drawn_in_the_headset(self):
        src = read(VR)
        self.assertIn("function makeSlate(", src)
        self.assertIn("camera.add(mesh)", src)
        self.assertIn("slate.mesh.visible = renderer.xr.isPresenting", src,
                      "the in-headset slate is created but never shown")


class TestTheTwoClocks(unittest.TestCase):
    """TIMELAPSE is the record's pace; REAL-TIME holds one moment for you."""

    def test_timelapse_is_the_default(self):
        src = read(VR)
        self.assertRegex(src, r"const held = \{\s*on: false")
        self.assertIn("TIMELAPSE", src)
        self.assertIn("REAL-TIME", src)
        self.assertIn("CONTINUE", src)

    def test_the_pace_is_read_from_the_record_not_hardcoded(self):
        src = read(VR)
        self.assertIn("years_per_real_day", src)
        self.assertIn("YEARS / REAL DAY", src)

    def test_real_time_holds_the_applied_state(self):
        src = read(VR)
        poll = src[src.index("async function poll("):src.index("function showError(")]
        self.assertIn("if (held.on)", poll)
        self.assertIn("pendingState = st", poll)
        self.assertIn("updateHUD()", poll)

    def test_polling_continues_while_the_clock_is_held(self):
        src = read(VR)
        frame = src[src.index("function frame("):src.index("function applyQueryMode(")]
        self.assertIn("if (ready) poll(false);", frame,
                      "the held viewer must keep looking for the newest moment")
        self.assertNotIn("!held.on) poll(false)", frame)

    def test_continue_applies_the_newest_snapshot(self):
        src = read(VR)
        head = src[src.index("function setHeld("):src.index("// ---- input:")]
        self.assertIn("if (pendingState)", head)
        self.assertIn("state = pendingState", head)
        self.assertIn("pendingState = null", head)
        self.assertIn("poll(true)", head)

    def test_people_move_faster_in_timelapse_than_in_real_time(self):
        src = read(VR)
        timelapse = float(re.search(r"Math\.max\((\d+(?:\.\d+)?), size \* 0\.07\)", src).group(1))
        held = float(re.search(r"Math\.min\(d, (\d+(?:\.\d+)?) \* dt\)", src).group(1))
        self.assertGreaterEqual(timelapse / held, 6.0,
                                "the timelapse crowd is not visibly faster than real time")

    def test_the_busy_timelapse_roams_between_record_snapshots(self):
        src = read(VR)
        self.assertIn("a busy year: even while the record has them at a spot", src)
        self.assertIn("const roam =", src)


class TestTheTerrariumPalette(unittest.TestCase):
    """The VR page keeps the house palette; it is the same terrarium, lit."""

    TOKENS = {
        "--surface": "#14130f", "--surface-2": "#1c1a15", "--ink": "#ede6d6",
        "--muted": "#a39b88", "--dim": "#8a8372", "--line": "#37332a",
        "--accent": "#e4b456", "--eden": "#8ec5d6", "--lagoon": "#a6c98a",
        "--warn": "#ec8f74",
    }

    def test_the_console_tokens_are_here(self):
        src = read(VR)
        root = re.search(r":root\s*\{(.*?)\n  \}", src, re.S)
        self.assertIsNotNone(root, "the VR page has no :root palette")
        for name, value in self.TOKENS.items():
            self.assertRegex(root.group(1), re.escape(f"{name}:") + r"\s*" + re.escape(value))

    def test_it_is_a_lit_terrarium_not_a_flat_canvas(self):
        src = read(VR)
        self.assertIn("ACESFilmicToneMapping", src)
        self.assertIn("PCFSoftShadowMap", src)
        self.assertIn("renderer.shadowMap.enabled = true", src)
        self.assertIn("setPixelRatio", src)
        self.assertIn("EDEN_TABLE", src)
        self.assertIn("LAGOON_TABLE", src)

    def test_both_worlds_are_on_the_first_table(self):
        src = read(VR)
        self.assertRegex(src, r"TABLE_X = \{\s*eden: -0\.99, lagoon: 1\.02")
        self.assertIn("buildEdenInto", src)
        self.assertIn("buildLagoonInto", src)

    def test_amenities_follow_the_model(self):
        src = read(VR)
        for f in ("pool", "bar", "theater", "field"):
            self.assertIn(f"f.{f} > 0", src)
        self.assertIn("buildPool", src)
        self.assertIn("buildBar", src)
        self.assertIn("buildTheater", src)
        self.assertIn("buildField", src)


class TestTheServerServesVR(unittest.TestCase):
    def test_the_routes_exist(self):
        src = read(SERVER)
        self.assertIn('path == "/vr.html"', src)
        self.assertIn('path == "/three.module.min.js"', src)
        self.assertIn('os.path.join(WEB, "vr.html")', src)
        self.assertIn('os.path.join(WEB, "three.module.min.js")', src)

    def test_the_page_is_served_as_html_and_the_library_as_javascript(self):
        src = read(SERVER)
        for path, mime in (("/vr.html", "text/html"), ("/three.module.min.js", "text/javascript")):
            block = src[src.index(f'path == "{path}"'):]
            block = block[:block.index("elif") if "elif" in block else len(block)]
            self.assertIn(mime, block)


if __name__ == "__main__":
    unittest.main()
