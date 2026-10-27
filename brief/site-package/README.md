# Site package

**XCITY AI Competition · 1,656 km² · San Juan, Argentina**

The organiser’s issued machine-readable site package is in this folder. Documentation cannot substitute for missing measured data. Coordinates are EPSG:4326 (WGS 84 lon/lat) unless a file says otherwise. Sources and licences: `sources.json`. File list and checksums: `datapackage.json`. Every area figure: `areas.json`.

| File | What it is | Confidence |
|---|---|---|
| `boundaries/parcels_9_13.geojson` | the two parcels | owner-derived topology revision; survey accuracy unknown |
| `boundaries/scope_9_13.geojson` | their union = the site | union of supplied geometry; not a legal survey |
| `pilot-area/pilot_area.geojson` | pilot area: the three agrivoltaic fields, **not open to design** | organiser |
| `pilot-area/pilot_living_area.geojson` | pilot area: the living quarter, phase 1 (outline), **not open to design** | organiser |
| `access/roads_osm.geojson` | nearest national and provincial roads | OpenStreetMap |
| `access/road_distances_9_13.json` | shortest distance from the site to each road | computed |
| `water/channels_dem.geojson` | seasonal channels derived from the DEM (upstream area ≥ 100 km²) | derived, not surveyed |
| `water/flood_sensitive_dem.geojson` | flood-sensitive band, 503 km² (defined in terrain_summary) | derived |
| `terrain/dem_9_13_utm19s_60m.tif` | elevation (GeoTIFF) | Copernicus DEM GLO-30 |
| `terrain/dem_9_13_utm19s_60m.png` | the same DEM as a 16-bit PNG, value = metres | same |
| `terrain/hillshade_9_13.png` / `hillshade_9_13_utm.png` | hillshade basemaps (lon/lat and UTM) | derived |
| `terrain/terrain_summary_9_13.json` | slope classes, flood band, elevation | computed |
| `zoning/indicative_systems_9_13.json` | indicative positions of the five systems | **indicative only** |
| `nodes/design_nodes.json` | ten key nodes, choose one from each of three groups | — |
| `climate/README.md` | climate: where to get it and how to declare it | — |

## Site facts

| | |
|---|---|
| Site | Nominal competition area 1,656 km² (retained label, not a new rounding); current geometric area and parcel areas are recorded in `boundaries/boundary-revision.json`; the nominal project label is not the measured geometric area |
| Pilot area | three fields, 13.9 km², and a living quarter, phase 1, 2.48 km², inside the south-west parcel |
| Slope < 2% | 1,183 km² |
| Slope ≥ 25% (mountain) | 127 km², mostly the Pie de Palo range in the south-east of the main parcel |
| Flood-sensitive | 503 km² |
| Flat and outside flood screening | 686 km² |
| Elevation | 606–2,658 m, median 675 m |
| National/provincial roads in supplied extract | **none on site**; nearest, RN 40, about 27.6 km straight-line boundary distance; local tracks are not inventoried |

## How to cite

- Cite the matching `SRC-*` id in your own `sources.json` for any figure taken from here.
- Anything from `zoning/indicative_systems_9_13.json` carries the evidence tag `indicative` — never measured or approved.
- Channels are terrain-derived flow lines drawn down to 100 km² upstream area; read smaller washes from the DEM yourself. Flood peaks are not supplied: write the value you used into `assumptions.json`.
- **A gap in organiser-supplied data is not itself a reason to mark an entry down.** Declare the source or assumption, its effect on the design, and how it must be verified. Disclosure satisfies traceability, not proof of technical feasibility or design quality.

## Not supplied

| Data | Held by | What to do |
|---|---|---|
| Official cadastre | Dirección de Geodesia y Catastro, San Juan | use the KML boundaries here |
| Grid connection and capacity | provincial utility | assume and declare |
| Water rights and abstraction | provincial water authority | assume and declare |
| Seismic code edition | INPRES-CIRSOC 103 | declare the edition you used |
| Climate series | see climate/README.md | obtain and declare |

## Licences

- Terrain-derived data: produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.
- Roads: © OpenStreetMap contributors, ODbL 1.0.
- Parcel boundaries, pilot area and indicative zoning are provided by XCITY for this competition only; not a cadastral record and not for legal use.

## Flood data: screening versus verified restrictions

- **Seasonal channels:** `water/channels_dem.geojson` contains DEM-derived channel lines, not surveyed banks. Permanent construction on an actual dry channel is prohibited. The checker uses indicative line buffers to flag possible conflicts for review; those buffers are not statutory setbacks. Smaller washes are not comprehensively mapped.
- **Flood-sensitive screening:** `water/flood_sensitive_dem.geojson` is a terrain screening model (within 1.5 km of a mapped channel and HAND less than 3 m, using a 60 m DEM), approximately 503 km². It is not a surveyed design-flood extent, a verified hazard zoning instrument, or a blanket permanent no-build area. “Outside the screening band” does not establish flood safety.
- **Verified restrictions:** no surveyed design-flood boundary, design discharge/return period or verified flood setback is supplied. Do not invent one. State assumptions and explain proposed avoidance, conveyance and protection; identify the hydraulic and field verification needed before implementation. Buildings in the screening layer are reported for content review, not failed merely for being in that layer.

