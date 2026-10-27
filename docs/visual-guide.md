# Visual guide

> A brief that demands drawings must supply a way to make them.

The competition page asks for a city people can see, not a stack of data layers. Every key node needs **at least one aerial view and one eye-level view in which you can see how people use the place**, plus a plan or section. Sequences, day and night, video and interactive 3D are encouraged. Dense unedited text, unexplained debug diagrams or raw GIS layers alone do not establish the final design. Formal design analysis diagrams, plans, sections, service/flow diagrams and massing relationships belong in the main booklet when they explain decisions.

## 1. The image pipeline

Design the four connected levels first (`AGENTS.md`, `brief/design-depth.json`); then use this pipeline to communicate them. Caption the extent, phase, source/assumption status and the actual spatial question each drawing answers. Provide a title, readable labels and, where useful, legend, orientation and scale/dimensions. Add required access/resource context with its separate evidence status; it must not masquerade as on-site authorised development.

| Step | Tool | Output | Needs |
|---|---|---|---|
| 1. 3D scene | `scripts/make_scene.py` (run by step 2) | `visual/index.html`: an offline three.js scene of your geometry on the real terrain, with sun, trees, people, robots and vehicles generated from it | Python only |
| 2. Massing renders | `scripts/render_views.py` | `renders/<view>.png` for the whole master area, the city, and each node (aerial, eye level by day, and evening or night); `renders/stamp.json` | Playwright + Chromium (software WebGL, no GPU) |
| 3. Finished images (expected) | `scripts/ai_render.py` | `media/<view>.jpg`, registered in `image_provenance.json` with model, full prompt and control image | The agent's own image tool first; otherwise any tool the human uses by hand (ChatGPT, Gemini, Midjourney, Stable Diffusion), XCITY Studio, or an API key of their own |
| 4. Drawings | `scripts/make_figures.py` | Required figures and shared locator, node sheets, main A3 booklet, technical appendix/page index and A0 board | Python only |

The drawings pick up the best image of each view automatically: a registered finished image, otherwise the massing render, otherwise make_figures' own massing drawing.

**Make finished images whenever you can.** The massing renders provide traceable controls from the submitted geometry; the finished images show the place to people, and the cover, the gallery card and the node sheets use them. If the agent can generate images itself, it does so without stopping to ask. An entrant with no image tool at all may use the established massing-only exception and disclose it. That exception does not establish that every other gate passed or excuse unclear spatial evidence; the tool’s absence itself is not penalised.

## 2. Cameras

`render_views.py` places the cameras itself: the master aerial frames everything you built, the city views frame your homes and shops, and the node aerials frame the buildings in each node. To control them, add to a node in `nodes.geojson`:

| Property | |
|---|---|
| `aerial_from` | `[lon, lat]`: the aerial camera looks from this direction |
| `eye_from`, `eye_to` | `[lon, lat]`: an eye-level camera at 1.6 m and the point it looks at. Stand where people are, not inside a building and not on empty ground |
| `render_note` | One or two sentences on materials and life, used in the image prompt |

`manifest.json` may carry `render_note` (the whole city), `render_rules` (rules every image must keep, such as "no private cars") and `scene_seed` (an integer: another arrangement of trees, people and vehicles; the same package always gives the same scene on any machine). **Look at every render.** If a camera faces a wall or bare ground, move it and render again.

## 3. Finished images

```bash
python scripts/ai_render.py <package> prompts                    # renders/prompts.json: one prompt per view
python scripts/ai_render.py <package> run --provider xcity       # XCITY Studio (billed to your XCITY balance, once it opens)
python scripts/ai_render.py <package> run --provider openai      # your own OPENAI_API_KEY, at OpenAI's prices
python scripts/ai_render.py <package> register media/A03-eye-day.jpg --view A03-eye-day --model "..."   # made by hand
```

**Any image tool works.** If your runtime generates images itself, that comes first: no handoff and no cost to your human. `run` automates two services; for every other tool, give it the control image and the prompt from `renders/prompts.json`, save the result under `media/`, and `register` it. When your human makes the images by hand, hand them each control image with a prompt ready to paste. The panel judges agreement with the geometry, not the tool. The example package happens to use ChatGPT by hand; that is one choice, not a requirement.

Each prompt asks the model to keep the control image's camera, footprints, heights, streets and trees, and to change only materials, light and life. An agent must ask its human before spending money (AGENTS.md, checkpoint 2). Keys stay in the environment or in `~/.xcity/`, never in the repository.

## 4. What make_figures.py draws

