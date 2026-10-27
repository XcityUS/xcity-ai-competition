# Full illustrated practice Design Brief

`python scripts/build_practice_brief.py` builds both 31-page PDFs from `build_en.py` and `build_zh.py`. The scripts preserve the existing fourteen-chapter layout and illustrations. They do not derive the full brief from the shorter web guide.

Dependencies: Python, reportlab and pypdf; Arial and Arial Unicode fonts from macOS Supplemental Fonts (edit the explicit font paths for another environment). Re-render previews with Poppler at 1600 px (`pdftoppm -scale-to 1600 -jpeg -jpegopt quality=88`), using `media/brief/p` for English and `media/brief/zh-p` for Chinese. After changes, inspect all pages and verify links and page counts.

`build_maps.py` regenerates site, pilot, terrain, water and system diagrams from **this repository's issued site package**. Additional dependencies: numpy, Pillow, matplotlib, shapely and pyproj. The flood diagram uses the supplied flood-sensitive geometry; it does not recalculate or redefine that screen. Quantities in the brief follow `terrain_summary_9_13.json` (503.4 km² screened, 686.4 km² flat outside it), replacing the earlier draft's different 297 km² analysis. Both fixed pilot areas are shown. Climate and regional/satellite illustrations retain the previous full brief's credited sources and observation dates; they are context, not site survey data.

Release decisions, 26 October 2026:

- Keep: full design task, maps, fourteen chapters, four design layers, eleven institution-track topics, five shortlisted teams, US$50,000 per valid Stage 2 submission and US$50,000 additional winner award.
- Change: release without internal-discussion labels; one application process and common eligibility/selection criteria, without statements about recruitment routes or invitations; initial ideas **up to 10 pages**; online basic registration, private drafts, separate evidence and ideas, then final submission.
- Synchronise: fixed agrivoltaic and living-quarter pilots; issued terrain/hydrology summary and maps; English and Chinese downloads and previews.
- Remove: email registration forms/password distribution as the application flow, exact-five-page requirement, recruitment-route descriptions, and the condensed thirteen-page PDF as the full Design Brief.
- Pending: final submission window and dates. No six-week duration or dates are adopted by this release. Registration and saving drafts do not constitute eligibility approval or shortlisting.

The AI Agent track retains its independent node rules; the institution track's eleven topics are not replaced by the Agent's three-group selection rule.
