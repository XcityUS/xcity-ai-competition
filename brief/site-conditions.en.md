# Site and shared conditions

**The common ground of both calls** — the AI Agent Autonomous Planning Challenge and the Design Practice Urban Design Call. The design tasks, deliverables and review differ between them; the facts and constraints below do not. Where another document repeats one of them, this file governs.

---

## 1. The land

**Parcels 9 and 13, San Juan province, Argentina, east of the Andes — joined into one piece, 1,656 km².** Both boundaries come from the owner's KML and are exact. All site data is in `brief/site-package/`.

| | |
|---|---|
| Parcel 9 | 1,483.8 km². The Pie de Palo range occupies its south-east; east of the range is about 7 km² of continuous flat ground (the eastern wing) |
| Parcel 13 | 172.5 km² |
| The site | 1,656.4 km² (quoted as 1,656 km²): `site-package/boundaries/scope_9_13.geojson` |
| Slope < 2% | 1,183 km²; of which 686 km² is outside the flood-sensitive band |
| Slope ≥ 25% | 127 km², mostly the Pie de Palo range |
| Flood-sensitive | 503 km², along the seasonal channels |
| Elevation | 606–2,658 m, median 675 m |
| Roads | **No existing national or provincial road on site.** Nearest: RN 40 about 27.6 km; RP 510 about 35.6 km; RN 20 about 40.7 km |

Every design lies inside the site boundary.

## 2. The pilot area — protected

Two parts, both in parcel 13, both planned by XCITY. **Neither is open to design**: a scheme meets them, it does not redraw them.

| | |
|---|---|
| Agrivoltaic fields 01–03 | 13.9 km² of outline. Under the arrays a symbiotic system of jojoba, rosemary, forage cactus and alpaca is already running; its layout is fixed |
| Living quarter, phase 1 | 2.48 km² in the south of parcel 13: the city's first neighbourhood. Only its outline is published |

Data: `site-package/pilot-area/`. The city grows beside the pilot area, and how it meets it is part of every design.

## 3. Water

An arid region; surface water depends on Andean snowmelt. Every use — domestic, cooling, agriculture, landscape, panel cleaning — enters one water balance. Water rights are not supplied: state what you assumed, and what stops first when water runs short.

## 4. Terrain and hazards

- **Earthquakes.** San Juan is among the most seismically active provinces in Argentina; the INPRES-CIRSOC 103 code family applies. Structure and seismic strategy shape heights, spacing and refuge space.
- **The Zonda.** A dry, hot, strong, dust-laden downslope wind from the Andes. It affects solar yield and cleaning water, air-cooled intakes, outdoor life and street orientation. State a stance: block, channel, or step aside.
- **Dry channels and flash floods.** Seasonal channels on the alluvial fan are dry most of the time and flood within minutes of an upstream storm. **No permanent construction on a dry channel.** Terrain-derived channels: `site-package/water/channels_dem.geojson`.
- **Dark sky.** San Juan hosts astronomical observatories; give a night-lighting and light-pollution strategy.
- **No road.** The access corridor is itself phase-one construction work.

## 5. Phase one stands on its own

Phase one must work as a place if nothing after it is built: water, power, services, access and public life complete at its own scale. Later phases are triggered by conditions that can be observed, not by dates.

## 6. Data

| Supplied | Not supplied (held by) |
|---|---|
| Exact parcel boundaries and the site; the pilot area; terrain (DEM 60 m, hillshade, slope and flood band); terrain-derived channels; regional roads and distances; indicative positions of five urban systems; ten key nodes. See `site-package/README.md` | Official cadastre (Dirección de Geodesia y Catastro, San Juan) · grid connection and capacity (provincial utility) · water rights and abstraction (provincial water authority) · seismic code edition (INPRES / CIRSOC) · climate series (see `site-package/climate/README.md`) |

Indicative positions are a direction, not a land-use boundary. Where data is not supplied, assume — and state the value, its source and the reason. **A gap in the data the organiser supplied is never a reason to mark a design down.**
