# Boundaries / competition topology revision

| File | What it is |
|---|---|
| `parcels_9_13.geojson` | Parcel A (original 9; machine ID `main`), 1,483.844674 km², and Parcel B (original 13; machine ID `south-west`), 174.975145 km² |
| `scope_9_13.geojson` | Revised union, 1,658.819819 km²; one Polygon without internal holes |
| `xcity_site_boundary.kml` / `xcity_site_boundary.kmz` | Exchange formats generated from the revised geometry |
| `boundary-revision.json` | Revision method, areas, checksums and archive pointer |

Revision **`2026-10-27-open-seam-closure`** repairs only the authorised open slit at the join between parcels 9 and 13. Other outer edges are retained. It also retains the earlier two internal-hole closures and overlap removal. Parcel A is unchanged; the authorised seam additions are assigned to Parcel B. The open-seam patch is explicitly documented in `boundary-revision.json`; this is not a general outward buffer or permission to alter other boundaries. Original files remain under `archive/2026-10-26/` for traceability. Existing submissions are not rewritten or silently represented as migrated.

The open-seam repair adds 2.135589 km² beyond the previous internal-hole-only revision (which added 0.304419 km² to the original 1,656.379811 km² union). The current geodesic union is 1,658.819819 km²; the nominal project description remains approximately 1,656 km² and must not substitute for geometric measurement. Areas are geodesic on WGS 84; the machine revision record is authoritative for full precision, method and version. This is a competition-data topology revision, **not cadastral certification**. Acquisition date, positional survey accuracy and legal verification remain unknown; the revision date is not a survey date. These files are not for legal or contractual use.

**The overall study area is the whole revised `scope_9_13.geojson`.** The issued geometry check uses its documented 50 m tolerance. When citing an area or generating a plan, identify the boundary revision and distinguish earlier raster summaries from revised vector geometry. Do not use archive or historical exchange files as the current boundary.