## Evidence classes: read before locating development

[evidence-index.json](evidence-index.json) covers every resource in `datapackage.json`: source ID, source-date status, precision, intended use and limitations. Unknown dates remain null; the documentation review date and Git commit date are not acquisition dates. Cite the actual file/version, not merely a rounded statistic.

| Class | Meaning for the design |
|---|---|
| Fixed condition | Issued site and pilot outlines govern this competition; this does not certify survey accuracy or legal approval. |
| Preliminary screening | Terrain, slopes and drainage identify issues and alternatives; validate at the design scale before claiming safety or buildability. |
| Reference context or intent | Regional OSM roads and indicative system points inform options; they do not establish an approved connection or mandatory zoning. |
| Participant assumption | Any missing capacity, alignment, discharge, climate series or inferred internal layout must be explicitly sourced or labelled assumed in your own `assumptions.json` and `sources.json`. Do not relabel it supplied or measured. |

### Access, water, electricity and existing facilities: one index

| Topic | What is actually issued | What remains unknown / how to use it |
|---|---|---|
| Regional roads | `access/roads_osm.geojson`: five national/provincial routes, approximately 200 m simplification; `access/road_distances_9_13.json`: shortest geodesic distances RN40 27.6, RP510 35.6, RN20 40.7, RN141 47.3, RN150 52.9 km | These are not proposed road lengths. Local tracks, rights of way, actual access junctions, condition and traffic capacity are not supplied. Draw and justify the proposed connection and flag permissions. |
| Water | `water/` provides DEM flow paths and screening only | No verified well, reservoir, perennial supply, yield, quality, right, pipe or supply commitment. Do not turn a seasonal channel or screening polygon into a lake or available water resource. State a supply scenario, balance, route and verification needs. |
| Electricity | No utility network, substation or connection-capacity dataset | Solar intentions are not a secured grid connection. Show assumed generation, storage/backup and delivery/connection scenarios; identify utility confirmation needed. |
| Pilot fields | `pilot-area/pilot_area.geojson`: fixed agrivoltaic field outlines | Classify separately as agriculture/energy context. Array counts describe the issued programme, not measured electrical output or service capacity. |
| Pilot living quarter | `pilot-area/pilot_living_area.geojson`: fixed phase-one living outline | Classify as living context; not wholesale agricultural land. No internal building inventory, measured population or infrastructure capacity is issued. Connect outside the outline and disclose assumed capacity. |
| Other existing facilities | No comprehensive surveyed facilities inventory | Absence from this package does not prove absence on the ground. Do not depict invented infrastructure as existing. |

For all gaps: explain a viable scenario and sensitivity, identify what could change the layout, and name the field/authority verification required. Adding a README does not supply the missing survey, hydrology or utility commitment. `zoning/indicative_systems_9_13.json` descriptions such as “near water and power” remain indicative intentions, not independent infrastructure evidence.

### 资料判读（中文摘要）

固定条件、初步筛选、参考意向与参赛者假设必须分开标注。边界采用 `2026-10-27-open-seam-closure` 修订：仅修复9/13接合处获授权的开放狭缝，其他外边保留；同时保留此前内部孔洞填合与局部重叠整理。当前几何面积、各地块面积及版本以 `boundaries/boundary-revision.json` 为准，项目名义面积仍约1,656 km²；这不等于地籍或测量精度已核实。洪泛敏感范围不是湖泊、设计洪水边界或全域永久禁建区；季节沟道也不是已落实的水源。农光场与既定生活区分别分类；生活区仅公布外轮廓，不应虚构内部建筑、现状人口和市政能力。道路距离为边界至道路的直线距离，不是可实施道路长度。供水、电力、现状设施、地形和水文缺失资料必须明确列出，并说明假设、方案影响与下一步核实方式；文字说明不能替代真实资料。

## Current boundary revision

Use the current `boundaries/boundary-revision.json` revision `2026-10-27-open-seam-closure`, not an archived source. Only the authorised open seam at parcels 9/13 is repaired; other outer edges are retained. The prior internal-hole closure and overlap removal are retained. Read the current geodesic union and parcel areas from that revision record; nominal project area remains about 1,656 km²; older terrain raster cell totals are a separate method/version and must not silently be presented as recalculated under this revision. The revision date is a topology-edit date, not a survey acquisition date. Exchange KML/KMZ and archive details are in `boundaries/README.md`.

The retained 1,656 km² competition label is nominal. Newly closed seam land is not automatically flood-safe: the historic hydraulic screening model has not been extended merely by closing geometry. Consult the terrain summary revision notes before using slope or screening statistics for the added seam.
