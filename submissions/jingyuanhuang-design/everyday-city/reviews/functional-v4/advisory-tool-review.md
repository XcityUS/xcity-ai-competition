# Area diagnostic review

The current organiser advisory tool was run outside the package. Its recursive area() applies the UTM-to-lon/lat transform again for MultiPolygon components, giving near-zero areas for most territories; those outputs were rejected. No repository script was modified. tools/check_functional_v4.py independently measures each lon/lat polygon component with pyproj.Geod once. Current scope:1658.8198km2 geodesic,1657.8435km2 UTM planar. Both comparisons agree at the displayed0.1% precision. Raw recursive diagnostic is not published as a reliable land account.
