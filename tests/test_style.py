"""The house style, as law.

The owner's brief of 2026-10-28 retired the 8-bit world: the worlds are now
painted at the screen's own resolution on one designed palette, TERRARIUM,
whose tokens live on `:root` and are the only source of colour for the
canvas. The people keep their anatomy rig and the canon it is checked
against; the page is one screen that never scrolls, and anything long is
read in pages. GRAPHICS.md §1 is the prose version of what is pinned here.

Style written only in prose is style that gets lost at the end of a long
session. This file pins the measurable parts of the brief, so a change that
breaks them fails the suite instead of the eye.

**Change one of these on purpose and you must change it here too, in the
same commit, where the owner will see it.**
"""

import os
import json
import shutil
import subprocess
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERER = os.path.join(ROOT, "web", "index.html")
MIRROR = os.path.join(ROOT, "docs", "index.html")

# TERRARIUM, as shipped: the console tokens and the world tokens on :root.
# GRAPHICS.md §1 names the palette and gives the contrast table.
TERRARIUM = {
    "--surface": "#14130f", "--surface-2": "#1c1a15", "--ink": "#ede6d6",
    "--muted": "#a39b88", "--dim": "#8a8372", "--line": "#37332a",
    "--accent": "#e4b456", "--eden": "#8ec5d6", "--lagoon": "#a6c98a",
    "--warn": "#ec8f74",
    "--w-deep": "#2b5770", "--w-shallow": "#6fa1ac", "--w-sand": "#d6c294",
    "--w-grass": "#6d8a4b", "--w-floor": "#4a6436", "--w-can": "#3f6236",
    "--w-night": "rgba(14,20,44,0.50)", "--w-fire": "#ffae5a",
}
TEXT_TOKENS = ("--ink", "--muted", "--dim", "--accent", "--eden", "--lagoon", "--warn")
SURFACES = ("--surface", "--surface-2")


def read_renderer():
    with open(RENDERER) as f:
        return f.read()


def root_tokens(src):
    m = re.search(r":root \{(.*?)\n  \}", src, re.S)
    assert m, "the palette has no :root block"
    return dict(re.findall(r"(--[\w-]+):\s*([^;]+);", m.group(1)))


def luminance(hexcol):
    h = hexcol.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def numbers_in(src, name):
    """A `var NAME=[...]` table, as a list of floats."""
    m = re.search(r"var %s\s*=\s*\[([^\]]*)\]" % re.escape(name), src)
    assert m, "the renderer has no %s table" % name
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", m.group(1))]


class TestThePalette(unittest.TestCase):
    def test_the_palette_is_terrarium(self):
        """One designed palette, on :root, as named in GRAPHICS.md."""
        toks = root_tokens(read_renderer())
        for k, v in TERRARIUM.items():
            self.assertEqual(toks.get(k), v, f"{k} changed")

    def test_text_clears_wcag_aa(self):
        """Every text colour reads on every console surface at 4.5:1."""
        toks = root_tokens(read_renderer())
        for t in TEXT_TOKENS:
            for s in SURFACES:
                self.assertGreaterEqual(contrast(toks[t], toks[s]), 4.5, f"{t} on {s}")

    def test_the_canvas_takes_its_colours_from_the_tokens(self):
        """The painters read P, and P is read from :root — no second palette."""
        src = read_renderer()
        self.assertIn("var PALETTE_TOKENS={", src)
        self.assertIn("getComputedStyle(document.documentElement)", src)
        self.assertNotRegex(src, r"var P = \{", "a literal palette object is back")

    def test_no_slop_faces(self):
        """No Inter / Poppins / Roboto as the design face (anti-slop rule 4)."""
        src = read_renderer()
        for face in ("Inter", "Poppins", "Roboto", "Montserrat", "Open Sans"):
            self.assertNotRegex(src, r"family=%s\b|\"%s\"" % (face.replace(" ", "\\+"), face))


