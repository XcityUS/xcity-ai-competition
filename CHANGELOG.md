# Changelog

## 2026-10-26 · Design Practice online application

Replace the email/two-PDF application flow with online registration, a private draft management link, separate applicable evidence and an initial-ideas PDF of up to ten pages. Registration does not require ideas or attachments. Drafts can be prepared; final submission stays closed pending the formal timing policy and dates. Electronic copies or official registry/project links are accepted as specified; no notarisation is requested. Refresh the downloadable brief and its web previews from the current source. Agent submissions remain on GitHub.

## 2026-10-26 · Agent planning-rule consistency

Clarify whole-site minimum design questions without imposing construction area or urban form; distinguish seasonal channels, DEM flood screening and verified restrictions; split fixed pilot agricultural and living context labels and checks. Automatic compliance and design content review are reported separately. Script version 1.1.0. Existing submissions are not rewritten; classification conflicts are listed for review.

## 2026-10-26 · Grouped node selection

New Agent submissions select one node from each of three groups: living/public space, production/infrastructure, and urban interfaces/environment. The two existing submission directories retain the previous any-three-of-ten rule, including revisions. Website, brief, Agent instructions, scaffolder and gate G9 use the same policy.

Changes to the brief, the site package, the rules and the tools — newest first. Entrants: if a change affects your scheme, note it in your own `changelog.md`.

## 2026-10-26 — Design Practice Call: one application, a prize, stage-one site data

- Stage one is one email with two PDFs: ① the application (form, proof of registration and licence, the actual team, relevant projects, declaration) and ② initial ideas of up to 10 pages (the reading of the site, the design direction and the way of working; no full masterplan or rendering). No registration step. Eligibility is checked first, then the team and the ideas; five are chosen.
- The call is open to every practice, and XCITY may also invite practices to apply; every applicant follows the same requirements and criteria.
- Eligibility no longer sets a fixed project size or period: a legally registered practice or consortium with the licence that applies where it is registered, and a team covering masterplanning, urban design and landscape.
- Stage two: US$50,000 to each of the five for a compliant entry; US$50,000 more to one winner.
- New application form (`templates/firm-application-form.docx`) and stage-one site data (`brief/design-practice-stage1-data.zip`: site and pilot-area boundaries as KMZ, DXF and SHP, analysis maps, read-me).

## 2026-10-25 — two calls, one site

- The parcels are no longer named by number in the text: the site is 1,656 km² in San Juan; its two parts are the main parcel and the south-west parcel. File names are unchanged.
- The Spanish version of the practice brief is withdrawn; the brief is in English.
- The website moves to the `gh-pages` branch. `main` now holds only what agents and entrants use: the brief, site data, tools and submissions.
- Design Practice Call: the full brief, as Markdown (`brief/firm-track.en.md`) and as a PDF (`brief/design-practice-brief.en.pdf`). Stage two in four layers (the whole site, phase one, an urban-design zoom-in, key issues: three of six in depth); a phase-one reference scenario (50,000 residents, 20,000 jobs, 200 MW, 1–3 GW); submission requirements (six A0 boards, an A3 report of up to 60 pages, an 800-word statement, a preview image, data); six evaluation criteria; free registration. Dates, the honorarium, the shortlist size, the jury and intellectual property are published with the formal rules. Its page is ordered as applicants look for things: design brief, site, prizes and honorarium, submission requirements, evaluation criteria, registration.
- Names: **Open Agent Call** and **Design Practice Call**, under XCITY Urban Design and AI Planning Calls. The site has an entry page (`index.html`) and one page per call (`agent.html`, `practice.html`). Practice applications use the subject line `XCITY - Design Practice Call - <practice name>`.
- XCITY runs two separate calls under one name: the **Open Agent Call** (this repository) and the **Design Practice Call** (by qualification). They share only the site and its conditions, now set out once in `brief/site-conditions.en.md`; each has its own task, deliverables and review.
- Open Agent Call: the brief, design requirements and rules point to the shared conditions instead of repeating them; review reads the seven dimensions through four criteria — autonomy, reasoning quality, verifiability, originality (`brief/evaluation.json` → `criteria`). Nothing an entry must deliver has changed.
- Practice call: stage 1 (qualifications) is unchanged in what to send; stage 2 now has its own brief, design focus, deliverables and review, given to shortlisted teams.

## 2026-10-25 — asking the human, scales 2 and 3

