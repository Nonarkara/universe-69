"""What GitHub Pages is allowed to publish from docs/.

Pages builds /docs on main with Jekyll. docs/audits is the evidence archive
(screenshots, fixtures, logs). The viewer does not request it, but with no
exclude list it is copied into the github-pages artifact and the deploy job
times out while syncing those files. This pins the exclude list and checks
that every asset the live pages actually reference is still inside the
published set.
"""

import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
CONFIG = os.path.join(DOCS, "_config.yml")

# Jekyll 3.10 defaults, plus CNAME, which github-pages adds only when the
# default exclude list is left untouched. Repeated in docs/_config.yml.
REQUIRED_EXCLUDES = (
    "audits",
    "CNAME",
    "Gemfile",
    "Gemfile.lock",
    "node_modules",
    "vendor/bundle/",
    "vendor/cache/",
    "vendor/gems/",
    "vendor/ruby/",
)

ASSET_EXT = (
    "html", "js", "css", "json", "png", "jpg", "jpeg", "gif", "svg",
    "woff2", "glb", "txt", "md", "webp",
)
QUOTED_ASSET = re.compile(
    r"""(?P<q>['"])(?P<p>(?:\./|\.\./)?(?:[\w.+-]+/)*[\w.+-]+\."""
    + "(?:" + "|".join(ASSET_EXT) + r"))(?P=q)"
)
ATTR_REF = re.compile(
    r"""(?:src|href)\s*=\s*(?P<q>['"])(?P<p>.*?)(?P=q)""",
    re.I,
)
CSS_URL = re.compile(r"""url\(\s*(?P<q>['"]?)(?P<p>[^)'"]+)(?P=q)\s*\)""", re.I)
IMPORT_FROM = re.compile(
    r"""(?:import\s+(?:[^'"]+?\s+from\s+)?|export\s+.+?\s+from\s+)(?P<q>['"])(?P<p>.+?)(?P=q)"""
)
GET_LITERAL = re.compile(r"""(?:get|light)\(\s*['"]([^'"]+)['"]\s*\)""")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_exclude(text):
    """The exclude list of our flat _config.yml. No other YAML is read."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^exclude:\s*$", line):
            start = i + 1
            break
    if start is None:
        return []
    items = []
    for line in lines[start:]:
        if not line.strip():
            continue
        m = re.match(r"^  - (.+?)\s*$", line)
        if not m:
            break
        items.append(m.group(1).strip().strip("'\""))
    return items


def excluded(rel, patterns):
    rel = rel.replace("\\", "/")
    for raw in patterns:
        pat = raw.strip().strip("/")
        if not pat:
            continue
        if rel == pat or rel.startswith(pat + "/"):
            return True
    return False


def published_files(patterns):
    """Files Jekyll will consider, before markdown rendering.

    Jekyll drops names that start with '.', '_', '#' or '~', and names that
    end with '~', unless include forces them back. We do not include any.
    """
    out = {}
    for dirpath, dirnames, filenames in os.walk(DOCS):
        rel_dir = os.path.relpath(dirpath, DOCS).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""
        kept_dirs = []
        for name in dirnames:
            rel = name if not rel_dir else rel_dir + "/" + name
            if name[:1] in "._#~" or name.endswith("~") or excluded(rel, patterns):
                continue
            kept_dirs.append(name)
        dirnames[:] = kept_dirs
        for name in filenames:
            rel = name if not rel_dir else rel_dir + "/" + name
            if name[:1] in "._#~" or name.endswith("~") or excluded(rel, patterns):
                continue
            out[rel] = os.path.getsize(os.path.join(dirpath, name))
    return out


def _is_local_asset(ref):
    if not ref or ref.startswith(("#", "//")):
        return False
    lower = ref.lower()
    if lower.startswith(("http:", "https:", "data:", "mailto:", "javascript:")):
        return False
    if ref.startswith("/"):
        return False
    return True


def _normalize(base_dir, ref):
    ref = ref.split("#", 1)[0].split("?", 1)[0].strip()
    if not _is_local_asset(ref):
        return None
    parts = []
    for part in (base_dir + "/" + ref).split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    path = "/".join(parts)
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if ext not in ASSET_EXT:
        return None
    return path


def references_from(rel, text):
    """Local asset paths referenced by one published file."""
    base = rel.rsplit("/", 1)[0] if "/" in rel else ""
    found = set()

    def add(ref, base_dir=None):
        path = _normalize(base if base_dir is None else base_dir, ref)
        if path:
            found.add(path)

    if rel.endswith("three.module.min.js"):
        return found

    vendored = rel.startswith("addons/")
    if not vendored:
        for m in ATTR_REF.finditer(text):
            add(m.group("p"))
        for m in CSS_URL.finditer(text):
            add(m.group("p"))
        # humans.js loads bodies from ./humans/, not from beside the module.
        asset_base = "humans" if rel == "humans.js" else None
        for m in QUOTED_ASSET.finditer(text):
            ref = m.group("p")
            if asset_base and "/" not in ref and not ref.startswith("."):
                add(ref, asset_base)
            else:
                add(ref)
        if rel == "humans.js":
            hair = re.search(
                r"const HAIR = \{[^}]*0:\s*\[([^\]]*)\][^}]*1:\s*\[([^\]]*)\]",
                text)
            names = re.findall(r"'([^']+)'", hair.group(0)) if hair else []
            if re.search(r"HAIR_FILES = \[.*?'beard'\]", text):
                names.append("beard")
            for name in names:
                add("hair_" + name + ".glb", "humans")
            for m in GET_LITERAL.finditer(text):
                add(m.group(1), "humans")

    for m in IMPORT_FROM.finditer(text):
        add(m.group("p"))
    # import maps are JSON inside the page, not ES import statements.
    for m in re.finditer(r'"imports"\s*:\s*\{([^}]*)\}', text):
        for spec in re.findall(r':\s*"([^"]+)"', m.group(1)):
            add(spec)
    return found


def reachable(files):
    """Follow the pages a visitor can open, then the assets those pages load."""
    seeds = [
        "index.html", "vr.html", "book/print.html", "humans/study.html",
        "config.js",
    ]
    seen = set()
    missing = []
    queue = list(seeds)
    while queue:
        rel = queue.pop()
        if rel in seen:
            continue
        seen.add(rel)
        if rel not in files:
            missing.append(rel)
            continue
        ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        if ext not in ("html", "js", "css", "json", "md", "txt", "svg"):
            continue
        text = read(os.path.join(DOCS, rel))
        refs = references_from(rel, text)
        if rel.endswith(".json"):
            refs |= json_asset_refs(rel, text)
        for ref in sorted(refs):
            if ref not in seen:
                queue.append(ref)
    return seen, missing


def json_asset_refs(rel, text):
    base = rel.rsplit("/", 1)[0] if "/" in rel else ""
    found = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("src", "href", "url") and isinstance(value, str):
                    path = _normalize(base, value)
                    if path:
                        found.add(path)
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(json.loads(text))
    return found


class TestPagesPublishSet(unittest.TestCase):
    def test_exclude_keeps_the_audit_archive_out_of_the_site(self):
        text = read(CONFIG)
        # These keys would override what GitHub Pages sets for a project site.
        for key in ("baseurl", "theme", "url", "source", "destination"):
            self.assertIsNone(
                re.search(rf"(?m)^{key}\s*:", text),
                f"{key} must stay unset so Pages keeps its own value")
        patterns = parse_exclude(text)
        for item in REQUIRED_EXCLUDES:
            self.assertIn(item, patterns)
        files = published_files(patterns)
        leaked = [p for p in files if p == "audits" or p.startswith("audits/")]
        self.assertEqual(leaked, [])
        self.assertIn("index.html", files)
        self.assertIn("vr.html", files)
        self.assertIn("book/print.html", files)
        self.assertIn("humans/study.html", files)
        self.assertNotIn("_config.yml", files)
        # The archive stays in the repo. Publishing is what changes.
        self.assertTrue(os.path.isdir(os.path.join(DOCS, "audits")))
        self.assertTrue(os.path.isfile(
            os.path.join(DOCS, "audits", "2026-11-03", "README.md")))
        published = sum(files.values())
        self.assertLess(
            published, 80 * 1024 * 1024,
            "the published tree grew past the viewer; an archive may have "
            "escaped the exclude list")

    def test_every_referenced_asset_is_in_the_published_set(self):
        files = published_files(parse_exclude(read(CONFIG)))
        seen, missing = reachable(files)
        self.assertEqual(missing, [], "live pages reference missing files")
        for required in (
            "book/book.json", "book/origin.json", "archive/archive.json",
            "fonts/Jost-latin-variable.woff2",
            "fonts/SourceSerif4-latin-normal-variable.woff2",
            "fonts/SourceSerif4-latin-italic-variable.woff2",
            "three.module.min.js", "humans.js",
            "humans/male.glb", "humans/female.glb", "humans/anims.glb",
            "humans/male_light.jpg", "humans/female_light.jpg",
            "addons/GLTFLoader.js", "addons/SkeletonUtils.js",
            "addons/BufferGeometryUtils.js",
        ):
            self.assertIn(required, seen)
        self.assertGreater(len(seen), 40)


if __name__ == "__main__":
    unittest.main()
