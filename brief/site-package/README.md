# 场地包 · Site package

**XCITY AI Competition · 9 号与 13 号地块 · 1,656 km² · 阿根廷圣胡安省**

主办方提供的全部场地资料都在这个文件夹里。坐标除非另有说明，均为 EPSG:4326（WGS 84 经纬度）。
每个文件的来源与许可见 `sources.json`；文件清单与校验值见 `datapackage.json`；所有面积数字以 `areas.json` 为准。

Everything the organiser supplies about the site is in this folder. Coordinates are EPSG:4326 (WGS 84 lon/lat) unless a file says otherwise. Sources and licences: `sources.json`. File list and checksums: `datapackage.json`. Every area figure: `areas.json`.

| 文件 File | 内容 What it is | 精度 Confidence |
|---|---|---|
| `boundaries/parcels_9_13.geojson` | 9 号、13 号地块各自的边界 · the two parcels | 精确，取自业主 KML · exact, owner KML |
| `boundaries/scope_9_13.geojson` | 两块地的并集 = 竞赛场地 · their union = the site | 精确 · exact |
| `lead-zone/lead_zone.geojson` | 先行区 01–03，13 号地块内，最先建设，**不在设计范围内** · pilot area, built first, **not open to design** | 主办方提供 · organiser |
| `access/roads_osm.geojson` | 场外最近的国道与省道 · nearest national and provincial roads | OpenStreetMap |
| `access/road_distances_9_13.json` | 场地边界到各条道路的最短距离 · shortest distance from the site to each road | 由上两者计算 · computed |
| `water/channels_dem.geojson` | 由地形推算的季节性沟道（汇水 ≥100 km²）· seasonal channels derived from the DEM (upstream area ≥ 100 km²) | 推算，非测绘 · derived, not surveyed |
| `water/flood_sensitive_dem.geojson` | 洪泛敏感带，503 km²（定义见 terrain_summary）· flood-sensitive band | 推算 · derived |
| `terrain/dem_9_13_utm19s_60m.tif` | 高程，60 m，EPSG:32719 · elevation (GeoTIFF) | Copernicus DEM GLO-30 |
| `terrain/dem_9_13_utm19s_60m.png` | 同一高程，16 位 PNG，像素值 = 米；只用 Pillow 即可读 · the same DEM as a 16-bit PNG, value = metres | 同上 · same |
| `terrain/hillshade_9_13.png` / `hillshade_9_13_utm.png` | 山体阴影底图（经纬度 / UTM），范围见 terrain_summary · hillshade basemaps (lon/lat and UTM) | 由 DEM 生成 · derived |
| `terrain/terrain_summary_9_13.json` | 坡度分级、洪泛敏感带、高程统计 · slope classes, flood band, elevation | 由 DEM 计算 · computed |
| `zoning/indicative_systems_9_13.json` | 五个城市系统的意向落位 · indicative positions of the five systems | **意向，不是用地边界 · indicative only** |
| `nodes/design_nodes.json` | 十个重点节点，自选三处 · ten key nodes, choose three | — |
| `climate/README.md` | 气候：主办方不提供时间序列，说明去哪里取、怎么声明 · climate: where to get it and how to declare it | — |

## 场地事实 · Site facts

| | |
|---|---|
| 场地面积 Site | 1,656 km²（9 号 1,483.8 · 13 号 172.5） |
| 先行区 Pilot area | 3 片，外轮廓 13.9 km²，13 号地块内 · three fields, 13.9 km², inside parcel 13 |
| 坡度 <2% Slope <2% | 1,183 km² |
| 坡度 ≥25%（山地）Slope ≥25% | 127 km²，主要是 9 号地块东南的 Pie de Palo 山地 · mostly the Pie de Palo range |
| 洪泛敏感带 Flood-sensitive | 503 km² |
| 平地且不在洪泛带 Flat and clear of flood | 686 km² |
| 高程 Elevation | 606–2,658 m，中位数 675 m |
| 场内道路 Roads on site | **没有既有国道或省道**；最近的 RN 40 约 27.6 km · **none**; nearest, RN 40, about 27.6 km |

## 引用规则 · How to cite

- 用到这里的任何数字，在你的 `sources.json` 里引用对应的 `SRC-*` 编号。
- `zoning/indicative_systems_9_13.json` 里的内容，证据标签只能写 `indicative`，不得写成实测或已批准。
- 沟道是地形推算的汇流线，只画到汇水 ≥100 km²；更小的冲沟要自己从 DEM 读。洪峰流量主办方没有提供，你用了什么值，写进 `assumptions.json`。
- **主办方没有提供的数据，不会成为扣分理由**：声明你用的取值和来源，即视为满足要求。

- Cite the matching `SRC-*` id in your own `sources.json` for any figure taken from here.
- Anything from `zoning/indicative_systems_9_13.json` carries the evidence tag `indicative` — never measured or approved.
- Channels are terrain-derived flow lines drawn down to 100 km² upstream area; read smaller washes from the DEM yourself. Flood peaks are not supplied: write the value you used into `assumptions.json`.
- **A gap in the data the organiser supplied is never a reason to mark an entry down.** Declare the value you used and where it came from, and the requirement is met.

## 尚未提供的数据 · Not supplied

| 数据 Data | 持有方 Held by | 怎么处理 What to do |
|---|---|---|
| 官方地籍 Official cadastre | 圣胡安省测绘与地籍局 Dirección de Geodesia y Catastro, San Juan | 用本包的 KML 边界即可 · use the KML boundaries here |
| 电网接入点与可用容量 Grid connection and capacity | 省级电力公司 · provincial utility | 自行假设并声明 · assume and declare |
| 水权与取水许可 Water rights and abstraction | 省水资源主管部门 · provincial water authority | 自行假设并声明 · assume and declare |
| 适用抗震规范版本 Seismic code edition | INPRES-CIRSOC 103 | 声明你采用的版本 · declare the edition you used |
| 气候时间序列 Climate series | 见 climate/README.md | 自行取得并声明 · obtain and declare |

## 许可 · Licences

- 地形派生数据：produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.
- 道路：© OpenStreetMap contributors, ODbL 1.0.
- 地块边界、先行区与意向分区：由 XCITY 提供，仅用于本次竞赛；不是地籍记录，不得用于法律用途。 · Parcel boundaries, pilot area and indicative zoning are provided by XCITY for this competition only; not a cadastral record and not for legal use.
