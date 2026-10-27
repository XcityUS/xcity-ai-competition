# Whole-site zoning and road framework / 全场地分区与路网推导

This corrects a failure observed in the organiser-directed Everyday City rerun. The full issued boundary must receive an actual spatial proposal, not only a terrain backdrop to a small residential prototype. The organiser's older zoning image illustrates the method, not the current geometry or approved quantities: its approximately 4,421 km² scope, capacities, setbacks and road figures are not transferred to the current approximately 1,659 km² issued site.

## Required design process

1. **Read the entire site.** Start from the issued boundary and separate fixed agrivoltaic/living pilots, terrain, seasonal channels, flood-sensitivity screening and unknown conditions. Prepare a suitability argument; do not convert all screening into statutory exclusion or assume green/flat land has irrigation rights.
2. **Choose a structure and capacities.** Explain the roles and locations of living/centres, solar/agriculture, compute, production/logistics, landscape and retained land. Compare decisive alternatives against terrain, access and resource assumptions. System weights are not a command to fill the same percentage of land; solar and agriculture can share a system overlay.
3. **Draw the full-site base zoning.** Use meaningful polygons with boundaries, IDs, names, primary uses and evidence references. Every part of the issued site receives a stated role, including fixed context and retained/conditional land. Different compute and solar-agricultural locations must be readable even when both contribute to energy/computing. Do not choose a small city footprint and call the surrounding remainder an unexplained reserve. Retaining land is valid when justified; full-site planning does not mean building on every hectare.
4. **Design the road skeleton with the zoning.** Locate arrivals and connect the main centres and development/production districts through primary and secondary routes; resolve local access in appropriate enlargements. Explain route choice, terrain and drainage crossings, public versus freight/service roles, emergency access and external approaches. Distinguish existing, proposed and unsecured external connections. User type is not road hierarchy. Iterate the districts and network together; do not draw decorative lines or force all routes straight.
5. **Reconcile land and capacity.** Start from the five-function approximate 60/30/5/3/2 project reference, and explain justified alternatives. Follow `docs/functional-balance-workflow.md` and use `scripts/analyse_functional_balance.py` to separate exclusive base land, overlapping functional coverage and phased serviced/built works. Compute area and share from the base polygons, with a whole-site denominator. Show district roles, capacity scenarios, phase and resource/access dependencies alongside the map. A base account must not double count; overlapping functional systems are reported separately. None of these figures establishes water, utility or development rights.
6. **Produce useful coordinated drawings.** Whole-site functional zoning and road-framework plans show the entire issued boundary and all principal districts/routes at a legible scale. The six city themes, phase map, selected enlargements, nodes and overall axonometric all derive from that proposal. Local insets add detail; they never substitute for the full-site drawings. No fixed AI Agent page count applies.

## Existing files: explicit roles, no new parallel package

| File / property | Meaning |
|---|---|
| `geometry/structure.geojson`, `plan_role: base_zoning` | The mutually exclusive whole-site base zoning. Required: `district_id`, `name`, `primary_use`, `basis_ref`, and the existing `system` classification. A district may be a MultiPolygon. Cite the actual proposal decision and source/assumption; a reference string is not proof of suitability. |
| `geometry/structure.geojson`, `plan_role: system_overlay` | Optional overlapping system relations, kept separate from the primary land account. The existing system categories remain unchanged. |
| `geometry/movement.geojson`, `road_class` | Explicit `primary`, `secondary` or `local` hierarchy on route lines. Provide primary and secondary routes for the full-site framework. Keep `network: people / shared / machine` for user/operating type; it does not replace hierarchy. |
| `geometry/master_area.geojson` and `land_use.geojson` | Urban-design study extents and their more detailed land allocation. These do not shrink or replace the full-site base zoning. |
| `design_depth_matrix.json`, `whole_site` | Link the actual full-site zoning map, road map, source geometry, area/capacity account and explanation. A tiny city inset or system-colour overview is insufficient. |

Example properties only, with no suggested location or copied geometry:

```json
{"plan_role":"base_zoning","district_id":"D-01","name":"Entrant-defined district name","primary_use":"solar_agriculture","system":"energy_compute","basis_ref":"proposal.md#actual-decision-and-assumption-reference"}
```