- Pilot area: now two parts, both planned by XCITY and not open to design — the three agrivoltaic fields and the living quarter, phase 1 (2.48 km², in the south-west parcel, outline only: `brief/site-package/pilot-area/pilot_living_area.geojson`). The self-check tests geometry against both. The approximate fifth living point is removed from the indicative systems.
- Checkpoint 1 asks only what is the human's to decide: whether they have an idea for the city ("you decide" is a full answer), and which three of the ten places they want to see. Design decisions are the agent's. Questions are in plain words: names, not codes (AGENTS.md, "How to ask").
- Design requirements, new section F2: the master area should come from the site, not be a rectangle of convenience; each node is designed in full, so the massing renders already show how people use it.

## 2026-10-25 — practice track, map and wording

- Design practice track: its own page (`practice.html`); an application form (`templates/firm-application-form.docx`, one page in English, Chinese and Spanish) as the first page of the application PDF; a questions-and-answers section — answers are published in the repository, the same for every applicant (`brief/firm-track.*.md`, section 4).
- Pilot area: the three agrivoltaic fields are called the pilot area throughout. The folder is now `brief/site-package/pilot-area/pilot_area.geojson` (was `lead-zone/lead_zone.geojson`), the source id `SRC-PILOT` (was `SRC-LEAD`), the area keys `pilot_area_*` and the field ids `PA-01`–`PA-03`.
- Indicative systems: a fifth living point marks the organiser's planned living area; its position is approximate (`zoning/indicative_systems_9_13.json`).
- Competition page: a language list (English by default), a centred map with distance arrows in proportion to each road's distance and a 10 km scale bar.

## 2026-10-25 — finished images

- Finished images are now expected, not optional. An agent that can generate images makes them itself, over its massing renders, without stopping to ask; otherwise its human makes them with any tool they already use, from control images and prompts the agent prepares. Massing renders only is the last resort. Each image is captioned as a concept image (AGENTS.md checkpoint 2, `docs/visual-guide.md`).
- The self-check notes an entry with no finished images; the gates are unchanged.

## 2026-10-24 — preview published

- Repository opened as a preview of the XCITY AI Competition: 1,656 km² in San Juan, Argentina.
- Brief (zh / en), design requirements, rules, design practice track, agent taskbook, evaluation (12 gates, 7 dimensions), scenarios, awards.
- Site package: exact parcel boundaries, lead zone, roads, DEM (60 m), hillshade, DEM-derived channels, terrain summary, indicative systems, ten key nodes.
- Tools: scaffold, make_figures (7 figures, node massing views, A3 booklet, A0 board), render_proposal_html, self_check (12 gates), finalize, CI path check.
- Renders: scripts/make_scene.py (offline three.js scene of the scheme on the real terrain, with trees, people, robots and shuttles), scripts/render_views.py (aerial and eye-level views of the master area, the city and each node, by day and by evening or night) and scripts/ai_render.py (prompts, finished images through XCITY Studio or the entrant's own tool, registration with a control image). Gate G10 checks that the scene, the renders and every registered image are current.
- Drawings are image-led: the booklet opens with the city seen whole, then the city views, the seven figures, one sheet per node, and day to night at eye level.
- Agents stop and ask their human three times: the idea and the nodes (two or three directions to choose from), the image tool, and consent before the pull request; after submitting they keep returning, revise and log each round.
- Deeper node drawings: each node now has three sheets — views; a plan with overall dimensions, street widths and numbered interfaces, sections at true scale (`section`, `section_b`) and a cut across each kind of street; and a day of use (`day`) with the people, robots and shuttles of the 3D scene.
- The booklet opens with the idea (`manifest.thesis`) and a page showing where every mandatory requirement and agent task is answered. Entrants choose the cover (`booklet.cover`) and add their own pages (`booklet.pages`).
- Entries are frozen at the deadline: the version in the repository then (its package sha256) is the one reviewed. Borrowing from other entries needs credit.
- Design practice track: a call for qualifications (`brief/firm-track.*.md`, in English, Spanish and Chinese) — apply to competition@xcity.ai.
- The site is in English, Spanish and Chinese, and opens in the visitor's browser language. The scheme page is a workspace: read the statement, browse every file, check the evidence behind each figure, and see each image beside the render it was made from.
- Example package: submissions/EXAMPLE-agent/sample-scheme — "Terrace Oasis", a city of about 41,000 people, with finished images made from its renders.
- Entry dates, review panel, dimension weights and licensing terms: published with the formal rules.
