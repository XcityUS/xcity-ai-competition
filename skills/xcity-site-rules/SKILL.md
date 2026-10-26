---
name: xcity-site-rules
description: Site facts and hard constraints for the XCITY site (1,656 km², San Juan, Argentina) - boundaries, pilot area, channels, terrain, roads, the five systems and their indicative siting. Use while designing or checking an XCITY scheme's geometry.
---

# XCITY site rules

All data: `brief/site-package/` (EPSG:4326 unless stated). All areas: `brief/site-package/areas.json`.

## Facts

| | |
|---|---|
| Site | 1,656 km² = the main parcel (1,483.8) + the south-west parcel (172.5); exact boundaries from owner KML |
| Pilot area | 3 agrivoltaic fields (13.9 km²) and a living quarter, phase 1 (2.48 km²), both in the south-west parcel; planned by XCITY; **not open to design** |
| Slope < 2% | 1,183 km² (686 km² of it outside the flood-sensitive band) |
| Slope ≥ 25% | 127 km², mostly the Pie de Palo range in the south-east of the main parcel |
| Flood-sensitive | 503 km² along the DEM-derived channels |
| Elevation | 606–2,658 m, median 675 m |
| Roads | none on site; RN 40 27.6 km, RP 510 35.6 km, RN 20 40.7 km, RN 141 47.3 km, RN 150 52.9 km |
| Eastern wing | about 7 km² of continuous flat ground east of Pie de Palo, in its lee: indicative site of port and gateway industry |

## Hard rules (checked)

1. All geometry inside `boundaries/scope_9_13.geojson` (50 m tolerance) — gate G9.
2. No building on the pilot area; only `agriculture` or `energy` land use may overlap it — gate G9.
3. No permanent construction on a dry channel; buildings touching `water/channels_dem.geojson` are listed for the reviewers.
4. The pilot-area under-panel system (jojoba, rosemary, forage cactus, alpaca) is unchanged; tall and climbing crops (pistachio, olive, vine) stay out of the arrays.

## Conditions every scheme answers

Water (snowmelt-fed, scarce; every use in the balance), earthquakes (INPRES-CIRSOC 103), the Zonda (block, channel or step aside), flash floods on dry channels, dark sky, no road (the access corridor is phase-one work), the running agrivoltaic system.

## The five systems (indicative — `zoning/indicative_systems_9_13.json`)

| System | Weight | Leans toward |
|---|---|---|
| Energy + compute | ~60% | West-central upland near water and power; 1–5 km from a main channel, slope < 3% |
| Agri-production | ~30% | Most of the flat ground; river valleys of the north and centre |
| Living + public life | ~5% | Several settlements near water, clear of flood, ≥ 13 km apart, away from compute and industry |
| Industry + automation | ~3% | Settlement industry with every settlement; gateway industry on the eastern wing |
| Trade + port | ~2% | Eastern wing of the main parcel, beside gateway industry; later phase, land held from phase one |

Indicative positions are a direction, not a boundary. Adopt, move or overturn them, and say why. Cite them only with evidence tag `indicative`.

## Reading terrain without GIS libraries

`terrain/dem_9_13_utm19s_60m.png` is a 16-bit PNG: pixel value = elevation in metres, EPSG:32719, 60 m cells, bounds in `terrain/terrain_summary_9_13.json` → `files.hillshade_utm_bounds_m`. Pillow + numpy are enough.
