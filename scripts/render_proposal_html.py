#!/usr/bin/env python3
"""Render proposal.md as report/proposal.html - one offline page, no network requests.

    python scripts/render_proposal_html.py submissions/<github-login>/<proposal-slug>

Images keep their relative paths (figures/..., media/...), rewritten so they resolve from report/.
The page records the sha256 of proposal.md; GATE-G1 fails if proposal.md changed after rendering.
"""
import argparse
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc  # noqa: E402

CSS = """
:root{--paper:#F7F5F0;--ink:#1E1D1B;--muted:#7A756C;--gold:#B08F45;--line:#DAD5CB}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",
"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:980px;margin:0 auto;padding:40px 24px 80px}
header .eyebrow{color:var(--gold);font-size:12px;letter-spacing:.12em;font-weight:700;text-transform:uppercase}
header h1{font-size:34px;line-height:1.2;margin:.3em 0 .2em}
header .meta{color:var(--muted);font-size:13px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);
padding:10px 0;margin:16px 0 28px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:4px 18px}
h1,h2,h3{font-weight:700}
h2{font-size:24px;margin:2.2em 0 .6em;padding-top:.6em;border-top:1px solid var(--line)}
h3{font-size:18px;margin:1.6em 0 .4em}
img{max-width:100%;height:auto;display:block;margin:14px 0;border:1px solid var(--line);background:#fff}
table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:#ECE6D8}
code{background:#ECE6D8;padding:1px 4px;border-radius:3px;font-size:.92em}
pre{background:#ECE6D8;padding:12px;overflow:auto}
blockquote{margin:1em 0;padding:.2em 1em;border-left:3px solid var(--gold);color:var(--muted)}
nav.toc{font-size:14px;columns:2;margin:0 0 24px}
nav.toc a{color:var(--ink);text-decoration:none}
footer{color:var(--muted);font-size:12px;margin-top:48px;border-top:1px solid var(--line);padding-top:10px}
"""


def md_to_html(text):
    try:
        import markdown  # noqa: WPS433
        return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc"])
    except ImportError:
        return "<pre>%s</pre>" % html.escape(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package")
    a = ap.parse_args()
    pkg, login, slug = xc.find_package(a.package)
    src = os.path.join(pkg, "proposal.md")
    text = open(src, encoding="utf-8").read()
    man = xc.load_json(os.path.join(pkg, "manifest.json"))
    body = md_to_html(text)
    # resolve package-relative paths from report/
    body = re.sub(r'(src|href)="(?!https?:|#|mailto:|/|\.\./)([^"]+)"', r'\1="../\2"', body)
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    toc = "".join('<div><a href="#%s">%s</a></div>' % (i, re.sub("<[^>]+>", "", t)) for i, t in heads)
    au, ag = man.get("author", {}), man.get("agent", {})
    meta = "".join("<div><b>%s</b> %s</div>" % (k, html.escape(str(v))) for k, v in [
        ("Package", "submissions/%s/%s" % (login, slug)),
        ("Responsible", au.get("responsible_party", "")),
        ("Agent", "%s · %s" % (ag.get("name", ""), ag.get("model", ""))),
        ("Autonomy", man.get("autonomy", {}).get("class", "")),
        ("Nodes", ", ".join(man.get("nodes", []))),
        ("Updated", man.get("updated", "")),
    ])
    downloads = '<nav aria-label="Submission documents"><a href="../drawings/a3-booklet.pdf">Public presentation</a>'
    if os.path.isfile(os.path.join(pkg, "drawings", "a3-technical-appendix.pdf")):
        downloads += ' · <a href="../drawings/a3-technical-appendix.pdf">Technical appendix</a>'
    downloads += '</nav>'
    body = downloads + body
    doc = ("<!doctype html><html lang=\"%s\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
           "<meta name=\"xcity-source-sha256\" content=\"%s\">"
           "<title>%s · XCITY AI Competition</title><style>%s</style></head><body><main>"
           "<header><div class=\"eyebrow\">XCITY AI Competition · San Juan, 1,656 km²</div>"
           "<h1>%s</h1><div class=\"meta\">%s</div></header><nav class=\"toc\">%s</nav>%s"
           "<footer>Rendered from proposal.md by scripts/render_proposal_html.py v%s. Offline: this page loads "
           "nothing from the network.</footer></main></body></html>") % (
        html.escape(man.get("language", "en")), xc.sha256_file(src), html.escape(man.get("title", slug)), CSS,
        html.escape(man.get("title", slug)), meta, toc, body, xc.SCRIPT_VERSION)
    # the H1 in proposal.md duplicates the header
    doc = re.sub(r"(</nav>)\s*<h1[^>]*>.*?</h1>", r"\1", doc, count=1, flags=re.S)
    os.makedirs(os.path.join(pkg, "report"), exist_ok=True)
    out = os.path.join(pkg, "report", "proposal.html")
    open(out, "w", encoding="utf-8").write(doc)
    print("wrote %s" % os.path.relpath(out, xc.ROOT))


if __name__ == "__main__":
    main()
