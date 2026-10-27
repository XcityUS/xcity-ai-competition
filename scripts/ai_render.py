#!/usr/bin/env python3
"""Turn the massing renders into rendered images with an image model, and record where every image came from.

    python scripts/ai_render.py submissions/<login>/<slug> prompts              # write renders/prompts.json
    python scripts/ai_render.py submissions/<login>/<slug> run --provider xcity  # XCITY Studio (recommended)
    python scripts/ai_render.py submissions/<login>/<slug> run --provider openai # your own OpenAI key
    python scripts/ai_render.py submissions/<login>/<slug> register media/A03-eye-day.jpg --view A03-eye-day \
        --model "ChatGPT image generation (web)"                                 # an image you made by hand

How it works. scripts/render_views.py draws each named view from the package's own geometry (renders/<view>.png).
That massing render is the control image: the model is asked to keep its camera, footprints, heights, streets and
trees, and to change only materials, light and life. Every output goes to media/ and is registered in
image_provenance.json with the model, the full prompt, the date and the control image it was made from, which is
what gate G8 checks. A rendered image illustrates the geometry; it is never evidence for a number.

Providers.
  xcity   XCITY Studio. Your XCITY account comes with a KWH balance; images are charged against it. Sign in once
          with:  python scripts/ai_render.py <pkg> login  (a browser page asks you to approve this computer; the
          credential is stored in ~/.xcity/credentials, never in the repository). The service address is
          published with the formal brief; until then this provider reports that it is not yet available.
  openai  OpenAI image editing with your own key in the OPENAI_API_KEY environment variable, at OpenAI's prices.
  manual  No API: prompts.json tells you which control image and prompt to give your image tool; save the result
          in media/ and register it with the register command.

Choosing is the entrant's decision. An agent must ask its human before spending money (AGENTS.md, checkpoint 2).
"""
import argparse
import base64
import datetime
import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc   # noqa: E402

STYLE = ("Photorealistic architectural visualisation of a new city in the arid Andean piedmont of San Juan province, "
         "Argentina: Monte desert with creosote and jarilla shrubs, warm ochre gravel ground, very clear dry air, "
         "strong sun, the Andes foothills faint on the western horizon. Natural colours, real materials, believable "
         "people of all ages, no science-fiction styling.")
KEEP = ("Use the attached image as an exact layout reference. Keep the camera position, lens and horizon exactly. "
        "Keep every building's footprint, height, position and number of floors, every street, square, canopy, tree "
        "and field where it is. Do not add or remove buildings, do not add towers, do not change the street pattern. "
        "Replace the plain massing materials with real ones and add light, texture and everyday life. No text, "
        "labels, logos, watermarks or borders.")
TIME = {"day": "Daylight, sun from the {dir} about {el} degrees up, crisp shadows.",
        "evening": "Early evening, low warm sun from the {dir}, long shadows, first lights coming on in windows and streets.",
        "night": "Night, warm street and window lights, deep blue sky with stars, people still out in the cool air."}
COMPASS = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
USE_WORDS = {"residential": "homes", "mixed_use": "homes over shops", "civic": "civic buildings",
             "compute": "data halls", "industry": "workshops", "logistics": "freight sheds",
             "infrastructure": "infrastructure", "agriculture": "greenhouses", "open_space": "shade structures"}


def scene_views(pkg):
    """Views from the scene file written by make_scene.py (same ids as renders/)."""
    p = os.path.join(pkg, "visual", "index.html")
    if not os.path.exists(p):
        raise SystemExit("no visual/index.html: run scripts/render_views.py first")
    t = open(p, encoding="utf-8").read()
    i = t.index("window.XCITY_SCENE=") + len("window.XCITY_SCENE=")
    d = json.loads(t[i:t.index(";</script>", i)])
    return d["views"], d["origin_utm"], d.get("suns", {})


