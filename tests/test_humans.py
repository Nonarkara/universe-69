"""Skinned humans for the headset viewer (web/humans.js, web/humans/).

Near people are real skinned bodies moved by captured clips; far people stay
on the instanced figures. These tests pin what keeps that honest and
shippable: CC0/MIT assets recorded in CREDITS, everything local and mirrored
to docs/, every clip the viewer plays actually packed, the body read from the
record's own fields, a sleeper never drawn with a death clip, and a budget
on how many skinned bodies a headset is asked to draw.
"""

import json
import os
import re
import struct
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DOCS = os.path.join(ROOT, "docs")
HUMANS_JS = os.path.join(WEB, "humans.js")
ASSETS = os.path.join(WEB, "humans")
ADDONS = os.path.join(WEB, "addons")
VR = os.path.join(WEB, "vr.html")
SERVER = os.path.join(ROOT, "sim", "server.py")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def glb_json(path):
    with open(path, "rb") as f:
        b = f.read()
    n = struct.unpack("<I", b[12:16])[0]
    return json.loads(b[20:20 + n])


def tree(base):
    out = {}
    for d, _, files in os.walk(base):
        for f in files:
            p = os.path.join(d, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, base)] = fh.read()
    return out


class TestAssetsAreLocalLicensedAndMirrored(unittest.TestCase):
    def test_docs_mirror_is_byte_identical(self):
        self.assertEqual(read(HUMANS_JS), read(os.path.join(DOCS, "humans.js")))
        self.assertEqual(tree(ASSETS), tree(os.path.join(DOCS, "humans")))
        self.assertEqual(tree(ADDONS), tree(os.path.join(DOCS, "addons")))

    def test_every_asset_is_credited_with_its_licence(self):
        credits = read(os.path.join(ASSETS, "CREDITS.md"))
        self.assertIn("CC0 1.0", credits)
        self.assertIn("MIT", credits)
        for f in os.listdir(ASSETS):
            if f.endswith((".glb", ".jpg")):
                stem = "hair_*.glb" if f.startswith("hair_") else f
                self.assertIn(stem, credits, f"{f} is not credited")

    def test_no_external_fetches(self):
        for path in (HUMANS_JS, os.path.join(ASSETS, "study.html")):
            src = read(path)
            for cdn in ("http://", "https://", "unpkg.com", "jsdelivr", "esm.sh"):
                self.assertNotIn(cdn, src.replace("https://creativecommons", ""), path)

    def test_addons_are_three_r160_and_resolve_locally(self):
        src = read(os.path.join(ADDONS, "GLTFLoader.js"))
        self.assertIn("from './BufferGeometryUtils.js'", src)
        self.assertIn('"three":"./three.module.min.js"', read(VR))

    def test_the_bodies_share_one_rig_with_the_clips(self):
        bones = lambda j: {n.get("name") for n in j["nodes"]}
        anims = glb_json(os.path.join(ASSETS, "anims.glb"))
        for sex in ("male", "female"):
            body = glb_json(os.path.join(ASSETS, sex + ".glb"))
            self.assertTrue(body.get("skins"), f"{sex}.glb has no skeleton")
            for bone in ("pelvis", "spine_02", "Head", "thigh_l", "calf_r", "ball_l"):
                self.assertIn(bone, bones(body))
                self.assertIn(bone, bones(anims))
            for img in body["images"]:
                self.assertEqual(img["mimeType"], "image/jpeg")

    def test_every_clip_the_viewer_plays_is_packed(self):
        packed = {a["name"] for a in glb_json(os.path.join(ASSETS, "anims.glb"))["animations"]}
        played = set(re.findall(r"'([A-Z][A-Za-z_]+_Loop|Fixing_Kneeling|PickUp_Table|Punch_Jab)'",
                                read(HUMANS_JS)))
        self.assertTrue(played)
        self.assertEqual(played - packed, set(), "humans.js plays a clip that is not packed")

    def test_assets_stay_small_enough_for_pages_and_a_headset(self):
        total = sum(len(b) for b in tree(ASSETS).values())
        self.assertLess(total, 14 * 1024 * 1024)


class TestTheBodyComesFromTheRecord(unittest.TestCase):
    def setUp(self):
        self.src = read(HUMANS_JS)

    def test_age_mass_and_strength_shape_the_body(self):
        self.assertIn("band(a.age)", self.src)
        self.assertIn("a.bmi", self.src)
        self.assertIn("a.sn", self.src)
        for attr in ("aFat", "aMuscle", "aBelly"):
            self.assertIn(attr, self.src)

    def test_a_sleeper_is_not_a_corpse(self):
        self.assertNotIn("Death", self.src)
        self.assertIn("CURL", self.src)

    def test_everyone_wears_something_and_children_are_covered(self):
        vr = read(VR)
        self.assertIn('(this.key === "eden" ? "swim" : "hide")', vr)
        for kind in ("hide", "swimM", "swimF", "fur"):
            self.assertIn(kind + ":", self.src)

    def test_the_viewer_never_writes(self):
        self.assertNotIn("fetch(", self.src)
        self.assertNotIn("/pace", self.src)

    def test_a_headset_draws_a_bounded_number_of_skinned_bodies(self):
        vr = read(VR)
        m = re.search(r"renderer\.xr\.isPresenting \? (\d+) : (\d+)", vr)
        self.assertIsNotNone(m)
        self.assertLessEqual(int(m.group(1)), 24)
        self.assertLessEqual(int(m.group(2)), 40)

    def test_instanced_figures_remain_the_fallback(self):
        vr = read(VR)
        self.assertIn("else this.drawBody(a, root, t, big, fast, c);", vr)
        self.assertIn("falling back to instanced figures", self.src)


class TestTheServerServesTheHumans(unittest.TestCase):
    def test_routes(self):
        src = read(SERVER)
        self.assertIn('path == "/humans.js"', src)
        self.assertIn('"/humans/", "/addons/"', src)
        self.assertIn('".glb": "model/gltf-binary"', src)


if __name__ == "__main__":
    unittest.main()