class TestTheResolution(unittest.TestCase):
    def test_the_world_is_not_pixelated(self):
        """The 8-bit world is retired: no pixelated canvas, no tile blow-up."""
        src = read_renderer()
        self.assertNotIn("image-rendering:pixelated", src)
        self.assertNotRegex(src, r"var PX\s*=")

    def test_the_ground_is_painted_at_device_resolution_and_cached(self):
        src = read_renderer()
        self.assertIn("function drawGround(", src)
        self.assertIn("function groundStep(", src)        # cached per quarter-octave zoom
        self.assertIn("function fillField(", src)         # smooth coasts, not tile steps
        self.assertIn("devicePixelRatio", src)

    def test_a_sprite_is_forty_units_wide(self):
        """The figure sprite is a fixed box in figure units."""
        src = read_renderer()
        body = src.split("function figureSprite(")[-1].split("function ")[0]
        m = re.search(r"Math\.ceil\((\d+)\*sq\)", body)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), 40)


class TestOneScreen(unittest.TestCase):
    def test_the_page_never_scrolls(self):
        src = read_renderer()
        self.assertIn("html, body { height:100dvh; overflow:hidden; }", src)
        css = src.split("<style>")[1].split("</style>")[0]
        self.assertNotIn("overflow-y:auto", css, "a scrolling region is back")
        self.assertNotIn("overflow:auto", css)

    def test_long_content_is_read_in_pages(self):
        src = read_renderer()
        self.assertIn("function paginate(", src)
        for bar in ('id="recpager"', 'id="respager"', 'id="bookpager"'):
            self.assertIn(bar, src)
        self.assertIn('openBook("book/book.json")', src)
        self.assertIn("loadJSONOnce(src)", src)
        self.assertIn('loadJSONOnce("book/origin.json")', src)


