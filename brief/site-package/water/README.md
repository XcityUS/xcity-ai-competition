# Water and flood data

## Flood data: screening versus verified restrictions

- **Seasonal channels:** `water/channels_dem.geojson` contains DEM-derived channel lines, not surveyed banks. Permanent construction on an actual dry channel is prohibited. The checker uses indicative line buffers to flag possible conflicts for review; those buffers are not statutory setbacks. Smaller washes are not comprehensively mapped.
- **Flood-sensitive screening:** `water/flood_sensitive_dem.geojson` is a terrain screening model (within 1.5 km of a mapped channel and HAND less than 3 m, using a 60 m DEM), approximately 503 km². It is not a surveyed design-flood extent, a verified hazard zoning instrument, or a blanket permanent no-build area. “Outside the screening band” does not establish flood safety.
- **Verified restrictions:** no surveyed design-flood boundary, design discharge/return period or verified flood setback is supplied. Do not invent one. State assumptions and explain proposed avoidance, conveyance and protection; identify the hydraulic and field verification needed before implementation. Buildings in the screening layer are reported for content review, not failed merely for being in that layer.

## Provenance, precision and gaps

Source: `SRC-DEM`; acquisition date and measured accuracy are not supplied. D8 channel routing uses a 60 m resampled DEM; main channels have at least 1,000 km² upstream area and primary channels at least 100 km². The 2 × 2 degree DEM window truncates upstream catchments; smaller washes are incomplete. Flood-sensitive polygons are simplified to 30 m, which does not establish 30 m survey accuracy. No supplied layer maps lakes or verifies perennial supply. Water rights, yields, water quality, design discharges, return periods and surveyed banks remain missing. See `../evidence-index.json` for per-file records and `../README.md` for the shared infrastructure index.
