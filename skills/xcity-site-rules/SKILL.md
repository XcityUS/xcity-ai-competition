---
name: xcity-site-rules
description: Site facts and hard constraints for the XCITY site (1,656 km², San Juan, Argentina) - boundaries, pilot area, channels, terrain, roads, the five systems and their indicative siting. Use while designing or checking an XCITY scheme's geometry.
---

# XCITY site rules

All data: `brief/site-package/` (EPSG:4326 unless stated). All areas: `brief/site-package/areas.json`.

## Facts

| | |
|---|---|
| Site | 1,656 km² nominal project area; current geometry 1,656.684229 km² (Parcel A 1,483.844674; Parcel B 172.839555). Owner-KML-derived competition boundary with internal seam closure; not cadastral verification |
| Fixed pilots | Three agrivoltaic field outlines (13.9 km²) and the planned first living-quarter outline (2.48 km²), both in the south-west parcel; fixed separately for competition, **not open to redesign**. Outline status does not establish measured interiors, building stock, capacity or completion |
| Slope < 2% | 1,183.6 km²; prior flood screening identifies about 686 km² outside its band (the newly closed seam is hydrologically unclassified) |
| Slope ≥ 25% | 127 km², mostly the Pie de Palo range in the south-east of the main parcel |
| Flood-sensitive | About 503 km² of DEM-derived screening, not a lake, surveyed design-flood extent, statutory setback or blanket permanent no-build zone; outside it does not establish flood safety |
| Elevation | 606–2,658 m, median 675 m |
| Roads | No national/provincial road crosses the supplied extract; local tracks are not comprehensively inventoried. Approximate shortest boundary-to-line distances: RN 40 27.6 km, RP 510 35.6 km, RN 20 40.7 km, RN 141 47.3 km, RN 150 52.9 km. These are not proposed route lengths, rights or utility evidence |
| Eastern wing | about 7 km² of continuous flat ground east of Pie de Palo, in its lee: indicative site of port and gateway industry |

## Hard rules (checked)

1. The seven checked geometry files stay inside `boundaries/scope_9_13.geojson` (the currently encoded G9 boundary tolerance is 50 m; not survey accuracy or a legal allowance). External access/resource study evidence belongs separately in optional `context/`, not in on-site development statistics or assumed rights.
2. No new submitted building in either fixed pilot part. Agrivoltaic context: `structure.system=agri_production`, land-use `agriculture`/`energy`. Living context: `structure.system=living`, land-use `residential`, `mixed_use`, `civic`, `open_space` or `infrastructure`. Do not label the whole living outline as agriculture/energy or claim verified internal agricultural uses. Agriculture labels retain historical compatibility only in the two organiser-listed legacy directories under v1, with a content-review note. These sourced labels do not authorise redesign or invented building stock. G9 checks land-use compatibility separately and reports structural-label conflicts for review; see `brief/site-package/pilot-area/README.md`.
3. No permanent construction on an actual dry channel. Supplied channel lines and check buffers are DEM indicators, not surveyed banks or statutory setbacks. Explain the basis/status of any proposed retreat; flagged conflicts require review. No verified design-flood boundary, design discharge or surveyed flood setback is supplied. The flood-sensitive screening alone neither bans all construction nor proves that it is safe.
4. The pilot-area under-panel system (jojoba, rosemary, forage cactus, alpaca) is unchanged; tall and climbing crops (pistachio, olive, vine) stay out of the arrays.

## Conditions every scheme answers

Water scarcity and uncertain secured supply (every use in the balance), seismic context, the Zonda, dry-channel flash floods, dark sky, unverified detailed access and the fixed pilots. Propose phase-one enabling works and state their evidence/rights status. A regional water source, nearby road or indicative power location is not a verified entitlement, connection capacity or approval. See the evidence index and site conditions for source limits rather than using this short summary as an engineering specification.

## The five systems (indicative — `zoning/indicative_systems_9_13.json`)

| System | Weight | Leans toward |
|---|---|---|
| Energy + compute | ~60% | West-central upland near water and power; 1–5 km from a main channel, slope < 3% |
| Agri-production | ~30% | Most of the flat ground; river valleys of the north and centre |
| Living + public life | ~5% | Several settlements near water, clear of flood, ≥ 13 km apart, away from compute and industry |
| Industry + automation | ~3% | Settlement industry with every settlement; gateway industry on the eastern wing |
| Trade + port | ~2% | Eastern wing of the main parcel, beside gateway industry; later phase, land held from phase one |

These are organiser reference intentions, not thresholds, confirmed resource locations or land-allocation percentages. They do not impose a 13 km spacing, channel offset or compulsory gateway location. Indicative positions are a direction, not a boundary. Adopt, move or overturn them, and say why. Cite them only with evidence tag `indicative`.

## Reading terrain without GIS libraries

`terrain/dem_9_13_utm19s_60m.png` is a 16-bit PNG: pixel value = elevation in metres, EPSG:32719, 60 m cells, bounds in `terrain/terrain_summary_9_13.json` → `files.hillshade_utm_bounds_m`. Pillow + numpy are enough.

## Evidence and scope discipline

Use `brief/site-package/evidence-index.json`, `sources.json`, `datapackage.json` and the boundary/terrain change records for actual provenance, dates, CRS/units, method/precision, use limits and gaps. Separate fixed competition conditions, preliminary screening, reference intentions and entrant design/assumptions. Unknown acquisition dates or capacities stay unknown; repository/revision dates are not survey dates. The owner-derived competition boundary is not certified cadastral evidence. The newly closed seam has updated terrain coverage but no silently extended hydraulic verification.

The whole-site structure covers the fixed extent. The entrant's master study area, actual phase-one development, first works and urban-design enlargement have different purposes; label areas and indicators accordingly. Reserves are not automatically urbanised, irrigated or realised demand. Missing organiser information itself is not penalised, but disclose assumptions/verification; it does not excuse missing required entrant design. Revisions must identify affected geometry, statistics, drawings and conclusions, with current recomputation and a preserved change record.
