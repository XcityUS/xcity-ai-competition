# Terrain evidence

Source: `SRC-DEM` in `../sources.json`. Source/acquisition date and measured horizontal/vertical accuracy are not supplied. The published grid is Copernicus GLO-30 resampled to 60 m in EPSG:32719; this is grid spacing, not a claim of 60 m survey accuracy. Slope is smoothed across 5 × 5 cells (300 m). Terrain summary describes raster-count areas as indicative to about 1%; raster and geodesic parcel areas have different methods.

Use for whole-site terrain screening, regional drainage and comparison of alternatives. Hillshade is visual relief, not a height measurement. `dem_9_13_utm19s_60m.png` is a 16-bit elevation-in-metres representation of the same grid; keep its published bounds and CRS when georeferencing. Do not derive detailed street grades, channel banks, building levels or foundation suitability as if surveyed. Detailed levels, control points, soils and geotechnical evidence remain missing. See `../evidence-index.json` for per-file provenance and limits.
