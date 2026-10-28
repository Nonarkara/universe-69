"""The house style, as law.

The owner wrote the style down: chunky pixels, `image-rendering: pixelated`,
flat palettes with three tones per material, a monospace HUD, and people
drawn as bodies with real proportion — an adult about 7.5 heads. It is in
`AGENTS.md` and in `GRAPHICS.md`.

Those words did not stop a renderer from being re-palettied into something
else, from being given round chibi heads, and from quietly losing the two
things the owner asked for by name: a couple drawn as one picture, and a
walk with a planted foot. Style written only in prose is style that gets
lost at the end of a long session.

This file is the guard. It pins the measurable parts of the brief, so a
change that breaks them fails the suite instead of the eye.

**Change one of these on purpose and you must change it here too, in the
same commit, where the owner will see it.**
"""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERER = os.path.join(ROOT, "web", "index.html")
MIRROR = os.path.join(ROOT, "docs", "index.html")

# The house palette, as shipped. Flat, three tones per material, one alpha
# for the shadow. GRAPHICS.md §1 is the prose version of this table.
HOUSE_PALETTE = {
    "waterD": "#1a4580", "water": "#2559a3", "waterS": "#3a78c8",
    "waterL": "#5a94d8", "foam": "#d4ecfa",
    "sand": "#d4bc7a", "sandL": "#e2cf96", "sandD": "#b89c58", "sandWet": "#b9a060",
    "grass": "#4e8a3a", "grassD": "#3f7230", "grassL": "#6aa84e", "grassX": "#2f5d26",
    "floorF": "#2f5e28", "canD": "#1b421b", "can": "#2f6b2c", "canL": "#4d8f3e",
    "canX": "#6cab52",
    "trunk": "#6b4226", "trunkD": "#4e2f18",
    "soil": "#8a6530", "soilD": "#6e4e1c", "soilL": "#a07a3e", "path": "#a8946a",
    "thatch": "#9a7a3a", "thatchD": "#7c6028", "thatchL": "#b8955a",
    "hutwall": "#7a5a34", "hutdoor": "#2c1a0c",
    "stone": "#b4ac9c", "stoneB": "#bcb4a4", "mortar": "#978f80", "dust": "#a8a092",
    "wallTop": "#8a7f6c", "wall": "#6a5f4e", "wallFace": "#473d30", "alcove": "#2e2619",
    "hopper": "#e0b838", "hopperD": "#b08a18", "trough": "#4a90d9",
    "lawn": "#55a04c", "lawnD": "#4c9344", "palm": "#2f7a38", "palmL": "#3f9a48",
    "pool": "#38b8e0", "poolL": "#7cd8f0", "rim": "#e8e8e0", "deck": "#d8c9a0",
    "shadow": "rgba(0,0,0,0.30)",
}


def read_renderer():
    with open(RENDERER) as f:
        return f.read()


def palette_of(src):
    """The `P` object in the renderer, as a dict of name -> colour."""
    m = re.search(r"var P = \{(.*?)\};", src, re.S)
    assert m, "the renderer has no palette object"
    out = {}
    for name, val in re.findall(r'(\w+):\s*"([^"]+)"', m.group(1)):
        out[name] = val
    return out


def numbers_in(src, name):
    """A `var NAME=[...]` table, as a list of floats."""
    m = re.search(r"var %s\s*=\s*\[([^\]]*)\]" % re.escape(name), src)
    assert m, "the renderer has no %s table" % name
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", m.group(1))]


class TestThePalette(unittest.TestCase):
    def test_the_palette_is_the_house_palette(self):
        """Flat, three tones per material, and the colours the owner chose."""
        self.assertEqual(palette_of(read_renderer()), HOUSE_PALETTE)

    def test_every_colour_is_flat(self):
        """No gradients in the palette, and only the shadow may be see-through."""
        for name, col in palette_of(read_renderer()).items():
            if name == "shadow":
                self.assertTrue(col.startswith("rgba("), col)
                continue
            self.assertRegex(col, r"^#[0-9a-fA-F]{6}$",
                             f"{name} is not a flat hex colour: {col}")


class TestThePixelGrid(unittest.TestCase):
    def test_nothing_is_smoothed(self):
        """The house style is chunky pixels. Smoothing is how it was lost."""
        src = read_renderer()
        self.assertNotIn("imageSmoothingEnabled=true", src,
                         "figures are being smoothed; the house style is pixelated")
        self.assertIn("image-rendering:pixelated", src)

    def test_a_sprite_is_forty_tiles_wide(self):
        """The figure sprite is a fixed box. A bigger one is a re-skin."""
        src = read_renderer()
        body = src.split("function figureSprite(")[-1].split("function ")[0]
        m = re.search(r"Math\.ceil\((\d+)\*sq\)", body)
        self.assertIsNotNone(m, "the figure sprite is no longer a fixed box")
        self.assertEqual(int(m.group(1)), 40,
                         "the sprite box changed; that is a change of house style")


class TestTheBody(unittest.TestCase):
    def test_an_adult_is_about_seven_and_a_half_heads(self):
        """The proportions are the brief: an adult is not a chibi."""
        src = read_renderer()
        head = numbers_in(src, "STAGE_HEAD")
        self.assertEqual(len(head), 5, "the stage table changed shape")
        adult_head = head[3]
        # the head radius in the figure's 32-unit space, and the body height
        m = re.search(r"var hr\s*=\s*([\d.]+)\*STAGE_HEAD", src)
        self.assertIsNotNone(m, "the head radius formula moved")
        radius = float(m.group(1)) * adult_head
        height = 32.0
        heads = height / (2 * radius)
        self.assertGreater(heads, 7.0,
                           f"an adult is only {heads:.1f} heads tall — that is a "
                           f"stylisation, not a body")
        self.assertLess(heads, 8.5,
                        f"an adult is {heads:.1f} heads tall — too stretched")

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


class TestTheMirror(unittest.TestCase):
    def test_the_mirror_is_identical(self):
        with open(RENDERER) as a, open(MIRROR) as b:
            self.assertEqual(a.read(), b.read(),
                             "web/index.html and docs/index.html have diverged")


if __name__ == "__main__":
    unittest.main()