| File | Content |
|---|---|
| `fig-01-structure.png` | Whole site: five design systems plus reserve with their recomputed areas, pilot area, channels, master area, nodes |
| `fig-02-master-plan.png` | Master area: land use, figure-ground, networks, place names, overall dimensions, nodes |
| `fig-03-land-use-density.png` | Buildings by floors; land use areas; coverage, FAR, open space recomputed |
| `fig-04-movement.png` | People, machine and shared networks; every interface numbered |
| `fig-05-open-space-water.png` | Open space, shaded and unshaded walking, channels and flood corridors |
| `fig-06-phasing.png` | Phases 1–3 with areas and triggers |
| `fig-07-metrics.png` | Every declared metric, its evidence tag, and the recomputed value where there is one |
| `node-<id>-plan.png`, `-aerial.png`, `-eye.png` | For each node: the plan, and the best aerial and eye-level image |
| `fig-08-node-location.png` | Whole-site location of the master area and a shared enlarged locator for all three nodes and their network relationships |
| `drawings/a3-booklet.pdf` | Complete public design: cover/thesis; whole site; shared locator/master plan; formal density, movement and water/open-space diagrams; three named/located nodes with necessary plans/sections; phasing; key indicators; custom pages needed for the design argument |
| `drawings/a3-technical-appendix.pdf` | Full accounts, compliance/evidence index, raw geometry controls, repeated image comparisons, extended technical details, sources, assumptions and disclosure; retain decisive formal node sections/operations in the main booklet |
| `drawings/presentation-index.json` | Document page counts and one-based page ranges for the required public sections |
| `drawings/a0-board.pdf` | One A0 board |

Every sheet carries a title, sources, the script version and a hash of its inputs, which include the renders and the registered images. The generator visualises supplied data and some rendering conventions. Check its labels, default cameras/sections and semantic assumptions; a generated sheet is not an independent confirmation of design quality or measured conditions.

**Make the layout yours; preserve the reading order.** The required information is in `docs/presentation-guide.md` and `templates/presentation.template.md`. Controls and checks stay in the technical appendix. `manifest.booklet.cover` picks the cover; `manifest.booklet.pages` adds pages you draw yourself (see `docs/submission-guide.md` §5). In `nodes.geojson`, `section` / `section_b` place the cuts and `day` writes the day of use; a land use with `level_m` is drawn at its level. The example's identity page comes from its own `tools/make_pages.py`.

## 5. Registering media

Every file under `media/` is registered in `image_provenance.json` (template: `templates/image_provenance.example.json`). `ai_render.py` does this for you.

| Field | |
|---|---|
| `path` | `media/...` |
| `node_id`, `view` | e.g. `B03`, `aerial` / `eye_level` / `other` |
| `model` | Tool or model and version |
| `prompt` | The full prompt, not shortened |
| `generated_at` | Date |
| `post_processing` | `none`, `retouch` or `composite` (+ `post_processing_note`) |
| `reference_images` | `none_text_only_prompt`, `own_work` or `third_party`; the last two need `reference_images_note` |
| `control_image` | `renders/<view>.png` the image was made from; gate G10 checks it exists and is current |
| `caption` | Must make clear it is a concept image that explains the geometry, not evidence |

**Rules.** Generated material may not pass itself off as a photograph, a measurement, an official boundary, a resident's opinion or an approval. Video carries a poster, captions and a transcript; audio a transcript; nothing autoplays. A render is judged on agreement with the submitted geometry — heights, positions, orientation — not on how good it looks. A render that contradicts the geometry costs points rather than earning them. **The disclosed tool/model and provenance remain available for review; the choice of tool earns no points.**

## 6. Interactive pages

`visual/index.html` is written for you: open it in any browser to orbit the scene and switch views. Anything else interactive goes under `media/`. Pages must work offline (gate G5): no CDN, no map tiles, no web fonts, no API calls, no iframes. Bundle any library you use into the package.

## 7. Cost

Every required output is free and offline. Finished images need not cost anything either: an agent's built-in image tool, or a free tier used by hand, is enough. Paying earns no points, and an image that disagrees with the geometry costs points. Confirm availability and actual charges before using any hosted image service; never assume an account credit or spend without the human’s authorisation.

## Design evidence belongs in the main story

The formal booklet is a complete design argument, not a fixed six-page abstract: site judgement → overall strategy → programme/capacity → movement/infrastructure → phase-one urban design → three nodes and use scenarios → implementation → indicators/trade-offs. Keep the established indexed whole-site/locator/node/phasing/indicator sequence, adding explanatory pages at its appropriate anchors. Page count follows the design.

Formal diagrams, master/block/node plans, decisive sections and massing relationships stay in the main booklet. Raw model screenshots, repeated control comparisons, calculation detail and program logs go in the technical appendix. The default generator now keeps its spatial-design diagrams and node details in the main booklet as a baseline; they still need entrant editing, captions and independent visual review. Use `booklet.pages` / `booklet.section_pages` for the full argument.

See `brief/design-depth.json`, `docs/design-depth-guide.md` and `docs/reference-examples.md`. More pages, larger development areas and more renders do not substitute for design depth.


## Final public submission language

Participants may communicate, research and design in their native language. Final public submissions must be in English: proposal title, narrative, public summary, booklets, drawing annotations and legends. This is a submission requirement, not a restriction on the working language. Automated checks verify the declared language; independent review must also verify text embedded in drawings and raster images.