Primary uses are entrant-defined; the default map recognises housing, mixed_use, agriculture, solar_agriculture, compute, industry, logistics, ecology, reserve and fixed_context for display. Keep categories and legends legible. Another justified category is allowed. No layout, district count, developed area, building product or facility separation distance is prescribed.

## What the tools now do, and do not do

The default whole-site panel draws submitted primary/secondary/local roads and base zoning. It does not invent either. A system-only input is visibly labelled as missing the full-site base plan. G12 checks base polygon coverage, overlap, required identifiers and explicit primary/secondary road records. It cannot establish that a retained area is justified, districts form a city, roads connect and serve them adequately, crossing engineering is feasible, or a diagram is useful. Those remain content-review questions. Passing these geometric tests is not design approval.

## 中文：这次反查的结论

之前的不足不只是“没列图名”：默认全场地图没有画提交的道路；五大系统的大类不能直接替代具体规划分区；局部住宅模板与默认图册很容易被误当成整体方案；检查也没有区分“覆盖全场地的分区”与“局部图＋大块背景”。我的重跑执行同样有错，不能全部归因于任务书。

正确推导是：**完整场地判断 → 结构与容量选择 → 全场地功能分区落位 → 主次道路与分区共同调整 → 面积、容量、资源及分期核对 → 专题图、局部深化与整体轴测**。

全场地分区须有明确多边形、名称、编号、用途及依据；农业、生产、算力、居住、公服、生态与保留地应在整个边界内形成有解释的安排。保留地不是空白，也不等于必须开发；固定农光场与生活区单列。功能系统可叠加，但基本土地账户不能重复。

路网须有真实线位和主次层级，说明如何联系地区与中心、怎样接入外部、物流与公共通行如何组织、哪里要跨沟。`network`表示使用者，不能代替`road_class`。主次道路不等于随意几条直线；分区与路线必须相互推敲。

分区与路网图必须展示当前完整边界，不能只把约11 km²局部放大，再把其余区域涂成没有说明的背景。上述英文表明确了既有JSON文件里的字段；不增设平行成果包。旧参考图约4,421 km²的边界、指标、退距及道路数值均不能直接沿用。图纸与几何引用可自动检查，空间方案的合理性必须另行评审。


## Revision scope / 修改边界

- Retain / 保留：issued boundary and both fixed pilots; overlapping five-system logic; design freedom, no minimum built footprint and no fixed Agent page count.
- Modify / 修改：whole-site base zoning roles, named districts/area account, road hierarchy, default rendering and geometric checks.
- Remove / 删除：accepting a small prototype plus an unexplained remainder or a system-only overlay as the complete zoning/road proposal.
- Unconfirmed / 待核实：old reference-image quantities, flood/setback assumptions, road rights and resource capacities; none is adopted as current site fact.

## Trace each district edge to a decision / 分区线要能追溯到设计决定

Read and apply `skills/xcity-city-design/SKILL.md` before geometry generation. For each meaningful district, explain its role/users, edge logic, source or declared assumption, access/service relationship, capacity basis and construction dependency in the existing proposal and account. Terrain/drainage, proposed corridors, centre/service relationships, operating interfaces and justified phase boundaries can inform edges. Where an edge is a design choice, say so. Rectangles, nearest-centre partitions or suitability pixels alone are not a functional zoning argument. Do not invent parcel boundaries, existing roads or detailed surveyed constraints.

At city scale show meaningful district and block relationships; resolve the selected urban enlargements without claiming that every hectare requires detailed parcels. Reserve and connect public-service sites before filling land with repeated housing modules. Overlay functions, roads, landscape and service access from the same geometry, inspect conflicts, and revise the organising layout before node views or finished renders. Keep a drawing when it tests a decision, required verification or clear communication, rather than adding sheets mechanically. No extra submission form or fixed site/population/page quota is introduced.

分区须在既有方案说明和土地账里讲清：用途与使用者、边界为何落在这里、资料或假设、交通和服务联系、容量依据、建设条件。地形水文、拟建路廊、中心与服务关系、生产运营和合理分期都可支持边界；设计选择应明说。不能只用矩形、最近中心自动分割或适宜性像元直接充当功能规划。先按使用与容量预留公服，再排街坊和住宅，叠合道路、功能、景观与服务并处理冲突，最后深化节点和渲染。不新增填表负担，不限定开发面积、人口或页数。
