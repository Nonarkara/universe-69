"""The VR viewer: the same record, two worlds, two clocks.

`web/vr.html` is the Meta Quest build. It is deliberately not a game and not
a second simulation: it reads the same `/state` snapshot as the 2D viewer
(or the published gist), draws both worlds from the record's own terrain,
settlements and people, and adds a viewing clock on top.

The clock is the part easiest to get wrong. TIMELAPSE is the record's own
reported pace, joining only observed coordinates along a dry straight
segment. REAL-TIME holds recorded coordinates and actions; CONTINUE applies
the newest snapshot. Unsupported routes snap to the recorded endpoint. It never writes to the
server and never touches `/pace`.

The core suite remains standard-library only, without a browser or headset.
Optional Node checks execute the actual pure JS helpers on the workbench.
"""

import os
import re
import shutil
import subprocess
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

    def test_vendored_fonts_have_mirrors_and_licenses(self):
        for name in ('Jost-latin-variable.woff2','SourceSerif4-latin-normal-variable.woff2',
                     'SourceSerif4-latin-italic-variable.woff2'):
            with open(os.path.join(WEB,'fonts',name),'rb') as f: font=f.read()
            with open(os.path.join(DOCS,'fonts',name),'rb') as f: mirror=f.read()
            self.assertEqual(font[:4],b'wOF2')
            self.assertEqual(font,mirror)
        for name in ('Jost-OFL.txt','SourceSerif4-OFL.txt'):
            self.assertIn('SIL OPEN FONT LICENSE',read(os.path.join(WEB,'fonts',name)))
            self.assertEqual(read(os.path.join(WEB,'fonts',name)),read(os.path.join(DOCS,'fonts',name)))
        self.assertIn('src:url("fonts/Jost-latin-variable.woff2")',read(VR))


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
        self.assertIn("YEARS / REAL HOUR", src)

    def test_representative_light_does_not_flash_each_model_day(self):
        src=read(VR)
        function=src[src.index('function displayTime('):src.index('function lightPreset(')]
        script=function+"""
const assert=require('node:assert/strict');
for(let d=0;d<360;d++){
 assert.equal(displayTime({day:d,part:0,tod:'night'},false),
   ['dawn','day','dusk','night'][Math.floor(((d%90)/90+.125)%1*4)]);
 assert.equal(displayTime({day:d,tod:'night'},true),'night');
}
assert.equal(displayTime({day:22,part:1},false),'day');
assert.equal(displayTime({day:22,part:2},false),'day');
"""
        if shutil.which('node'):
            result=subprocess.run([shutil.which('node')],input=script,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('smooth(phase-Math.floor(phase))',src)
        self.assertNotIn('tod === "night" || (u && u.night)',src)

    def test_connected_anatomy_and_face_are_instanced(self):
        src=read(VR)
        self.assertIn('this.torso = inst(torsoGeometry(), cap)',src)
        self.assertIn('this.head = inst(skullGeometry(), cap)',src)
        self.assertIn('this.face.count = c.nface',src)
        self.assertIn('this.feet = inst(new THREE.SphereGeometry(0.5, 12, 8), cap * 8)',src)
        self.assertNotIn('lamps.visible = !!u.night',src)
        self.assertNotIn('lamps.visible = !!(state && state.u.eden.night)',src)
        self.assertIn('Math.PI*2, 0, 1.25',src)
        self.assertIn('inst(limbGeometry(), cap * 4)',src)
        self.assertIn('limbR*3.0*big',src)
        self.assertIn('new THREE.Vector3(1, 0, 0), -Math.PI / 2);',src)
        self.assertIn('if (mode.view === "inside")',src)

    def test_real_time_holds_the_applied_state(self):
        src = read(VR)
        poll = src[src.index("async function poll("):src.index("function showError(")]
        self.assertIn("if (held.on)", poll)
        self.assertIn("heldRecordUpdate(state, worldInfo", poll)
        self.assertIn("pendingState = next.pending", poll)
        self.assertNotIn("newer moment", src)
        self.assertIn("an updated record is available", src)
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

    def test_motion_only_joins_recorded_endpoints_on_dry_land(self):
        src = read(VR)
        self.assertIn('function canInterpolateRecord(', src)
        self.assertIn('function recordedStep(', src)
        update = src[src.index('  update(dt, t, heldOn)'):src.index('  drawBody(')]
        self.assertIn('recordedStep(this.key, a, dt, heldOn', update)
        self.assertNotIn('a.act =', update)
        self.assertNotIn('const roam', src)
        self.assertNotIn('nearestAnchor(', src)

    def test_held_positions_are_the_record_not_a_new_walk(self):
        src = read(VR)
        step = src[src.index('function recordedStep('):src.index('function bodyLandmarks(')]
        self.assertIn('if (heldOn || !locomotion ||', step)
        self.assertIn('a.px = a.x; a.py = a.y', step)
        self.assertNotRegex(step, r'a\.act\s*=(?!=)')
        self.assertIn('terrain[y][x] !== 2', src)

    def test_age_tables_match_the_canonical_2d_rig(self):
        import ast
        src=read(VR); canonical=read(os.path.join(WEB,'index.html'))
        for name in ('STATURE','AGE_BAND','HEADS','LEG_FRAC','ARM_FRAC','SH_FRAC','HP_FRAC'):
            pattern=r'\b'+name+r'\s*=\s*(\[[^]]+\])'
            self.assertEqual(ast.literal_eval(re.search(pattern,src).group(1)),
                             ast.literal_eval(re.search(pattern,canonical).group(1)))

    def test_sitting_and_lying_landmarks_scale_with_body_height(self):
        src = read(VR)
        landmarks = src[src.index('function bodyLandmarks('):src.index('const _m =')]
        self.assertIn('const hipY = lying ? 0 : sitting ? D.shin', landmarks)
        self.assertIn('const torso = D.shY - D.hipY', landmarks)
        body = src[src.index('  drawBody('):src.index('function seg(')]
        self.assertIn('bodyLandmarks(D, lying, sitting)', body)
        self.assertIn('bodyRadii(D, fat, strong)', body)
        self.assertIn('lyingSupport(headR, torsoR, limbR) * big', body)
        self.assertNotIn('P(0, 0.62', body)
        self.assertNotIn('ey = 0.50', body)
        self.assertIn('a.moving', body)
    def test_compact_context_and_record_pager_preserve_details(self):
        src = read(VR)
        self.assertIn('id="bRecord" aria-expanded="false"',src)
        self.assertIn('worldLines(key, u).slice(1)',src)
        self.assertIn('aria-label="Previous record page"',src)
        self.assertIn('aria-label="Next record page"',src)
        self.assertIn('target.focus({preventScroll:true})',src)
        self.assertIn('summary(key, u)',src)
        self.assertIn('RECORD HELD',src)
        self.assertIn('age unknown',src)


@unittest.skipUnless(shutil.which('node'), 'optional workbench JS execution requires Node; source contracts still run')
class TestRecordedMotionAndGeometry(unittest.TestCase):
    def test_actual_javascript_record_motion_and_scaled_landmarks(self):
        src = read(VR)
        helpers = src[src.index('const STATURE ='):src.index('const _m =')]
        script = helpers + r"""
const assert = require('node:assert/strict');
const dry = Array.from({length:8},()=>Array(8).fill(0));
const sea = dry.map(r=>r.slice()); sea[2][2]=2;
assert.equal(canInterpolateRecord(dry,1,1,5,5),true);
assert.equal(canInterpolateRecord(sea,1,1,5,5),false);
const corner = dry.map(r=>r.slice());corner[1][2]=2;
assert.equal(canInterpolateRecord(corner,1,1,2,2),false);
assert.equal(canInterpolateRecord(dry,-1,1,2,2),false);
assert.equal(canInterpolateRecord(null,1,1,2,2),false);
for (const act of [1,4,8,9,10,11,12,17,18,22]) {
  const a={id:7,x:5,y:5,px:1,py:1,act,face:-1};
  recordedStep('lagoon',a,.5,true,dry);
  assert.deepEqual([a.px,a.py,a.act,a.moving],[5,5,act,false]);
  for(let i=0;i<100;i++)recordedStep('lagoon',a,.1,false,dry);
  assert.deepEqual([a.px,a.py,a.act,a.moving],[5,5,act,false]);
}
for(const act of [4,8,9,10,11,12,17,18,22]) {
 const stationary={x:5,y:5,px:1,py:1,act};
 recordedStep('lagoon',stationary,.1,false,dry);
 assert.deepEqual([stationary.px,stationary.py,stationary.act,stationary.moving],[5,5,act,false]);
}
const travel={x:5,y:5,px:1,py:1,act:1};
recordedStep('lagoon',travel,.1,false,dry);
assert(travel.px>1&&travel.px<5);assert.equal(travel.act,1);
const blocked={x:5,y:5,px:1,py:1,act:22};
recordedStep('lagoon',blocked,.1,false,sea);
assert.deepEqual([blocked.px,blocked.py,blocked.act,blocked.moving],[5,5,22,false]);
for (const age of [0,1,2,4,7,10,13,16,25,70]) for(const sex of [0,1]) {
 const D=bodyDimensions(age,sex), i=ageBand(age);
 assert(Math.abs(D.headR*2.12-D.H/HEADS[i])<1e-12);
 assert(Math.abs(D.upper+D.fore-ARM_FRAC[i]*D.H)<1e-12);
 assert(Math.abs(D.thigh+D.shin-(LEG_FRAC[i]-1.1/32)*D.H)<1e-12);
 if(age<12) {
  const other=bodyDimensions(age,1-sex);
  assert.equal(D.H,other.H);assert.equal(D.shHalf,other.shHalf);assert.equal(D.hipHalf,other.hipHalf);
  assert.equal(bodyRadii(D,1,1).torsoR,bodyRadii(other,1,1).torsoR);
 }
 for(const [lying,sitting] of [[true,false],[false,true],[false,false]]) {
  const pose=bodyLandmarks(D,lying,sitting);
  assert(Math.abs(pose.shY-pose.hipY-(D.shY-D.hipY))<1e-12);
  const root={x:0,y:pose.hipY,z:0}, hint={x:0,y:pose.ky,z:pose.kz}, end={x:0,y:pose.ay,z:pose.az};
  const chain=limbChain(root,hint,end,D.thigh,D.shin);
  const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
  assert(Math.abs(distance(root,chain.middle)-D.thigh)<1e-12);
  assert(Math.abs(distance(chain.middle,chain.end)-D.shin)<1e-12);
  const shoulder={x:D.shHalf,y:pose.shY,z:0};
  const arm=limbChain(shoulder,{x:D.shHalf,y:pose.shY-.2*D.H,z:.1*D.H},
    {x:D.shHalf,y:pose.shY-.4*D.H,z:.15*D.H},D.upper,D.fore);
  assert(Math.abs(distance(shoulder,arm.middle)-D.upper)<1e-12);
  assert(Math.abs(distance(arm.middle,arm.end)-D.fore)<1e-12);
 }
}
for (const age of [0,1,2,4,7,10,13,16,25,70]) for(const sex of [0,1]) {
 const D=bodyDimensions(age,sex);
 for(const fat of [.78,1,1.55]) for(const strong of [.2,1]) {
  const {torsoR,limbR,headR}=bodyRadii(D,fat,strong);
  const lift=lyingSupport(headR,torsoR,limbR);
  for(const low of [lift-headR,lift-torsoR,lift-1.5*limbR,lift-1.10*limbR,
    lift+.18*headR-1.03*headR,lift+.006*D.H-.95*limbR]) assert(low>=-1e-12);
 }
}
const packet=(day,iter=1,part=0)=>({u:{lagoon:{day,iter,part}}});
const world={lagoon_iter:1,terrain:[[0,2],[0,0]]};
assert.equal(shouldFetchWorld(packet(9),packet(10),world),true);
assert.equal(shouldFetchWorld(packet(10,1,0),packet(10,1,3),world),true);
assert.equal(shouldFetchWorld(packet(11),packet(10),world),false);
assert.equal(shouldFetchWorld(packet(10,2),packet(9),world),true);
assert.notEqual(terrainIdentity(world),terrainIdentity({...world,terrain:[[0,0],[0,0]]}));
const applied={engine:'test',wall:10,u:{eden:{day:10},lagoon:{day:10}}};
const fresh={...applied,wall:11,status:{fresh:true}};
const transportOnly=heldRecordUpdate(applied,world,null,null,fresh,world);
assert.equal(transportOnly.pending,null);assert.equal(transportOnly.applied,fresh);
assert.equal(transportOnly.applied.wall,11);
const changed={...applied,wall:12,u:{eden:{day:11},lagoon:{day:11}}};
const staged=heldRecordUpdate(applied,world,null,null,changed,world);
assert.equal(staged.pending,changed);assert.equal(staged.applied,applied);
const late=heldRecordUpdate(applied,world,changed,world,fresh,world);
assert.equal(late.pending,changed);assert.equal(late.applied,applied);
const rewind={...changed,wall:13,u:{eden:{day:1},lagoon:{day:1}}};
assert.equal(heldRecordUpdate(applied,world,changed,world,rewind,world).pending,rewind);
const returned=heldRecordUpdate(applied,world,changed,world,{...applied,wall:14},world);
assert.equal(returned.pending,null);assert.equal(returned.applied.wall,14);
const newTerrain={...world,terrain:[[1,1],[1,1]]};
assert.equal(heldRecordUpdate(applied,world,null,null,fresh,newTerrain).pending,fresh);
assert.equal(heldRecordUpdate(applied,world,null,null,{...fresh,engine:'next'},world).pending.engine,'next');
console.log('actual VR helpers: held/action invariance; no random offsets; dry/corner gates; child pose scaling PASS');
"""
        result = subprocess.run([shutil.which('node')],input=script,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_actual_idle_policy_keeps_reading_and_keyboard_focus_bright(self):
        src=read(VR)
        function=src[src.index('function updateChromeIdle('):src.index('function bindInput(')]
        script=r"""
const assert=require('node:assert/strict');
let showRecord=false, keyboardFocus=false, dim=false;
const chrome={querySelector:()=>keyboardFocus?{}:null,classList:{toggle:(name,on)=>{dim=on;}}};
const $=()=>chrome;
"""+function+r"""
updateChromeIdle(0,20000);assert.equal(dim,true);
showRecord=true;updateChromeIdle(0,40000);assert.equal(dim,false);
showRecord=false;keyboardFocus=true;updateChromeIdle(0,60000);assert.equal(dim,false);
keyboardFocus=false;updateChromeIdle(0,60000);assert.equal(dim,true);
updateChromeIdle(59000,60000);assert.equal(dim,false);
"""
        result=subprocess.run([shutil.which('node')],input=script,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('setInterval(() => updateChromeIdle(lastMove), 3000)',src)

    def test_actual_hold_shortcut_ignores_boot_before_first_record(self):
        src=read(VR)
        function=src[src.index('function setHeld('):src.index('// ---- input:')]
        script='const assert=require("node:assert/strict");let state=null;const held={on:false};\n'+function+"\nsetHeld(true);assert.equal(held.on,false);setHeld(false);assert.equal(held.on,false);"
        result=subprocess.run([shutil.which('node')],input=script,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_actual_actor_cache_resets_on_reseed_or_observed_rewind(self):
        src=read(VR)
        hash_source=src[src.index('const hash ='):src.index('// ---- the record')]
        row_source=src[src.index('function personRow('):src.index('async function getJSON(')]
        method=src[src.index('  setSource(u) {'):src.index('  hold() {')]
        script='let worldInfo={lagoon_iter:3,terrain:[[0]]};function worldSize(){return 160;}\n'+src[src.index('function timelineReset('):src.index('// Only interpolate an observed straight dry segment.')]+hash_source+row_source+'function '+method.strip()+r"""
const assert=require('node:assert/strict');
const c={actors:new Map(),key:'eden'};
const row=(x,sex=0)=>[x,1,0,sex,7,17,1,20,22,5,0,0,0,0];
setSource.call(c,{iter:1,day:10,people:[row(1)]});
const prior=c.actors.get(7);
setSource.call(c,{iter:1,day:11,people:[row(5)]});
assert.equal(c.actors.get(7),prior);assert.equal(prior.px,1);assert.equal(prior.x,5);
setSource.call(c,{iter:2,day:0,people:[row(8,1)]});
const next=c.actors.get(7);
assert.notEqual(next,prior);assert.equal(next.px,8);assert.equal(next.sex,1);
setSource.call(c,{iter:2,day:9,people:[row(9,1)]});
setSource.call(c,{iter:2,day:8,people:[row(3,1)]});
assert.notEqual(c.actors.get(7),next);assert.equal(c.actors.get(7).px,3);
c.key='lagoon';setSource.call(c,{iter:3,day:1,people:[row(2)]});
const oldTerrainPerson=c.actors.get(7);worldInfo={lagoon_iter:3,terrain:[[1]]};
setSource.call(c,{iter:3,day:2,people:[row(4)]});
assert.notEqual(c.actors.get(7),oldTerrainPerson);assert.equal(c.actors.get(7).px,4);
"""
        result=subprocess.run([shutil.which('node')],input=script,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


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


@unittest.skipUnless(shutil.which('node'), 'optional workbench JS execution')
class TestHumanAnatomyAndGait(unittest.TestCase):
    def execute(self, script):
        src=read(VR)
        helpers=src[src.index('const STATURE ='):src.index('const _m =')]
        result=subprocess.run([shutil.which('node')],input=helpers+script,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_explicit_detail_requires_known_adult_bare_body_and_no_sexual_act(self):
        self.execute("""
const assert=require('node:assert/strict');
for(const age of [undefined,null,NaN,Infinity,'30',0,6,12,17.99])
 assert.equal(visibleAdultAnatomy({age,sex:0,act:0},'',true),false);
for(const sex of [0,1])for(const age of [18,30,70]) {
 const a={age,sex,act:0};assert.equal(visibleAdultAnatomy(a,'',true),true);
 for(const dress of ['swim','hide','fur'])assert.equal(visibleAdultAnatomy(a,dress,true),false);
 assert.equal(visibleAdultAnatomy(a,'',false),false);
 for(const act of [A.MATE,A.BIRTH])assert.equal(visibleAdultAnatomy({...a,act},'',true),false);
}
assert.equal(visibleAdultAnatomy({age:30,act:0},'',true),false);
for(const key of ['eden','lagoon']) {
 assert.equal(clothingOf({age:30,id:7},key,{modesty:0}), '');
 assert.equal(clothingOf({age:30,id:7},key,{modesty:1}),key==='eden'?'swim':'hide');
 assert.equal(clothingOf({age:6,id:7},key,{modesty:1}), '');
}
assert.equal(clothingOf({age:6,id:7},'lagoon',{season:'winter',modesty:0}), 'fur');
""")

    def test_stance_is_distance_driven_and_leg_bones_do_not_stretch(self):
        self.execute("""
const assert=require('node:assert/strict');
for(const age of [3,6,12,18,30,70])for(const sex of [0,1]) {
 const D=bodyDimensions(age,sex),H=D.H,cycle=.58*H,L=D.thigh+D.shin;
 for(let i=0;i<100;i++) {
  const distance=i/100*cycle,feet=[-1,1].map(s=>gaitFoot(distance,H,s));
  const allowed=Math.min(...feet.filter(f=>f.stance).map(f=>.034375*H+Math.sqrt(L*L-f.z*f.z)));
  const hip=Math.min(D.hipY,allowed-1e-5);
  for(const f of feet) {
   const a={x:0,y:hip,z:0},target={x:0,y:.034375*H+f.lift,z:f.z};
   const j=legIK(a,target,D.thigh,D.shin);
   assert(Math.abs(Math.hypot(j.middle.y-a.y,j.middle.z-a.z)-D.thigh)<1e-8);
   assert(Math.abs(Math.hypot(j.end.y-j.middle.y,j.end.z-j.middle.z)-D.shin)<1e-8);
   if(f.stance)assert(Math.abs(j.end.y-target.y)<1e-7&&Math.abs(j.end.z-target.z)<1e-7);
  }
 }
 for(const side of [-1,1]) {
  const phaseOffset=side>0?.5:0;
  const distance=(side>0?.6:.1)*cycle;
  const a=gaitFoot(distance,H,side),b=gaitFoot(distance+.001,H,side);
  assert(a.stance&&b.stance);assert(Math.abs(distance+a.z-(distance+.001+b.z))<1e-9);
 }
}
""")

    def test_meshes_keep_sex_shape_and_neutral_children_separate(self):
        src=read(VR)
        self.assertIn('this.torsoFemale = inst(torsoGeometry(true), cap)',src)
        self.assertIn('this.torsoChild = inst(torsoGeometry(false,true), cap)',src)
        self.assertIn('const torsoMesh=!adult?this.torsoChild',src)
        self.assertIn('visibleAdultAnatomy(a,dress,true)',src)
        self.assertIn('a.walkDistance = (a.walkDistance || 0) + step',src)
        self.assertNotIn('Math.sin(t * (fast ? 9.0',src)


    def test_arm_ik_handles_collinear_hints_without_changing_bone_length(self):
        self.execute("""
const assert=require('node:assert/strict');
for(const target of [{x:0,y:0,z:0},{x:0,y:-.4,z:0},{x:.2,y:.1,z:.2}]) {
 const root={x:0,y:0,z:0},j=armIK(root,target,{x:0,y:0,z:0},.3,.2);
 const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
 assert(Math.abs(dist(root,j.middle)-.3)<1e-8);assert(Math.abs(dist(j.middle,j.end)-.2)<1e-8);
}
""")