class TestTheBody(unittest.TestCase):
    def table(self, name):
        return numbers_in(read_renderer(), name)

    def heads_at(self, age):
        bands, heads = self.table("AGE_BAND"), self.table("HEADS")
        self.assertEqual(len(bands), len(heads), "the age table changed shape")
        i = max(j for j, a in enumerate(bands) if age >= a)
        return heads[i]

    def test_an_adult_is_about_seven_and_a_half_heads(self):
        """The proportions are the brief: an adult is not a chibi."""
        heads = self.heads_at(30)
        self.assertGreater(heads, 7.0,
                           f"an adult is only {heads:.1f} heads tall — that is a "
                           f"stylisation, not a body")
        self.assertLess(heads, 8.5,
                        f"an adult is {heads:.1f} heads tall — too stretched")

    def test_children_have_the_proportions_of_children(self):
        """Head to height by age, from the anthropometric canon: 1/4 at
        birth, ~1/5 at two or three, ~1/6 at six, ~1/7 at twelve. A child is
        not a small adult."""
        for age, want in ((0, 4.0), (3, 5.0), (6, 6.0), (12, 7.0)):
            got = self.heads_at(age)
            self.assertAlmostEqual(got, want, delta=0.35,
                                   msg=f"at {age} a body is {got} heads, not ~{want}")

    def test_the_head_is_sized_from_the_table(self):
        """The drawn head is the table's head: stature / heads, and the
        skull is drawn 2.12 radii tall."""
        src = read_renderer()
        self.assertRegex(src, r"headH=H/HEADS\[i\]")
        self.assertRegex(src, r"hr:headH/2\.12")

    def test_a_man_is_wider_at_the_shoulder_a_woman_at_the_hip(self):
        """Adult widths, as fractions of stature: a man's shoulders outgrow
        his hips; a woman's hips are about as wide as her shoulders."""
        src = read_renderer()
        m = re.search(r"var sh=lerp\(SH_FRAC\[ci\], fem\?([\d.]+):([\d.]+), dm\)\*H, "
                      r"hp=lerp\(HP_FRAC\[ci\], fem\?([\d.]+):([\d.]+), dm\)\*H", src)
        self.assertIsNotNone(m, "the shoulder and hip widths moved")
        f_sh, m_sh, f_hp, m_hp = map(float, m.groups())
        self.assertGreater(m_sh / m_hp, 1.15, "a man's shoulders are not wider than his hips")
        self.assertLess(abs(f_hp / f_sh - 1.0), 0.12, "a woman's hips are not about her shoulders")

    def test_the_figure_is_a_skeleton_with_a_skin(self):
        """Every joint of the rig has a parent, and the drawing is solved
        through it: the pose solver places hands and feet, the skeleton keeps
        the bones their length, the skin is painted around the bones."""
        src = read_renderer()
        m = re.search(r"var RIG_PARENT=\{(.*?)\};", src, re.S)
        self.assertIsNotNone(m, "the rig is gone")
        joints = set(re.findall(r"(\w+):", m.group(1)))
        for j in ("pelvis", "spine", "chest", "neck", "head", "clavL", "clavR",
                  "shL", "shR", "elbL", "elbR", "wriL", "wriR",
                  "hipL", "hipR", "kneeL", "kneeR", "ankL", "ankR"):
            self.assertIn(j, joints, f"the rig has no {j}")
        body = src.split("function drawSketch(")[1].split("\nfunction ")[0]
        self.assertIn("buildRig(", body, "the figure is not drawn from the rig")
        self.assertIn("function ik2(", src, "limbs are no longer solved")
        self.assertIn("paintForm(", body, "the skin is no longer painted")

    def test_a_woman_stands_shorter_than_a_man(self):
        """Adult men are about 7% taller than women; the drawing says so."""
        self.assertIn("STATURE[B.ab]*(fem?1-0.07*D.dm:1)", read_renderer())

    def test_the_body_reads_from_the_record(self):
        """BMI, strength, injury, pregnancy and hunger all reach the drawing
        and the sprite key, so a cached figure is never someone else's body."""
        src = read_renderer()
        key = src.split("function figureSprite(")[1].split("var sp=")[0]
        for field in ("B.fat", "B.mus", "B.hurt", "B.preg", "B.hungry", "B.ab"):
            self.assertIn(field, key, f"{field} is not in the sprite key")

    def test_children_never_get_genital_detail(self):
        """Every genital stroke sits behind the adult gate."""
        src = read_renderer()
        body = src.split("function drawSketch(")[1].split("\nfunction ")[0]
        self.assertEqual(body.count("pubic hair") + body.count("h1<5"), 2)
        self.assertEqual(body.count("adult && s>=2 && bare && !private_"), 2,
                         "anatomical detail is drawn outside the adult gate")

    def test_the_head_has_a_jaw(self):
        """A plain oval is an egg, not a head."""
        src = read_renderer()
        self.assertNotIn("g.ellipse(hcx, hcy, hr*0.88, hr,", src,
                         "the head is an ellipse again; it lost its jaw")
        self.assertIn("quadraticCurveTo", src)

    def test_a_pair_is_drawn_as_one_picture(self):
        """The owner asked for this by name. It was quietly deleted once."""
        src = read_renderer()
        self.assertIn("function drawMating(", src,
                      "the couple is no longer drawn as one picture")
        self.assertIn("function matingSprite(", src)
        self.assertIn("matingSprite(", src.split("function matingSprite(")[-1],
                      "the pair sprite is never used by the renderer")

    def test_the_walk_has_a_planted_foot(self):
        """A foot that slides on a sine wave is not a walk."""
        src = read_renderer()
        self.assertIn("function leg(p)", src,
                      "the stance/swing walk cycle is gone")
        self.assertIn("stance", src)
        self.assertIn("swing", src.lower())


