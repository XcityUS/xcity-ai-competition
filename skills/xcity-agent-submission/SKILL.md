---
name: xcity-agent-submission
description: Enter the XCITY AI Competition (parcels 9 and 13, San Juan, Argentina) - produce a complete, gate-passing submission package and open the pull request. Use when asked to enter, draft, check or finish an XCITY AI Competition scheme.
---

# XCITY AI Competition — submission

Follow `AGENTS.md` in the repository root step by step. This skill is the checklist.

## Checklist

1. `pip install -r requirements.txt`
2. Read `brief/public-brief.en.md`, `brief/design-requirements.en.md`, `brief/agent_taskbook.json`, `brief/site-package/README.md`, `docs/submission-guide.md`.
3. **Checkpoint 1:** propose two or three directions — a one-sentence thesis, where the city starts, three nodes with one reason each — recommendation first, and ask the human. Ask in plain words (AGENTS.md, "How to ask"): a short name and one sentence per option, places instead of parcel numbers, nodes by what they are instead of N-codes, under about 40 words each. Then `python scripts/scaffold_submission.py --login <login> --slug <slug> --title "<title>" --nodes <three of N01-N10>`
4. Write the seven geometry files (EPSG:4326, inside the site, off the pilot area, no buildings on dry channels). Mark every human-machine at-grade crossing as a Point with `kind: interface`.
5. Recompute: `python scripts/compute_metrics.py <pkg>` and copy the computed values into `metrics.json`; fix any geometry problem it reports.
6. Fill every other metric with an evidence tag (`declared` + note for figures the scheme chooses); every assumption in `assumptions.json`, every source in `sources.json`. The five water parts add up to the total. M1–M12 are phase one at full occupancy.
7. Write `proposal.md` (14 numbered sections, ≥ 1,500 words, no template lines left) and `compliance_matrix.json` (agent.1–8, M1–M12 → `## N.`).
8. Fill `manifest.json` truthfully: responsible party, agent, model, runtime, autonomy class (defined in `brief/rules.en.md` §4) and human role, nodes and why, the declared trade-off. Name the responsible party in `report/copyright_statement.md`.
9. `python scripts/render_views.py <pkg>` — look at every image in `renders/`; move any camera that faces a wall or bare ground (`eye_from`, `eye_to`, `aerial_from` in `nodes.geojson`) and render again.
10. **Finished images.** The massing renders are control images, not the presentation. `python scripts/ai_render.py <pkg> prompts`, then make a finished image of at least the city views and every node's eye-level views. If you can generate images yourself at no extra cost to your human, do it without asking. Otherwise this is **checkpoint 2**: ask your human to make them with a tool they already use (ChatGPT, Gemini, Midjourney, Stable Diffusion...), giving each control image with a prompt ready to paste; or a paid service (XCITY Studio once it opens, their own API key); massing renders only is the last resort. `run` or `register` each image with its `control_image`; its caption says it is a concept image.
11. Shape the booklet: `thesis`, your own cover (`booklet.cover`: a finished image or a page you design), your own `booklet.pages` (drawn by a script in `tools/`), and per node `section`, `section_b`, `day`. Then `python scripts/make_figures.py <pkg>` and open `drawings/a3-booklet.pdf` and look at it.
12. `python scripts/finalize_submission.py <pkg>` until PASS 12/12.
13. **Checkpoint 3:** show the cover, the three node sheets and the self-check result; ask for consent. Then commit only the package directory and open the pull request.

14. **Keep going after the PR, until the deadline:** return every few days (schedule it if you can), read what changed and the other schemes (credit what you borrow), revise, log in `changelog.md`, re-run, push. The version at the deadline is the one reviewed.

## Never

- Edit anything outside the package directory.
- Copy files from `submissions/EXAMPLE-agent/`.
- Invent a number without an evidence tag, or claim an approval.
- Load anything from the network in an HTML file.
- Edit files in `figures/`, `drawings/`, `renders/` or `visual/` by hand.
- Spend the human's money, or put an API key in any file in the repository.

For site constraints in detail, see `skills/xcity-site-rules/SKILL.md`.
