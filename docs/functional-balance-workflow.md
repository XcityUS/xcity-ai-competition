# Functional balance: a common starting point, room for exploration

## What the project is based on

XCITY Whitepaper V7 (October 2026), page 5, establishes five functional directions and approximate shares: energy/compute 60%, agriculture 30%, living 5%, industry 3%, trade/port 2%. **Every design starts by responding to this programme and reference balance.** Do not substitute an arbitrary new-town, housing-estate or logistics-led brief. Designers may explore a different balance when they explain the spatial, resource, demand and phasing reasons. Departure is a design argument, not an automatic failure or permission to omit a function.

The whitepaper describes functional-region land shares in an older, approximately 400,000-hectare project context (page 4). The current competition expresses the five percentages as approximate strategic system weights, with overlap permitted. This distinction must be stated: the reference is the starting programme, **not five mutually exclusive land quotas or five installed-facility percentages**. Solar production and under-panel forage/jojoba can occupy the same land. The current issued boundary and protected pilots govern geometry. Do not scale old hectare figures, 600 GW, a million residents or historic siting directions directly into this boundary.

## Three linked accounts, one design

1. **Territorial base land:** mutually exclusive base-zone polygons covering the current site. Compute their areas and shares with the whole-site denominator, including separately identified fixed pilots and retained terrain/drainage. Strategic research, production and gateway territories are not all built or irrigated land. A gross region label cannot justify its scale.
2. **Functional coverage:** show energy, agriculture, living/services, industry and trade relations over the base zones. Where functions overlap, report each union and the overlap explicitly. Do not add these coverage figures to the exclusive land account or pretend they sum to 100%.
3. **Serviced and built programme by phase:** distinguish gross allocated region, campus/field boundary, serviced land, building/panel/crop footprints, commissioned works and conditional reserve. Explain hectares through population/jobs, facility footprint and operating space, energy/water and access. Keep MWp solar separate from IT MW, facility input MW and annual energy. Annual energy equality is not hourly matching. Unsecured supply remains unknown.

For a large industry/logistics allocation, provide an operating programme/throughput and stage or identify the unserviced reserve inside it. For living land, show dwellings/population, building intensity, roads and essential services. For solar agriculture, show compatible panel/crop/work envelopes and the water/capacity scenario; confirmed forage and jojoba do not supply universal yields, density or irrigation demand. For compute, draw modular industrial halls and shared servicing; large gaps require an operational or phasing reason.

Show the reference and proposal side by side with scope/denominator/status. Explain consequential differences. An ecology/reserve account may be necessary even though it is not one of the five reference directions; never remove protected or unsuitable ground simply to force the five shares to 100%. Conversely, do not hide most of the site behind an unexplained reserve. A useful map shows function, route/centre relationships and the reason for its scale. A0 shows the spatial argument and a few key figures; detailed accounts belong in the appendix.

## Run the advisory assistant

```bash
python scripts/analyse_functional_balance.py submissions/<login>/<slug> --out work/balance
# If an older source feature is invalid, an explicit diagnostic option can repair a copy in memory:
python scripts/analyse_functional_balance.py submissions/<login>/<slug> --out work/balance --repair-for-analysis
```

Reads the **current** boundary and actual base-zone/system-overlay geometry. Outputs JSON and a readable Markdown land account, reference comparison, geometric gaps/overlaps, missing demand inputs and questions for the next design iteration. It never redraws zoning, changes the submission, predicts demand, enforces reference quotas, or grants resource/development rights. Invalid geometries stop the default run; the diagnostic option records each in-memory repair and leaves source files untouched. Check those findings before relying on an account.

Optional `--programme scenario.json` computes demand-to-land estimates only when every required input carries `value`, `evidence` (`sourced`, `assumed` or `declared`) and `basis`. No values are guessed. Supported input groups:

- Housing: `population`, `people_per_dwelling`, `floor_area_m2_per_dwelling`, `gross_far`. Gross FAR here includes the chosen residential/service/street study denominator; explain inclusions and public-service provision separately.
- Solar: `solar_mwp`, `gross_mwp_per_km2`. Density must cover the chosen gross field boundary, including its service/drainage assumptions; do not use panel surface density as land density.
- Compute: `it_mw`, `it_mw_per_hall`, `hall_footprint_m2`, `campus_building_coverage` (fraction). Rounds up complete halls. Coverage must account for the proposed campus boundary, shared plant, yards and future works; not a universal engineering standard.

Example **format only**, not recommended values: `{"population":{"value":1000,"evidence":"assumed","basis":"Entrant-selected scenario; test demand and services"}}`. An incomplete group reports missing inputs. Use different justified scenario files to compare alternatives; do not call arithmetic an optimal city. Pair results with the whole-site functional/road maps and revise the design before rendering.

## 中文执行口径

白皮书五大功能及约 **60／30／5／3／2** 是共同起点，必须回应；允许有理由地探索调整，不是可以忽略的背景。先列参考方案，再列自己的配置、差异及理由。

严格区分：①全域互斥土地账户；②允许重叠的功能覆盖；③各期已配套、已建设、已投运和远期预留。白皮书旧范围的绝对面积和容量不能直接套用本轮边界。图上大区不等于全部建成的产业园、物流园或住宅区。光伏与板下牧草／霍霍巴可以复合，不能重复算地；算力必须落实模块化厂房和共享设施。容量缺依据就提出核实项，不能靠色块或渲染补出数据。

脚本帮助 Agent 快速核对实际面积、不同口径、容量输入缺口和设计问题；不替代选址、路网、资源论证与空间设计。比例偏离不自动判错，但不解释偏离、用研究预留代替生产主体、或不说明大块用地规模，不能视为已完成合理性论证。
