#!/usr/bin/env python3
"""Export a Figma file (JSON + rendered frames + image assets) for offline analysis.

Env:
  FIGMA_TOKEN  personal access token
  FILE_KEY     figma file key
  OUT_DIR      output directory (default: figma-export)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

TOKEN = os.environ["FIGMA_TOKEN"]
FILE_KEY = os.environ.get("FILE_KEY", "BO6GAA0KF1Q0W9SzpfcZym")
OUT = os.environ.get("OUT_DIR", "figma-export")
API = "https://api.figma.com/v1"


def api_get(path, retries=5):
    url = f"{API}{path}"
    last = None
    for i in range(retries):
        req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            last = e
            wait = 2 ** i
            print(f"  retry {i+1}/{retries} after error: {e} (sleep {wait}s)", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"GET failed: {url}: {last}")


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "figma-export/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:120]


def fetch_images(ids, scale, fmt="png"):
    """Call the image render endpoint in batches; returns {node_id: url}."""
    out = {}
    ids = list(ids)
    B = 30
    for i in range(0, len(ids), B):
        batch = ids[i : i + B]
        q = urllib.parse.urlencode({"ids": ",".join(batch), "format": fmt, "scale": scale})
        data = api_get(f"/files/{FILE_KEY}/images?{q}")
        if data.get("err"):
            print(f"  image batch error: {data['err']}", flush=True)
        out.update(data.get("images", {}))
        time.sleep(0.6)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    print("== file (depth=2) ==", flush=True)
    shallow = api_get(f"/files/{FILE_KEY}?depth=2")
    with open(f"{OUT}/file-depth2.json", "w") as f:
        json.dump(shallow, f)

    pages = shallow["document"]["children"]
    print("Pages:")
    frames = []  # (page_name, frame)
    for pg in pages:
        print(f"  - {pg['name']} ({pg.get('type')})")
        for child in pg.get("children", []):
            print(f"      * {child['name']} [{child['type']}] id={child['id']}")
            frames.append((pg["name"], child))

    print("== full file ==", flush=True)
    full = api_get(f"/files/{FILE_KEY}")
    with open(f"{OUT}/file.json", "w") as f:
        json.dump(full, f)
    print(f"  file.json bytes: {os.path.getsize(f'{OUT}/file.json')}", flush=True)

    # specific node dumps referenced in the brief
    for nid in ["247-1092", "947-3137"]:
        try:
            nd = api_get(f"/files/{FILE_KEY}/nodes?id={nid}")
            with open(f"{OUT}/node-{nid.replace(':', '-')}.json", "w") as f:
                json.dump(nd, f)
            print(f"  dumped node {nid}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  node {nid} failed: {e}", flush=True)

    # ---- render every top-level frame at 1x ----
    print("== render frames @1x ==", flush=True)
    by_id = {c["id"]: (pn, c) for pn, c in frames}
    urls = fetch_images(list(by_id.keys()), 1)
    for nid, url in urls.items():
        if not url:
            continue
        pn, node = by_id[nid]
        dest = f"{OUT}/frames/{safe(pn)}/{safe(node['name'])}_{nid.replace(':', '-')}.png"
        try:
            download(url, dest)
        except Exception as e:  # noqa: BLE001
            print(f"  dl fail {nid}: {e}", flush=True)
    print(f"  rendered {len([u for u in urls.values() if u])} frames", flush=True)

    # ---- 2x renders for frames that look like homepage / reservation ----
    key_words = ("home", "reservation", "booking", "reserve")
    key_ids = {
        nid: (pn, node)
        for nid, (pn, node) in by_id.items()
        if any(k in node["name"].lower() for k in key_words)
    }
    if key_ids:
        print(f"== render key frames @2x ({len(key_ids)}) ==", flush=True)
        urls2 = fetch_images(list(key_ids.keys()), 2)
        for nid, url in urls2.items():
            if not url:
                continue
            pn, node = key_ids[nid]
            dest = f"{OUT}/frames-2x/{safe(pn)}/{safe(node['name'])}_{nid.replace(':', '-')}.png"
            try:
                download(url, dest)
            except Exception as e:  # noqa: BLE001
                print(f"  dl fail {nid}: {e}", flush=True)

    # ---- collect nodes that contain image fills ----
    image_fill_ids = []

    def walk(n):
        for fill in n.get("fills", []) or []:
            if fill.get("type") == "IMAGE" and fill.get("imageRef"):
                image_fill_ids.append(n["id"])
                break
        for c in n.get("children", []):
            walk(c)

    walk(full["document"])
    image_fill_ids = list(dict.fromkeys(image_fill_ids))[:300]
    print(f"== render {len(image_fill_ids)} image-fill nodes @2x ==", flush=True)
    if image_fill_ids:
        au = fetch_images(image_fill_ids, 2)
        for nid, url in au.items():
            if not url:
                continue
            dest = f"{OUT}/asset-nodes/{nid.replace(':', '-')}.png"
            try:
                download(url, dest)
            except Exception as e:  # noqa: BLE001
                print(f"  dl fail {nid}: {e}", flush=True)

    # ---- original image refs ----
    try:
        imgs = api_get(f"/files/{FILE_KEY}/images")
        with open(f"{OUT}/image-refs.json", "w") as f:
            json.dump(imgs, f)
        for ref, url in imgs.get("meta", {}).items():
            ext = "png"
            dest = f"{OUT}/asset-originals/{ref}.{ext}"
            try:
                download(url, dest)
            except Exception as e:  # noqa: BLE001
                print(f"  dl fail ref {ref}: {e}", flush=True)
        print(f"  downloaded {len(imgs.get('meta', {}))} original images", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  image refs failed: {e}", flush=True)

    print("DONE", flush=True)


if __name__ == "__main__":
    sys.exit(main())