def what_is_in_view(pkg, view, origin):
    """Names of the land uses and buildings around the view target, nearest first (at most 8)."""
    from shapely.geometry import Point
    geo = xc.load_geometry(pkg)
    tx, ty = view["target"][0] + origin[0], view["target"][1] + origin[1]
    px, py = view["pos"][0] + origin[0], view["pos"][1] + origin[1]
    eye = view["pos"][2] < 3
    reach = 90.0 if eye else max(150.0, math.hypot(tx - px, ty - py) * 0.6)
    t = Point(tx, ty)
    seen = []
    for layer in ("buildings", "land_use"):
        for p, g in geo[layer]:
            if p.get("use") == "reserve":
                continue
            gu = xc.to_utm(g)
            d = gu.distance(t)
            name = str(p.get("name") or USE_WORDS.get(p.get("use"), p.get("use") or "")).strip()
            if name and d < reach:
                seen.append((d, name))
    out = []
    for d, n in sorted(seen):
        n = n.split(" - ")[0] if len(n) > 70 else n
        if n not in out:
            out.append(n)
    return out[:8]


def build_prompts(pkg):
    man = xc.load_json(os.path.join(pkg, "manifest.json"))
    views, origin, suns = scene_views(pkg)
    stamp_p = os.path.join(pkg, "renders", "stamp.json")
    stamp = xc.load_json(stamp_p) if os.path.exists(stamp_p) else {"files": {}}
    nodes = {str(p.get("node_id")): p for p, g in xc.load_geometry(pkg)["nodes"]}
    out = []
    for v in views:
        ctl = "renders/%s.png" % v["id"]
        nid = v["id"].split("-")[0]
        node = nodes.get(nid, {})
        aerial = v["pos"][2] > 20
        parts = [STYLE]
        if node:
            parts.append("This is %s of '%s' (key node %s)." % ("an aerial view" if aerial else "an eye-level view at 1.6 m",
                                                               node.get("name", nid), nid))
        else:
            parts.append("This is %s of the scheme '%s'." % ("an aerial view" if aerial else "an eye-level view",
                                                              man.get("title", "")))
        seen = what_is_in_view(pkg, v, origin)
        if seen:
            parts.append("In view: " + "; ".join(seen) + ".")
        if node.get("render_note"):
            parts.append(node["render_note"])
        elif man.get("render_note"):
            parts.append(man["render_note"])
        if man.get("render_rules"):
            parts.append(man["render_rules"])
        sun = suns.get(v.get("time"), {})
        az = float(sun.get("azimuth", 300))
        parts.append(TIME.get(v.get("time"), TIME["day"]).format(dir=COMPASS[int((az + 22.5) % 360 // 45)],
                                                                  el=int(round(float(sun.get("elevation", 45)) / 5) * 5)))
        parts.append(KEEP)
        out.append({"view": v["id"], "label": v["label"], "node_id": nid if node else None,
                    "control_image": ctl, "control_sha256": stamp.get("files", {}).get(v["id"] + ".png", {}).get("sha256"),
                    "prompt": " ".join(parts)})
    xc.write_json(os.path.join(pkg, "renders", "prompts.json"),
                  {"note": "One prompt per massing render. Give the control image and the prompt to your image tool; "
                           "save the result in media/ and register it (scripts/ai_render.py register).",
                   "views": out})
    return out


def register(pkg, path, view, model, prompt=None, post="none", note=""):
    rel = os.path.relpath(os.path.abspath(path), pkg)
    if rel.startswith(".."):
        raise SystemExit("put the image inside the package, in media/")
    prompts = {p["view"]: p for p in build_prompts(pkg)} if prompt is None else {}
    pr = prompt or prompts.get(view, {}).get("prompt")
    if not pr:
        raise SystemExit("unknown view %s; see renders/prompts.json" % view)
    ip_p = os.path.join(pkg, "image_provenance.json")
    ip = xc.load_json(ip_p) if os.path.exists(ip_p) else {"images": []}
    ip["images"] = [im for im in ip.get("images", []) if im.get("path") != rel]
    nid = view.split("-")[0]
    kind = "aerial" if "aerial" in view else "eye_level" if "eye" in view else "other"
    ip["images"].append({
        "path": rel, "node_id": nid if nid in {n["id"] for n in xc.load_json(os.path.join(xc.ROOT, "brief/site-package/nodes/design_nodes.json"))["nodes"]} else None, "view": kind, "model": model, "prompt": pr,
        "generated_at": datetime.date.today().isoformat(), "post_processing": post, "post_processing_note": note,
        "reference_images": "own_work",
        "reference_images_note": "Control image renders/%s.png, drawn by scripts/render_views.py from this package's geometry." % view,
        "control_image": "renders/%s.png" % view,
        "caption": "Rendered from the massing view %s; illustrates the geometry, not evidence." % view})
    ip["images"].sort(key=lambda im: im["path"])
    xc.write_json(ip_p, ip)
    print("registered %s (control renders/%s.png)" % (rel, view))


def run_openai(pkg, items, size):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("set OPENAI_API_KEY in your environment (never in a file in this repository)")
    import uuid
    for it in items:
        ctl = os.path.join(pkg, it["control_image"])
        boundary = uuid.uuid4().hex
        body = []
        for k, v in (("model", "gpt-image-1"), ("prompt", it["prompt"]), ("size", size), ("n", "1")):
            body.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v)).encode())
        body.append(("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"control.png\"\r\n"
                     "Content-Type: image/png\r\n\r\n" % boundary).encode() + open(ctl, "rb").read() + b"\r\n")
        body.append(("--%s--\r\n" % boundary).encode())
        req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"".join(body),
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "multipart/form-data; boundary=" + boundary})
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.load(r)["data"][0]["b64_json"]
        out = os.path.join(pkg, "media", it["view"] + ".png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "wb").write(base64.b64decode(data))
        register(pkg, out, it["view"], "OpenAI gpt-image-1 (images/edits)", prompt=it["prompt"])


def run_xcity(pkg, items, size):
    api = os.environ.get("XCITY_STUDIO_API", "")
    cred = os.path.expanduser("~/.xcity/credentials")
    if not api:
        raise SystemExit("XCITY Studio is not yet open to agents: its address is published with the formal brief. "
                         "Until then use --provider openai or manual, or keep the massing renders - they already meet "
                         "the render requirement.")
    if not os.path.exists(cred):
        raise SystemExit("sign in first: python scripts/ai_render.py <package> login")
    raise SystemExit("XCITY Studio client: to be connected when the service address and interface are published.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package")
    ap.add_argument("command", choices=["prompts", "run", "register", "login"])
    ap.add_argument("image", nargs="?")
    ap.add_argument("--provider", choices=["xcity", "openai", "manual"], default="xcity")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--view")
    ap.add_argument("--model", default="")
    ap.add_argument("--post-processing", default="none", choices=["none", "retouch", "composite"])
    ap.add_argument("--size", default="1536x1024")
    a = ap.parse_args()
    pkg, _, _ = xc.find_package(a.package)
    if a.command == "prompts":
        items = build_prompts(pkg)
        print("wrote renders/prompts.json (%d views)" % len(items))
    elif a.command == "register":
        if not (a.image and a.view and a.model):
            raise SystemExit("register needs: the image path, --view <view id> and --model \"<model and version>\"")
        register(pkg, a.image, a.view, a.model, post=a.post_processing)
    elif a.command == "login":
        run_xcity(pkg, [], a.size)
    else:
        items = [it for it in build_prompts(pkg) if not a.only or it["view"] in a.only]
        if a.provider == "manual":
            print("prompts written to renders/prompts.json; make the images with your tool, save them in media/ and "
                  "register each one")
        elif a.provider == "openai":
            run_openai(pkg, items, a.size)
        else:
            run_xcity(pkg, items, a.size)


if __name__ == "__main__":
    main()