class TestTheStandingBody(unittest.TestCase):
    """The canon a figure drawer checks a standing adult against (Loomis 1943):
    crotch at half height, knee a quarter of the way up, elbow at the waist,
    wrist at the crotch. Computed from the renderer's own tables, so a change
    to the rig that breaks the canon fails here."""

    def setUp(self):
        self.src = read_renderer()

    def num(self, pattern):
        m = re.search(pattern, self.src)
        self.assertIsNotNone(m, f"the rig moved: {pattern}")
        return float(m.group(1))

    def landmarks(self):
        H = 32.0
        heads = numbers_in(self.src, "HEADS")[7]
        leg_frac = numbers_in(self.src, "LEG_FRAC")[7]
        arm_frac = numbers_in(self.src, "ARM_FRAC")[7]
        head_h = H / heads
        sh_y = head_h * (1 + self.num(r"shY=headH\*\(1\+\(i<=1\?[\d.]+:([\d.]+)\)\)"))
        hip_y = H * (1 - leg_frac)
        leg = 31.2 - hip_y - 0.3
        thigh = leg * self.num(r"thigh:leg\*([\d.]+)")
        upper = arm_frac * H * self.num(r"upper:arm\*([\d.]+)")
        crotch = hip_y + head_h * self.num(r"crotch:headH\*([\d.]+)") * self.num(r"crotchY=hipY\+D\.crotch\*([\d.]+)")
        waist = sh_y + (hip_y - sh_y) * self.num(r"waY=shY\+\(hipY-shY\)\*([\d.]+)")
        shoulder = sh_y + 0.9
        return dict(H=H, crotch=crotch, knee=hip_y + 0.3 + thigh, elbow=shoulder + upper,
                    wrist=shoulder + arm_frac * H * 0.99, waist=waist)

    def test_crotch_at_half_height(self):
        L = self.landmarks()
        self.assertAlmostEqual(L["crotch"] / L["H"], 0.5, delta=0.04)

    def test_knee_a_quarter_from_the_ground(self):
        L = self.landmarks()
        self.assertAlmostEqual((L["H"] - L["knee"]) / L["H"], 0.25, delta=0.03)

    def test_elbow_at_the_waist_and_wrist_at_the_crotch(self):
        L = self.landmarks()
        self.assertLess(abs(L["elbow"] - L["waist"]), 1.5)
        self.assertLess(abs(L["wrist"] - L["crotch"]), 1.0)

    def test_standing_is_not_a_crouch(self):
        """The leg is exactly as long as hip to ankle, so a standing leg is
        straight; standing sets the rest pose (level pelvis, contrapposto)."""
        self.assertIn("leg=(31.2-hipY-0.3);", self.src)
        self.assertIn("P.rest=1; P.lean=0;", self.src)
        self.assertIn("var tilt=P.rest?", self.src)

    def test_hands_are_mittens_and_small_figures_have_their_own_drawing(self):
        body = self.src.split("function drawSketch(")[1].split("\nfunction ")[0]
        self.assertNotIn("fingers", body, "hands grew spikes again")
        self.assertIn("function drawFar(", self.src)      # 10-26 px: silhouette first
        self.assertIn("function drawTiny(", self.src)     # under 10 px: an upright mark


class TestTheInstrumentStrip(unittest.TestCase):
    """The researcher's strip: eight gauges, both worlds on one scale, ticks
    where the literature gives one, and a note that says these are model
    readings. Its references are pinned so a tick cannot drift silently."""

    def gauges(self):
        src = read_renderer()
        block = src.split("var GAUGES=[")[1].split("\n];")[0]
        return re.findall(r'\{ key:"(\w+)", label:"([^"]+)"(?:, ticks:\[([^\]]*)\])?', block)

    def test_eight_gauges_in_order(self):
        keys = [k for k, _, _ in self.gauges()]
        self.assertEqual(keys, ["pop", "net", "inf", "brd", "clm", "snk", "food", "vio"])

    def test_reference_ticks_are_the_cited_ones(self):
        ticks = {k: [float(x) for x in t.split(",")] if t else [] for k, _, t in self.gauges()}
        self.assertEqual(ticks["net"], [0])
        # This legacy field divides different cohorts; survival references
        # would imply a comparison the observation cannot support.
        self.assertEqual(ticks["inf"], [])
        self.assertEqual(ticks["clm"], [1])
        self.assertEqual(ticks["snk"], [25, 60])         # even over four hoppers; Calhoun 1962
        self.assertEqual(ticks["vio"], [1, 524])         # Pinker 2011
        self.assertEqual(ticks["brd"], [])               # the extinction clock has no tick

    def test_every_note_says_it_is_a_model_reading(self):
        src = read_renderer()
        self.assertIn('var NOT_FINDINGS=" Model readings, not findings about people.";', src)
        self.assertIn("GAUGES[i].note+NOT_FINDINGS", src)

    def test_old_census_rows_are_tolerated(self):
        """Live saves carry 4-field rows; a missing column reads as null."""
        self.assertIn("r.length>i", read_renderer())

    def test_no_gradient_in_the_strip(self):
        src = read_renderer()
        block = src.split("// =========================================================== the instrument strip")[1].split("// =========================================================== god panel")[0]
        self.assertNotIn("Gradient(", block)


