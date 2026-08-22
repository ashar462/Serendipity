#!/usr/bin/env python3
"""Build manifest.json for the focused render pass (frames + section crops + assets)."""
import json, os

d = json.load(open("/home/user/Serendipity/figma-export/file.json"))
analysis = json.load(open("/home/user/Serendipity/figma-export/analysis.json"))

frames = {}
for pg in d["document"]["children"]:
    for c in pg.get("children", []):
        frames[c["id"]] = c

def safe(n):
    s = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in n)[:80]
    return s or "unnamed"

def bb(n):
    b = n.get("absoluteBoundingBox") or {}
    return int(b.get("width", 0)), int(b.get("height", 0))

items = []

def add(nid, scale, path):
    items.append({"nid": nid, "scale": scale, "path": path})

def smart(n, folder):
    w, h = bb(n)
    px = w * scale * h * scale if False else w * h * 4  # @2x pixels
    scale = 2 if px < 40_000_000 else 1
    add(n["id"], scale, f"renders/{folder}/{n['id'].replace(':', '-')}_{safe(n['name'])}@{scale}x.png")

# 1) full homepage @1x (9421px tall -> 2x too big)
add("247:1092", 1, "renders/homepage/__home-full@1x.png")

# 2) homepage sections (direct children)
hp = frames["247:1092"]
for c in hp.get("children", []):
    smart(c, "homepage")

# 3) reservation flow: full @1x + sections @2x
for rid, nm in (("736:1531", "reservation"), ("740:4330", "payment"), ("767:5221", "confirmed")):
    fr = frames.get(rid)
    if not fr: continue
    add(rid, 1, f"renders/{nm}/__{nm}-full@1x.png")
    for c in fr.get("children", []):
        w, h = bb(c)
        if w * h < 20000:  # skip tiny lines/icons at section level
            continue
        smart(c, nm)

# 4) asset image-fill nodes @2x (homepage + reservation)
for a in analysis["imageFills"]:
    nid = a["id"].split(";")[-1]  # instance path -> actual node id
    w, h = a["bbox"][2], a["bbox"][3]
    if w * 4 * h * 4 > 40_000_000:
        add(nid, 2, f"renders/assets/{nid.replace(':', '-')}-{safe(a['name'])}@2x.png")

# de-dup by path
seen = set(); out = []
for it in items:
    if it["path"] in seen: continue
    seen.add(it["path"]); out.append(it)

os.makedirs("/home/user/Serendipity/figma-export/renders", exist_ok=True)
json.dump({"items": out}, open("/home/user/Serendipity/figma-export/manifest.json", "w"), indent=1)
print(f"manifest: {len(out)} render items")
for it in out[:12]: print(" ", it["nid"], it["scale"], it["path"])
print("  ...")
