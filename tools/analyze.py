#!/usr/bin/env python3
"""Analyze the Figma file JSON: homepage structure, typography, colors, effects, assets."""
import json, re, sys
from collections import Counter, defaultdict

d = json.load(open("/home/user/Serendipity/figma-export/file.json"))

def rgba(c):
    if not isinstance(c, dict): return None
    if c.get("type") == "SOLID":
        r,g,b,a = c.get("r",0), c.get("g",0), c.get("b",0), c.get("a",1)
        h = "#%02X%02X%02X" % (round(r*255), round(g*255), round(b*255))
        return h + ("" if a == 1 else f" @{round(a*100)}%")
    if c.get("type") in ("GRADIENT_LINEAR","GRADIENT_RADIAL","GRADIENT_ANGULAR"):
        stops = ",".join("#%02X%02X%02X@%d%%" % (round(s["color"]["r"]*255), round(s["color"]["g"]*255), round(s["color"]["b"]*255), round(s["position"]*100)) for s in c.get("gradientStops",[]))
        return f"{c['type']}({stops})"
    return None

def bbox(n):
    b = n.get("absoluteBoundingBox") or {}
    return (int(b.get("x",0)), int(b.get("y",0)), int(b.get("width",0)), int(b.get("height",0)))

def walk(n, fn, depth=0, maxdepth=999):
    fn(n, depth)
    if depth >= maxdepth: return
    for c in n.get("children", []):
        walk(c, fn, depth+1, maxdepth)

# ---------- locate frames ----------
frames = {}
for pg in d["document"]["children"]:
    for c in pg.get("children", []):
        frames[c["id"]] = c

print("### OTHER PAGES ###")
for pg in d["document"]["children"]:
    if pg["name"] == "Prototype": continue
    print(f"\n== {pg['name']} ==")
    for c in pg.get("children", []):
        x,y,w,h = bbox(c)
        print(f"  {c['id']:>12} {c['type']:<12} {w:>5}x{h:<6} {c['name'][:55]!r}")

hp = frames.get("247:1092")
if not hp:
    print("homepage frame not found"); sys.exit(1)

# ---------- homepage sections ----------
print("\n### HOMEPAGE 'home page' (247:1092) DIRECT CHILDREN (sections) ###")
for c in hp.get("children", []):
    x,y,w,h = bbox(c)
    print(f"  {c['id']:>12} {c['type']:<10} x={x:<6} y={y:<7} {w:>4}x{h:<6} {c['name'][:50]!r} children={len(c.get('children',[]))}")

# ---------- typography ----------
styles = defaultdict(list)   # key -> [text samples]
fonts = Counter()
colors = Counter()
gradients = []
effects = defaultdict(list)
imgfills = []   # (node name, id, imageRef, bbox)
componentUses = Counter()

def inspect(n, depth):
    if n.get("type") == "TEXT":
        st = n.get("style", {})
        fam = st.get("fontFamily","?"); fonts[(fam, st.get("fontStyle","?"))] += 1
        size = st.get("fontSize"); lh = st.get("lineHeightPx"); ls = st.get("letterSpacing")
        fill = None
        for f in n.get("fills", []) or []:
            fill = rgba(f); break
        key = (fam, st.get("fontStyle"), size, lh, ls, st.get("textAlignHorizontal"), st.get("textCase"), st.get("textDecoration"), fill)
        chars = n.get("characters","").replace("\n"," / ")[:70]
        styles[key].append(chars)
    if n.get("type") == "INSTANCE":
        cname = (n.get("componentId") or "?")[:10]
        componentUses[cname] += 1
    for f in (n.get("fills") or []) + (n.get("strokes") or []):
        v = rgba(f)
        if v:
            if isinstance(f, dict) and f.get("type") == "SOLID": colors[v] += 1
            else: gradients.append((v, n.get("name","")[:40]))
        if isinstance(f, dict) and f.get("type") == "IMAGE" and f.get("imageRef"):
            imgfills.append((n.get("name",""), n["id"], f["imageRef"], bbox(n), round(f.get("scaleMode","?")=="FILL"), f.get("imageTransform")))
    for e in n.get("effects", []) or []:
        desc = f"{e.get('type')} blur={e.get('radius')}"
        if e.get("offset"): desc += f" off=({e['offset']['x']},{e['offset']['y']})"
        if e.get("color"): desc += " " + str(rgba(e["color"]))
        if e.get("spread"): desc += f" spread={e['spread']}"
        effects[desc].append(n.get("name","")[:30])

walk(hp, inspect)
# also reservation flow frames
for rid in ("736:1531","740:4330","767:5221"):
    if rid in frames: walk(frames[rid], inspect)

print("\n### FONTS USED ###")
for (fam, style), cnt in fonts.most_common():
    print(f"  {fam!r} [{style}] x{cnt}")

print("\n### TYPE STYLES (dedup) ###")
for key, samples in sorted(styles.items(), key=lambda kv: -(kv[0][2] or 0)):
    fam, style, size, lh, ls, align, tcase, tdec, fill = key
    print(f"  {fam} {style} {size}px lh={lh} ls={ls} align={align} case={tcase} dec={tdec} color={fill}  e.g. {samples[0][:48]!r} ({len(samples)}x)")

print("\n### SOLID COLORS ###")
for col, cnt in colors.most_common(40):
    print(f"  {col} x{cnt}")

print("\n### GRADIENTS (unique) ###")
seen = set()
for g, nm in gradients:
    if g not in seen:
        seen.add(g)
        print(f"  {g}   ({nm})")

print("\n### EFFECTS ###")
for desc, names in effects.items():
    print(f"  {desc}  x{len(names)} e.g. {names[:3]}")

print("\n### IMAGE FILLS (assets) ###")
print("  count:", len(imgfills))
for nm, nid, ref, bb, _s, it in imgfills[:60]:
    print(f"  {nid:>12} ref={ref[:12]:<13} {bb[2]:>4}x{bb[3]:<5} {nm[:40]!r} transform={bool(it)}")

# save the analysis
out = {
    "imageFills": [{"name": nm, "id": nid, "ref": ref, "bbox": bb} for nm, nid, ref, bb, s, it in imgfills],
    "typeStyles": [{"key": list(k), "count": len(v), "sample": v[0]} for k, v in styles.items()],
    "colors": dict(colors),
}
json.dump(out, open("/home/user/Serendipity/figma-export/analysis.json", "w"), indent=1)
print("\nsaved analysis.json")
