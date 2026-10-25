# Reproduction and review

This directory contains original design-generation tools, not organiser code. No example geometry was copied. The final submitted GeoJSON is canonical.

In a checkout of the competition repository, using Python 3.10+ and the organiser requirements (final gate verification used Python 3.12.14):

1. Run `tools/design.py` from the repository root to create original geometry.
2. Run `tools/repair_geometry.py` to correct a projection-roundtrip topology sliver.
3. Run `tools/refine_views.py`, `tools/reconcile_shade.py`, then `tools/finish_node.py` and `tools/short_labels.py` in that order.
4. Run `tools/energy.py`, `tools/metadata.py`, and `tools/make_pages.py`.
5. Run organiser `scripts/render_views.py` with width 1600 and height 1000. Final renders use the organiser renderer and its stamps.
6. The five built-in image edits are already retained under `media/`; their exact prompts are in `tools/final_prompts.json` and `image_provenance.json`. Stochastic image output is not exactly reproducible. If geometry changes, generate new concept images from new control renders and register them.
7. Run organiser `scripts/finalize_submission.py <package> --redraw`. Never edit generated figures, renders or PDFs by hand.

All steps refer to this package's own `tools/` paths. The metadata script resets the manifest to draft and pending-public-consent; finalize marks it ready again. Human consent must be recorded before any public submission.

## Important limits

- Hourly dispatch uses a synthetic weather profile; 72.993% is an illustrative energy-weighted physical match, not measured site performance.
- Fresh input is 840,000 m3/year including upstream loss of 40,000; reuse is an internal 200,000 transfer. Gross use is 1,000,000. Water rights, pilot use and quality are not verified.
- The 80 km external road is a quantity allowance, not a surveyed alignment. The access page is schematic.
- Proposed roofs cover 84.429% of the submitted public route length after reconciling actual canopy coverage. This is not a thermal-comfort simulation.
- Permanent building footprints avoid supplied dry-channel lines and flood-sensitive polygons. Smaller gullies and external upstream catchments require study.
- The organiser's general open-space figure depicts an illustrative channel corridor; our actual exclusion is the submitted flood reserve and A-FLOOD offsets, not a certified design flood width.
- Public entry remained unopened in the repository README when this scheme was prepared. No public PR was opened. Next manual rule/status review: 2026-10-28; the user has not requested a scheduled monitor.