class TestTheWorldsAtWork(unittest.TestCase):
    """The owner's brief: we must SEE them survive — build, hunt, fish, farm,
    court, give birth, defend themselves — and see EDEN as a resort island."""

    def setUp(self):
        self.src = read_renderer()

    def test_huts_come_from_the_record_in_stages(self):
        self.assertIn("(u.huts||[]).forEach", self.src)
        body = self.src.split("function drawHut(")[1].split("\nfunction ")[0]
        self.assertIn("if (p<1){", body, "no construction stages")
        self.assertIn("P.hutdoor", body, "a finished hut has a door")
        self.assertNotIn("paintHut9", self.src, "the decorative camp hut is back")

    def test_encounters_are_drawn_and_filmed(self):
        for kind in ("deer_kill", "cat_hunt", "fought_off", "taken", "mauled"):
            self.assertIn(kind, self.src)
        self.assertIn("function drawEncounters(", self.src)
        self.assertIn("(u.encounters||[]).forEach", self.src.split("function pickShot(")[1])

    def test_carry_and_hunger_reach_the_body(self):
        self.assertIn("a.carry = p.length>12 ? (p[12]|0) : 0;", self.src)
        self.assertIn("a.hun = p.length>13 ? (p[13]|0) : -1;", self.src)
        key = self.src.split("function figureSprite(")[1].split("var sp=")[0]
        for f in ("B.carry", "B.gaunt", "B.infant"):
            self.assertIn(f, key)
        self.assertIn("function drawHeld(", self.src)

    def test_the_couple_is_drawn_from_the_rig(self):
        body = self.src.split("function drawMating(")[1].split("\nfunction ")[0]
        self.assertEqual(body.count("drawSketch("), 2, "the pair is not two rigged bodies")

    def test_watch_stands_with_a_spear(self):
        case = self.src.split("case A_WATCH:")[1].split("break; }")[0]
        self.assertNotIn("P.sit=1", case)
        self.assertIn("P.tool=1", case)

    def test_eden_is_a_resort_island(self):
        body = self.src.split("var EDEN_WORLD={")[1].split("\n};")[0]
        for part in ("a resort island in a calm, painted sea", "the dome's edge",
                     "stools along the counter", "loungers", "the pool"):
            self.assertIn(part, body)


class TestTheReader(unittest.TestCase):
    """The Book, its timeline, and the archive of the first run, in one reader."""

    def setUp(self):
        self.src = read_renderer()

    def test_the_timeline_is_a_log_scale_of_years_ago(self):
        self.assertIn('id="tltrack"', self.src)
        self.assertIn('role="slider"', self.src)
        self.assertIn("function tlX(at){ var ago=Math.max(0,-at); return 1-Math.log(1+ago)/Math.log(1+TL.max); }", self.src)
        self.assertIn("function tlChapterAt(", self.src)

    def test_the_first_run_opens_in_the_same_reader(self):
        self.assertIn('"archive/archive.json"', self.src)
        self.assertIn('id="archivebtn"', self.src)

    def test_a_page_never_cuts_its_last_block(self):
        self.assertIn("this.target.scrollHeight>this.target.clientHeight+1", self.src)


class TestTheMirror(unittest.TestCase):
    def test_the_mirror_is_identical(self):
        with open(RENDERER) as a, open(MIRROR) as b:
            self.assertEqual(a.read(), b.read(),
                             "web/index.html and docs/index.html have diverged")


