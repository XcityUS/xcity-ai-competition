#!/usr/bin/env python3
"""Pages the agent drew for its own booklet (manifest.booklet.pages): here, the identity page for agent task 1.

    python submissions/EXAMPLE-agent/sample-scheme/tools/make_pages.py

Writes pages/identity.png. make_figures.py places it in the A3 booklet after the idea page.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch   # noqa: E402

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCHRE, GREEN, SLATE, INK, PAPER, MUTED = "#C9A15C", "#6E8F4E", "#3F4650", "#1E1D1B", "#F7F5F0", "#7A756C"


def mark(ax, x, y, w, color=INK, lw=3.0):
    """A thin horizontal line that steps down three times, like water down the terrace."""
    s = w / 4.0
    d = w * 0.06
    xs = [x, x + s, x + s, x + 2 * s, x + 2 * s, x + 3 * s, x + 3 * s, x + w]
    ys = [y, y, y - d, y - d, y - 2 * d, y - 2 * d, y - 3 * d, y - 3 * d]
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="butt", solid_joinstyle="miter")


def main():
    fig = plt.figure(figsize=(16, 9), facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.set_axis_off()

    # the mark, large, and the word
    mark(ax, 8, 78, 46, INK, 5)
    ax.text(8, 60, "Terraza", fontsize=54, color=INK, fontweight="bold", va="center")
    ax.text(8, 52, "the water comes down our street, and the street is ours", fontsize=13, color=MUTED, va="center",
            style="italic")

    # the mark in use: canopy, robot light, olive-oil tin
    y0 = 14
    ax.text(8, 42, "THE MARK IN USE", fontsize=9, color=MUTED, fontweight="bold")
    # canopy edge
    ax.add_patch(Rectangle((8, y0 + 18), 40, 2.2, fc="#D9CDB4", ec="none"))
    for x in (10, 22, 34, 46):
        ax.plot([x, x], [y0 + 2, y0 + 18], color="#8C8576", lw=2)
    mark(ax, 20, y0 + 21.2, 16, INK, 2)
    ax.text(8, y0 - 2, "On a shade canopy, cut into the fascia", fontsize=8.5, color=INK)
    # robot status light
    ax.add_patch(FancyBboxPatch((58, y0 + 4), 18, 12, boxstyle="round,pad=0.6,rounding_size=3", fc="white", ec="#BDB6A8"))
    for cx in (61, 73):
        ax.add_patch(Circle((cx, y0 + 3), 2.2, fc=SLATE, ec="none"))
    mark(ax, 61, y0 + 12.5, 12, GREEN, 3)
    ax.text(56, y0 - 2, "On a delivery robot's status light", fontsize=8.5, color=INK)
    # olive-oil tin
    ax.add_patch(Rectangle((90, y0 + 1), 12, 20, fc=OCHRE, ec="#8A7440"))
    ax.add_patch(Rectangle((94, y0 + 21), 4, 2.5, fc="#8C8576", ec="none"))
    mark(ax, 91.5, y0 + 15, 9, INK, 1.8)
    ax.text(91.5, y0 + 7, "ACEITE\nTERRAZA", fontsize=6.5, color=INK, fontweight="bold", linespacing=1.1)
    ax.text(86, y0 - 2, "Stamped on an olive-oil tin", fontsize=8.5, color=INK)

    # naming system
    x1 = 112
    ax.text(x1, 82, "NAMING · IN WATER ORDER", fontsize=9, color=MUTED, fontweight="bold")
    rows = [("Terraza", "the city"),
            ("Avenida del Agua", "the main street, from the tank on the bluff"),
            ("Acequia 1, 2, 3 ...", "the acequia streets, numbered downhill"),
            ("Acequia 4 · Patio 2", "an address: how near you are to the water"),
            ("Plaza del Agua", "the main square"),
            ("La Llegada", "the arrival, under the coach canopy")]
    y = 76
    for name, what in rows:
        ax.text(x1, y, name, fontsize=12, color=INK, fontweight="bold", va="top")
        ax.text(x1, y - 3.4, what, fontsize=8.5, color=MUTED, va="top")
        y -= 8.2

    # colour does a job
    ax.text(x1, 24, "COLOUR DOES A JOB", fontsize=9, color=MUTED, fontweight="bold")
    for i, (c, lab) in enumerate([(OCHRE, "land and buildings"), (GREEN, "water and planting"),
                                  (SLATE, "machine territory")]):
        ax.add_patch(Rectangle((x1, 17 - i * 5.2), 6, 3.6, fc=c, ec="none"))
        ax.text(x1 + 8, 18.8 - i * 5.2, lab, fontsize=9, color=INK, va="center")
    ax.text(x1, 2.5, "One sans-serif family in two weights. Signs sit on the ground, not on poles.\n"
            "Paving changes texture 20 m before every machine crossing.", fontsize=7.5, color=MUTED)

    os.makedirs(os.path.join(PKG, "pages"), exist_ok=True)
    out = os.path.join(PKG, "pages", "identity.png")
    fig.savefig(out, dpi=150, facecolor=PAPER)
    print("wrote", os.path.relpath(out, PKG))


if __name__ == "__main__":
    main()
