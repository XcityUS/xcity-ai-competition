# Boundaries / competition topology revision

| File | What it is |
|---|---|
| `parcels_9_13.geojson` | Parcel A (original 9; machine ID `main`), 1,483.844674 km², and Parcel B (original 13; machine ID `south-west`), 172.839555 km² |
| `scope_9_13.geojson` | Revised union, 1,656.684229 km²; one Polygon without internal holes |
| `xcity_site_boundary.kml` / `xcity_site_boundary.kmz` | Exchange formats generated from the revised geometry |
| `boundary-revision.json` | Revision method, areas, checksums and archive pointer |

Revision **`2026-10-27-seam-closure`** normalises the owner-supplied competition geometry. It retains the existing combined exterior exactly, closes two internal seam holes, retains Parcel A, assigns the closed seam to Parcel B and removes the earlier overlap from Parcel B. No buffering or external outline movement is applied. Consequently it is not accurate to say every parcel vertex is unchanged. Original files are retained under `archive/2026-10-26/` for traceability. Existing submissions are not rewritten.

The internal seam adds 0.304419 km² to the earlier 1,656.379811 km² union. Areas are geodesic on WGS 84; see the machine record for full precision. This is a competition-data topology revision, **not cadastral certification**. Acquisition date, positional survey accuracy and legal verification remain unknown; the revision date is not a survey date. These files are not for legal or contractual use.

**The overall study area is the whole revised `scope_9_13.geojson`.** The issued geometry check uses its documented 50 m tolerance. When citing an area or generating a plan, identify the boundary revision and distinguish earlier raster summaries from revised vector geometry. Do not use archive or historical exchange files as the current boundary.