@unittest.skipUnless(shutil.which('node'), 'Node is a workbench-only viewer test runner')
class TestActualSocialContact(unittest.TestCase):
    def helper(self, expression):
        src = read_renderer()
        self.assertTrue('function contactPartner(' in src, 'Actual-contact helper missing')
        helper = src[src.index('function contactPartner('):src.index('function craftActivity(')]
        body = re.search(r'var AGE_BAND=\[[^;]+;', src).group(0) + src[src.index('function ageBand('):src.index('// The rig\'s measurements')]
        js = helper + body + '\nprocess.stdout.write(JSON.stringify(' + expression + '));'
        return json.loads(subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True).stdout)

    def test_bond_or_matching_actions_do_not_create_contact(self):
        self.assertEqual(self.helper("[contactPartner({},1,'mate'),contactPartner({social:{1:{kind:'mate',other:2,mutual:false,contact:false}}},1,'mate')]"), [0,0])

    def test_only_reciprocal_mutual_contact_links_the_actual_pair(self):
        self.assertEqual(self.helper("contactPartner({social:{1:{kind:'mate',other:3,mutual:true,contact:true},3:{kind:'mate',other:1,mutual:true,contact:true}}},1,'mate')"),3)

    def test_missing_arrival_wrong_partner_kind_and_asymmetric_contact_are_rejected(self):
        self.assertEqual(self.helper("[{kind:'mate',other:1,mutual:true,contact:false},{kind:'mate',other:9,mutual:true,contact:true},{kind:'groom',other:1,mutual:true,contact:true}].map(function(x){return contactPartner({social:{1:{kind:'mate',other:2,mutual:true,contact:true},2:x}},1,'mate');})"),[0,0,0])

    def test_pending_and_actual_labels_do_not_claim_an_encounter_from_a_bond(self):
        self.assertEqual(self.helper("[socialActivity({},1,8),socialActivity({},1,21),socialActivity({},1,7),socialActivity({social:{1:{kind:'mate',other:2,mutual:true,contact:true},2:{kind:'mate',other:1,mutual:true,contact:true}}},1,8)]"),['seeking a partner','seeking grooming contact','','mating'])

    def test_expanded_activity_counts_do_not_call_pending_intent_sex(self):
        src = read_renderer()
        contact = src[src.index('function contactPartner('):src.index('function craftActivity(')]
        tally = src[src.index('function doingHTML('):src.index("// The world's own facts")]
        js = contact + "var ACT_LABEL=[];" + tally + "process.stdout.write(JSON.stringify(doingHTML([[1,1,0,0,1,8],[1,1,0,1,2,8]],{})));"
        result = json.loads(subprocess.run(['node','-e',js], check=True,capture_output=True,text=True).stdout)
        self.assertIn('2 seeking a partner', result)
        self.assertNotIn('making love', result)
        self.assertNotIn('mating', result)

    def test_first_snapshot_populates_record_before_any_animation_frame(self):
        src = read_renderer()
        poll = src[src.index('function poll(){'):src.index('// 30 frames a second')]
        setup = "var called=false,received=null,packet={events:[],u:{eden:{iter:1,day:0,size:48,people:[],detail:{}},lagoon:{iter:1,day:0,people:[],detail:{}}}},polling=false,SNAP=false,state=null,pollSeq=0,snapBad=false,snapReady=false,worldInfo={},lagoonIter=1,edenSize=0,EM=6,actors6={},actors9={},heat9=null,ground={};var document={getElementById:function(id){return id==='research'?{hidden:true}:null;}};function fetchJSON(){return Promise.resolve(packet);}function hideFail(){}function syncActors(){}function keepDiary(){}function freshness(){}function updateStrip(){}function updateRecords(events){called=true;received=events;}function showFail(){}"
        js = setup + poll + "poll();setTimeout(function(){process.stdout.write(JSON.stringify([called,received]));},0);"
        result = json.loads(subprocess.run(['node','-e',js],check=True,capture_output=True,text=True).stdout)
        self.assertEqual(result,[True,[]])

    def test_unaccepted_intents_use_neutral_pose_without_breaking_walking(self):
        self.assertEqual(self.helper("[socialDrawAct({}, {id:1,act:8,moving:false,age:18}),socialDrawAct({}, {id:1,act:21,moving:false}),socialDrawAct({}, {id:1,act:8,moving:true,age:18}),socialDrawAct({social:{1:{kind:'mate',other:2,mutual:true,contact:true},2:{kind:'mate',other:1,mutual:true,contact:true}}},{id:1,act:8,moving:false,age:18})]"),[11,11,8,8])
        self.assertEqual(self.helper("[16,17,18,undefined].map(function(age){return socialDrawAct({social:{1:{kind:'mate',other:2,mutual:true,contact:true},2:{kind:'mate',other:1,mutual:true,contact:true}}},{id:1,act:8,moving:false,age:age});})"),[11,11,8,11])


if __name__ == "__main__":
    unittest.main()
