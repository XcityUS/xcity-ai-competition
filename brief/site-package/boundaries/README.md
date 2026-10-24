# 边界 · Boundaries

| 文件 File | 内容 What it is |
|---|---|
| `parcels_9_13.geojson` | 9 号（1,483.8 km²）与 13 号（172.5 km²）地块，两个要素 · two features |
| `scope_9_13.geojson` | 两块地的并集，1,656.4 km²，即本次竞赛的场地 · their union, the competition site |

两块地的顶点都取自业主提供的 KML，坐标未改动，**是精确边界**。面积为 WGS 84 椭球面积。
本文件不是地籍记录，不得用于法律或合同用途。

Both parcels' vertices come from the owner-supplied KML, unmodified: **these are exact boundaries**. Areas are geodesic on WGS 84. These files are not a cadastral record and are not for legal or contractual use.

**方案的「统筹研究范围」就是 `scope_9_13.geojson` 的全部。** 你提交的所有几何都必须落在这条红线内（容差 50 m），自检脚本会检查。

**The overall study area of every scheme is the whole of `scope_9_13.geojson`.** All submitted geometry must lie inside this line (50 m tolerance); the self-check tests it.
