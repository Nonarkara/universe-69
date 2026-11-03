"""Pack the CC0 Quaternius humans into small GLBs for the headset viewer.

Workbench tool, run once when the assets change; the viewer only reads its
output in web/humans/. Standard library plus macOS `sips` for resizing.

    python3 tools/build_humans.py /path/to/u69vr

where the folder holds the unzipped "Universal Base Characters[Standard]"
(under ubc/) and "Universal Animation Library[Standard]" (under ual/).
"""
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "humans")
TEX = 1024          # texture edge for a body seen from 0.5 m in a headset
JPEG_Q = 85

# One clip per activity family; everything else in the library is dropped.
CLIPS = ["Idle_Loop", "Walk_Loop", "Jog_Fwd_Loop", "Sprint_Loop", "Crouch_Idle_Loop",
         "Fixing_Kneeling", "PickUp_Table", "Idle_Talking_Loop", "Punch_Jab",
         "Dance_Loop", "Sitting_Idle_Loop", "Sitting_Talking_Loop"]

HAIR = ["Hair_SimpleParted", "Hair_Buzzed", "Hair_Beard",
        "Hair_Long", "Hair_Buns", "Hair_BuzzedFemale"]


def read_glb(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    o = 20 + n
    m = struct.unpack("<I", b[o:o + 4])[0]
    return j, b[o + 8:o + 8 + m]


def write_glb(path, j, binary):
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(js) + 8 + len(binary)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<I", len(js)) + b"JSON" + js)
        f.write(struct.pack("<I", len(binary)) + b"BIN\0" + binary)


def jpeg(src, edge=TEX):
    """Resize to `edge` and re-encode as JPEG; returns the bytes."""
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, "t.jpg")
        subprocess.run(["sips", "-Z", str(edge), "-s", "format", "jpeg",
                        "-s", "formatOptions", str(JPEG_Q), src, "--out", dst],
                       check=True, capture_output=True)
        return open(dst, "rb").read()
    finally:
        shutil.rmtree(tmp)


def append_view(j, blob, data):
    blob += b"\0" * (-len(blob) % 4)
    j.setdefault("bufferViews", []).append(
        {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
    return blob + data, len(j["bufferViews"]) - 1


def embed_gltf(gltf_path, image_files, out_path):
    """A .gltf + .bin + textures becomes one GLB with JPEG textures."""
    j = json.load(open(gltf_path))
    folder = os.path.dirname(gltf_path)
    blob = open(os.path.join(folder, j["buffers"][0]["uri"]), "rb").read()
    for img in j.get("images", []):
        src = image_files.get(img["uri"], os.path.join(folder, img["uri"]))
        edge = 256 if "Eye" in img["uri"] else TEX
        blob, view = append_view(j, blob, jpeg(src, edge))
        img.clear()
        img.update({"bufferView": view, "mimeType": "image/jpeg"})
    j["buffers"] = [{"byteLength": len(blob) + (-len(blob) % 4)}]
    write_glb(out_path, j, blob)


def accessor_bytes(j, blob, i):
    a = j["accessors"][i]
    v = j["bufferViews"][a["bufferView"]]
    comps = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
    size = {5126: 4, 5123: 2, 5125: 4, 5121: 1}[a["componentType"]] * comps
    assert not v.get("byteStride") or v["byteStride"] == size
    start = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    return blob[start:start + size * a["count"]]


def animations(glb_path, out_path):
    """Keep the skeleton and the chosen clips; drop the mannequin mesh."""
    j, blob = read_glb(glb_path)
    keep = [a for a in j["animations"] if a["name"] in CLIPS]
    missing = set(CLIPS) - {a["name"] for a in keep}
    assert not missing, missing
    out = {"asset": j["asset"], "scene": 0, "scenes": j["scenes"],
           "nodes": [{k: v for k, v in n.items() if k not in ("mesh", "skin")}
                     for n in j["nodes"]],
           "accessors": [], "bufferViews": [], "animations": []}
    data, remap = b"", {}

    def copy(i):
        nonlocal data
        if i not in remap:
            a = dict(j["accessors"][i])
            data, view = append_view(out, data, accessor_bytes(j, blob, i))
            a["bufferView"] = view
            a.pop("byteOffset", None)
            out["accessors"].append(a)
            remap[i] = len(out["accessors"]) - 1
        return remap[i]

    for anim in keep:
        samplers = [{**s, "input": copy(s["input"]), "output": copy(s["output"])}
                    for s in anim["samplers"]]
        out["animations"].append({"name": anim["name"], "samplers": samplers,
                                  "channels": anim["channels"]})
    out["buffers"] = [{"byteLength": len(data) + (-len(data) % 4)}]
    write_glb(out_path, out, data)


def main(root):
    ubc = os.path.join(root, "ubc", "Universal Base Characters[Standard]")
    ual = os.path.join(root, "ual", "Universal Animation Library[Standard]")
    body = os.path.join(ubc, "Base Characters", "Godot - UE")
    tex = os.path.join(ubc, "Base Characters", "Textures")
    gl_normals = os.path.join(tex, "Normals Unity - Godot")   # OpenGL +Y, as glTF wants
    os.makedirs(OUT, exist_ok=True)
    for sex in ("Male", "Female"):
        fixes = {f"T_Superhero_{sex}_Normal.png": os.path.join(gl_normals, f"T_Superhero_{sex}_Normal.png"),
                 "T_Eye_Normal_png.png": os.path.join(gl_normals, "T_Eye_Normal.png"),
                 "T_Hair_1_Normal_png.png": os.path.join(gl_normals, "T_Hair_1_Normal.png"),
                 "T_Hair_2_Normal_png.png": os.path.join(gl_normals, "T_Hair_2_Normal.png")}
        embed_gltf(os.path.join(body, f"Superhero_{sex}_FullBody.gltf"), fixes,
                   os.path.join(OUT, f"{sex.lower()}.glb"))
    # The lighter skin ships beside the body; the viewer picks per person.
    light = {"male": "T_Superhero_Male_Ligh.png", "female": "T_Superhero_Female_Light_BaseColor.png"}
    for sex, name in light.items():
        open(os.path.join(OUT, f"{sex}_light.jpg"), "wb").write(jpeg(os.path.join(tex, name)))
    hair_dir = os.path.join(ubc, "Hairstyles", "Origin at 0", "glTF (Godot)")
    hair_normals = os.path.join(ubc, "Hairstyles", "Textures", "Normals Unity - Godot")
    for h in HAIR:
        embed_gltf(os.path.join(hair_dir, h + ".gltf"),
                   {f"T_Hair_{i}_Normal.png": os.path.join(hair_normals, f"T_Hair_{i}_Normal.png")
                    for i in (1, 2)},
                   os.path.join(OUT, f"hair_{h[5:].lower()}.glb"))
    animations(os.path.join(ual, "Unreal-Godot", "UAL1_Standard.glb"),
               os.path.join(OUT, "anims.glb"))
    for f in sorted(os.listdir(OUT)):
        print(f"{os.path.getsize(os.path.join(OUT, f)) / 1024:8.0f} KB  {f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/Volumes/Data/agent-scratch/u69vr")
