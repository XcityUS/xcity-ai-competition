#!/usr/bin/env python3
"""Render the named views of a submission's 3D scene to PNG files.

    python scripts/render_views.py submissions/<github-login>/<proposal-slug> [--width 2400 --height 1500] [--only ID ...]

Builds visual/index.html first if it is missing or out of date (scripts/make_scene.py), opens it in headless
Chromium (Playwright, software WebGL, no GPU needed) and writes renders/<view-id>.png plus renders/stamp.json.
The stamp records the package input hash, so the self-check can tell when renders are stale.

Needs: pip install playwright && python -m playwright install chromium
"""
import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
        "--enable-webgl", "--disable-gpu-sandbox"]


def scene_is_current(pkg, h):
    p = os.path.join(pkg, "visual", "index.html")
    if not os.path.exists(p):
        return False
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    return ('"input_sha256":"%s"' % h) in txt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package")
    ap.add_argument("--width", type=int, default=2400)
    ap.add_argument("--height", type=int, default=1500)
    ap.add_argument("--only", nargs="*", help="render only these view ids")
    a = ap.parse_args()
    pkg, _, _ = xc.find_package(a.package)
    h = xc.scene_input_hash(pkg)
    if not scene_is_current(pkg, h):
        subprocess.check_call([sys.executable, os.path.join(HERE, "make_scene.py"), pkg])
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("render_views.py needs Playwright: pip install playwright && python -m playwright install chromium")
    out = os.path.join(pkg, "renders")
    os.makedirs(out, exist_ok=True)
    url = "file://" + os.path.join(pkg, "visual", "index.html") + "?render"
    stamp_p = os.path.join(out, "stamp.json")
    old = xc.load_json(stamp_p) if os.path.exists(stamp_p) else {}
    files = dict(old.get("files", {})) if a.only and old.get("input_sha256") == h else {}
    with sync_playwright() as p:
        br = p.chromium.launch(args=ARGS)
        pg = br.new_page(viewport={"width": 1200, "height": 750})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_function("window.XC_READY === true", timeout=240000)
        if errs:
            raise SystemExit("scene error: " + errs[0])
        views = pg.evaluate("XC.views.map(v => ({id: v.id, label: v.label, time: v.time}))")
        for v in views:
            if a.only and v["id"] not in a.only:
                continue
            t0 = time.time()
            data = pg.evaluate("([id, w, h]) => XC.render(id, w, h)", [v["id"], a.width, a.height])
            png = base64.b64decode(data.split(",", 1)[1])
            fn = v["id"] + ".png"
            with open(os.path.join(out, fn), "wb") as f:
                f.write(png)
                f.flush()
                os.fsync(f.fileno())
            if xc.sha256_file(os.path.join(out, fn)) != hashlib.sha256(png).hexdigest():
                raise SystemExit("renders/%s did not write back intact - check the disk and run again" % fn)
            files[fn] = {"sha256": hashlib.sha256(png).hexdigest(), "label": v["label"], "time": v["time"]}
            print("  %-24s %5.1f s  %d KB" % (fn, time.time() - t0, len(png) // 1024))
        br.close()
    xc.write_json(stamp_p, {"input_sha256": h, "width": a.width, "height": a.height,
                            "generator": "scripts/render_views.py " + xc.SCRIPT_VERSION, "files": files})
    print("renders in %s (%d views)" % (os.path.relpath(out, xc.ROOT), len(files)))


if __name__ == "__main__":
    main()
