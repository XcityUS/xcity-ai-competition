# -*- coding: utf-8 -*-
"""The example's own data script: fills metrics, assumptions, sources, compliance and manifest for 'Terrace Oasis'.
Run from the repository root after gen_geometry.py:
    python submissions/EXAMPLE-agent/sample-scheme/tools/fill_data.py submissions/EXAMPLE-agent/sample-scheme
"""
import json, sys, os, datetime
sys.path.insert(0, "scripts")
import xcity_common as xc

PKG = sys.argv[1]
c = xc.compute_metrics(PKG)
g = xc.load_geometry(PKG)
solid = [(p, geom) for p, geom in g["buildings"] if p.get("form") != "canopy"]
gfa = lambda use: sum(xc.geodesic_m2(geom) * float(p["floors"]) for p, geom in solid if p["use"] == use)
res, mix = gfa("residential"), gfa("mixed_use")
dwell = int(round((res + mix * 2 / 3) / 85))
residents = int(round(dwell * 2.4 / 10) * 10)
ha = lambda use, word=None: sum(xc.geodesic_m2(geom) for p, geom in g["land_use"]
                                if p["use"] == use and (word is None or word in p.get("name", "").lower())) / 1e4
pv_ha = ha("energy")
pv_mwp = int(round(pv_ha / 2.0 / 10) * 10)                 # 2 ha per MWp on the fans
roof_mwp = 20
orch_ha = ha("agriculture", "orchard")
north_ha = ha("agriculture", "north terrace")
green_ha = sum(xc.geodesic_m2(geom) for p, geom in solid if p.get("name", "").startswith("Greenhouse")) / 1e4
children = int(round(residents * 0.22 / 10) * 10)

JOBS = [("Compute campus operations and security", 140), ("PV, batteries and the microgrid", 120),
        ("Greenhouses", int(round(green_ha * 10))), ("Orchards, acequias and landscape crews", 420),
        ("Agri-processing, cold store and packing", 260),
        ("Workshops: PV and robot maintenance for the whole site's fields, fabrication, repair", 900),
        ("Freight cross-dock and autonomous fleet", 220), ("Water reclamation and the bluff tank", 60),
        ("Schools", int(round(children / 11.5 / 10) * 10)), ("Kindergartens and health posts", 420), ("Clinic", 260),
        ("Training college (robotics, agronomy, water)", 180),
        ("Town hall, open-data office and administration", 280), ("Library, culture, media school", 120),
        ("Markets, shops, cafes and food", 2200), ("Arrival hall, guesthouse and visitors", 260),
        ("Personal and home care", 700), ("Pilot-area field operations living in the city", 420)]
jobs = sum(n for _, n in JOBS)

L_PER_DAY = 130
w_dom = round(residents * L_PER_DAY * 365 / 1000)
IT_MW, AVAIL = 40, 0.85
it_gwh = IT_MW * AVAIL * 8760 / 1000
w_comp = round(0.20 * it_gwh * 1e6 / 1000)
w_agri = round(orch_ha * 4000 + green_ha * 8000 + north_ha * 600)
LAND_HA = 50
w_land = LAND_HA * 6000
w_ind = 60000
w_tot = w_dom + w_comp + w_agri + w_land + w_ind
reclaimed = round(w_dom * 0.8 * 0.9)
fresh = w_tot - reclaimed
city_gwh = round(residents * 2.0 / 1000 + 70)
facility_gwh = round(it_gwh * 1.25)

A = lambda i: "A-%02d" % i
metrics = [
    {"key": "master_area_km2", "value": c["master_area_km2"], "unit": "km2", "evidence": "computed", "computed_from": "geometry/master_area.geojson"},
    {"key": "site_coverage_pct", "value": c["site_coverage_pct"], "unit": "%", "evidence": "computed", "computed_from": "geometry/buildings.geojson"},
    {"key": "gfa_m2", "value": c["gfa_m2"], "unit": "m2", "evidence": "computed", "computed_from": "geometry/buildings.geojson"},
    {"key": "far", "value": c["far"], "unit": "ratio", "evidence": "computed", "computed_from": "geometry/buildings.geojson"},
    {"key": "open_space_pct", "value": c["open_space_pct"], "unit": "%", "evidence": "computed", "computed_from": "geometry/land_use.geojson"},
    {"key": "human_machine_interfaces", "value": c["human_machine_interfaces"], "unit": "count", "evidence": "computed", "computed_from": "geometry/movement.geojson"},
    {"key": "shaded_pedestrian_pct", "value": c["shaded_pedestrian_pct"], "unit": "%", "evidence": "computed", "computed_from": "geometry/movement.geojson"},
    {"key": "structure_km2", "value": c["structure_km2"], "unit": "km2", "evidence": "computed", "computed_from": "geometry/structure.geojson"},
    {"key": "hourly_cfe_match_pct", "value": 100, "unit": "%", "evidence": "assumed", "assumption": A(7),
     "note": "Physical and islanded: PV and batteries are the only source. The cost is carried by the compute campus as 85% availability; the city is served first in every hour."},
    {"key": "compute_availability_pct", "value": 85, "unit": "%", "evidence": "assumed", "assumption": A(7)},
    {"key": "peak_it_load_mw", "value": IT_MW, "unit": "MW", "evidence": "declared",
     "note": "Two 20 MW halls on the upper terrace; no grid connection assumed in phase one (A-03)."},
    {"key": "pv_capacity_mwp", "value": pv_mwp + roof_mwp, "unit": "MWp", "evidence": "declared",
     "note": "%d MWp of trackers on %d ha of the upper terrace at 2 ha/MWp, plus %d MWp on canopies and roofs in the city." % (pv_mwp, round(pv_ha), roof_mwp)},
    {"key": "storage_mwh", "value": 1000, "unit": "MWh", "evidence": "declared", "note": "Two 500 MWh battery halls beside the substation (A-06)."},
    {"key": "pue", "value": 1.25, "unit": "ratio", "evidence": "assumed", "assumption": A(4)},
    {"key": "wue_l_per_kwh", "value": 0.2, "unit": "L/kWh", "evidence": "assumed", "assumption": A(4)},
    {"key": "waste_heat_reuse_pct", "value": 9, "unit": "%", "evidence": "assumed", "assumption": A(13)},
    {"key": "annual_water_demand_m3", "value": w_tot, "unit": "m3/yr", "evidence": "assumed", "assumption": A(1)},
    {"key": "water_domestic_m3", "value": w_dom, "unit": "m3/yr", "evidence": "assumed", "assumption": A(8)},
    {"key": "water_compute_m3", "value": w_comp, "unit": "m3/yr", "evidence": "assumed", "assumption": A(4)},
    {"key": "water_agriculture_m3", "value": w_agri, "unit": "m3/yr", "evidence": "assumed", "assumption": A(9)},
    {"key": "water_landscape_m3", "value": w_land, "unit": "m3/yr", "evidence": "assumed", "assumption": A(9)},
    {"key": "water_industry_m3", "value": w_ind, "unit": "m3/yr", "evidence": "assumed", "assumption": A(9),
     "note": "Includes panel cleaning (robotic dry cleaning, two wet washes a year)."},
    {"key": "water_reuse_pct", "value": 90, "unit": "%", "evidence": "assumed", "assumption": A(8),
     "note": "Share of treated wastewater reused: %s m3/yr back into the acequias, orchards and groves." % format(reclaimed, ",")},
    {"key": "machine_traffic_rule", "value": "combined", "unit": "enum", "evidence": "declared",
     "note": "Separated on the 600 m machine grid; shared at walking pace on the 300 m acequia streets; people only in the lanes (A-16)."},
    {"key": "jobs_phase1", "value": jobs, "unit": "jobs", "evidence": "declared", "note": "Sum of the phase-one programme by facility (A-11)."},
    {"key": "residents_phase1", "value": residents, "unit": "persons", "evidence": "declared", "note": "Dwellings recomputed from buildings.geojson times 2.4 persons per dwelling (A-10)."},
    {"key": "dwellings_phase1", "value": dwell, "unit": "units", "evidence": "declared",
     "note": "Residential GFA plus two thirds of mixed-use GFA, recomputed from buildings.geojson, at 85 m2 gross per dwelling."},
    {"key": "long_term_residents", "value": 160000, "unit": "persons", "evidence": "declared",
     "note": "Four oasis cities of about 40,000 on the Line, each limited by its own water (A-15)."},
]
assumptions = [
    {"id": A(1), "topic": "Water source", "value": "Alluvial groundwater wellfield up the fan, %s m3/yr fresh in phase one (about %d L/s); %s m3/yr more is reclaimed wastewater" % (format(fresh, ","), round(fresh / 31536), format(reclaimed, ",")),
     "basis": "No water right is supplied by the organiser and recharge is unknown, so phase two is gated on measured drawdown rather than on a yield we cannot know."},
    {"id": A(2), "topic": "Phase-one IT load", "value": "40 MW: two 20 MW halls; pads for two more reserved on the terrace for phase two",
     "basis": "Sized so that the PV and storage can carry the city first and the campus second, islanded."},
    {"id": A(3), "topic": "Grid", "value": "No grid connection in phase one; the city runs as an islanded microgrid",
     "basis": "Grid capacity is not supplied; the nearest road (RN 20) is 40.7 km beyond the site and no transmission line is assumed."},
    {"id": A(4), "topic": "Cooling", "value": "Dry coolers with adiabatic assist above 35 C (about 500 h/yr): WUE 0.20 L/kWh, PUE 1.25",
     "basis": "Water binds, power does not; dry cooling gives up about 0.1 of PUE to save most of the water. WUE per IT kWh."},
    {"id": A(5), "topic": "PV yield", "value": "2,150 kWh/kWp/yr, single-axis tracking, 2 ha per MWp",
     "basis": "Order of magnitude for the high-irradiance Andean piedmont at 31.1 S; to be replaced by a PVGIS run (S-01)."},
    {"id": A(6), "topic": "Storage", "value": "1,000 MWh lithium iron phosphate, round-trip efficiency 88%",
     "basis": "Carries the city's night load (about 15 MW) and the campus at 70% for 13 hours with margin."},
    {"id": A(7), "topic": "Hourly matching and availability", "value": "100% physical hourly carbon-free supply; the city is served first; compute available 85% of hours at full load",
     "basis": "Day: 11 h at full load. Night: 13 h at 70% from storage. Winter cloud: batch work curtailed. 11 x 100% + 13 x 70% = 84% of full-load hours."},
    {"id": A(8), "topic": "Domestic water and reuse", "value": "%d L per person per day; 80%% returns as wastewater; 90%% of it reused" % L_PER_DAY,
     "basis": "Metered supply, greywater separation and low-flow fittings in an arid new city; San Juan's own consumption is far higher and is not the benchmark."},
    {"id": A(9), "topic": "Agricultural, landscape and industrial water",
     "value": "Orchards %d ha at 4,000 m3/ha/yr deficit drip; greenhouses %d ha at 8,000; north terrace %d ha of jojoba and algarrobo at 600 (establishment); irrigated streets, patios and squares %d ha at 6,000; industry 60,000 m3/yr" % (round(orch_ha), round(green_ha), round(north_ha), LAND_HA),
     "basis": "Orchards and street trees run on reclaimed water through the acequias; the river park, north slope and PV fields are unirrigated desert planting."},
    {"id": A(10), "topic": "Dwellings and household size", "value": "85 m2 gross per dwelling; 2.4 persons per dwelling; mixed-use blocks two thirds residential",
     "basis": "Courtyard houses and flats of 55-120 m2 for a young city with families."},
    {"id": A(11), "topic": "Phase-one jobs", "value": "%d jobs located in the city: %s" % (jobs, "; ".join("%s %d" % (k, n) for k, n in JOBS)),
     "basis": "Staffing ratios per facility; the construction workforce of phase two is temporary and excluded."},
    {"id": A(12), "topic": "Wind", "value": "Zonda from the west to north-west, hot and dry, several days a year; ordinary winds not assumed",
     "basis": "Wind data is not supplied; to be checked against SMN San Juan Aero observations before phase two."},
    {"id": A(13), "topic": "Waste-heat demand", "value": "Greenhouse night heating about 1.2 GWh/ha/yr; hot water for the civic quarter and the market about 8 GWh/yr: about 25 GWh of about 300 GWh IT energy",
     "basis": "The campus is 2.4 km from the nearest homes, so heat goes only to the greenhouses beside it and, by an insulated main down the bluff, to the civic quarter."},
    {"id": A(14), "topic": "Seismic design", "value": "Highest seismic zone of INPRES-CIRSOC 103 assumed; buildings of six floors or fewer, most of two to four; regular, short-span courtyard blocks in reinforced concrete frames or confined masonry",
     "basis": "San Juan is among the most seismically active provinces; edition and zone to be confirmed (S-03)."},
    {"id": A(15), "topic": "Long-term size", "value": "Four oasis cities of about 40,000 each on the Line, about 160,000 people",
     "basis": "Each city stays within a 2.5 km walk across and within reach of its own wellfield; size is limited by water, not land."},
    {"id": A(16), "topic": "Machine traffic rule", "value": "combined: separated on the 600 m machine grid; shared at walking pace on the acequia streets; people only in the lanes",
     "basis": "Freight and shuttles never need the lanes; doorstep delivery uses the acequia streets; every crossing of a machine street is a marked interface."},
    {"id": A(17), "topic": "City energy demand", "value": "About %d GWh/yr for the city (2,000 kWh per resident plus 70 GWh non-residential), %d GWh/yr for the campus at PUE 1.25" % (city_gwh, facility_gwh),
     "basis": "All-electric city with heat pumps and an electric fleet; to be replaced by an hourly load model."},
    {"id": A(18), "topic": "Flood", "value": "The lower terrace stands 4-15 m above the wash bed and outside the DEM flood-sensitive band; storm water from the bluff is led round the city in two swales to the river park",
     "basis": "Flood peaks are not supplied; the city is placed out of the band instead of being raised inside it."},
]
sources = [
    {"id": "S-01", "title": "Photovoltaic Geographical Information System (PVGIS)", "publisher": "European Commission, Joint Research Centre",
     "url": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en", "accessed": "2026-10-24",
     "used_for": "Tool named for verifying the PV yield assumption A-05"},
    {"id": "S-02", "title": "NASA POWER Data Access Viewer", "publisher": "NASA",
     "url": "https://power.larc.nasa.gov/docs/tutorials/data-access-viewer/quick-start/", "accessed": "2026-10-24",
     "used_for": "Named for hourly irradiance and temperature to size storage and cooling hours (A-04, A-06)"},
    {"id": "S-03", "title": "INPRES-CIRSOC 103 - Argentine seismic design code", "publisher": "INPRES / CIRSOC", "url": "",
     "accessed": "", "used_for": "Seismic design basis (A-14); edition to be confirmed"},
]
items = [{"id": "agent.%d" % i, "status": "answered", "section": "## %d." % s, "note": ""}
         for i, s in zip(range(1, 9), (1, 3, 4, 5, 6, 7, 8, 9))]
ms = {"M1": 3, "M2": 3, "M3": 4, "M4": 4, "M5": 4, "M6": 5, "M7": 5, "M8": 8, "M9": 8, "M10": 9, "M11": 9, "M12": 6}
items += [{"id": k, "status": "answered", "section": "## %d." % v, "note": ""} for k, v in ms.items()]

xc.write_json(os.path.join(PKG, "metrics.json"), {"metrics": metrics})
xc.write_json(os.path.join(PKG, "assumptions.json"), {"assumptions": assumptions})
xc.write_json(os.path.join(PKG, "sources.json"), {"sources": sources})
xc.write_json(os.path.join(PKG, "compliance_matrix.json"), {"items": items})
NODES = ["N01", "N02", "N10"]
man = xc.load_json(os.path.join(PKG, "manifest.json"))
man.update({
    "title": "Terrace Oasis: a city that grows its own shade beside the first fields",
    "summary": ("Reference example, not an entry. The first city stands on the flat terrace directly east of the pilot area, "
                "between the fields and a 30 m bluff, facing the Andes. About %s people live in low courtyard houses on a "
                "300 m grid; every street is an acequia street, shaded by trees watered by gravity from a tank on the bluff; "
                "machines keep to their own 600 m grid. Across the site, four oasis cities hang on one corridor, the Line, "
                "from the RN 20 gate to the port in the east. The city gives up growth speed, not water." % format(residents, ",")),
    # the arrangement of trees, people and vehicles the finished images were made from
    "scene_seed": 3658308874,
    "thesis": ("When machines take over much of the work, a desert city should be built around being outside together: "
               "shade and water first, and growth only as fast as the water allows."),
    "booklet": {"cover": "media/city-evening.jpg",
                "pages": [{"path": "pages/identity.png", "after": "idea", "title": "Identity: names, mark and colour",
                           "subtitle": "Agent task 1 · drawn by the agent with tools/make_pages.py"}]},
    "language": "en",
    "author": {"github": "EXAMPLE-agent", "responsible_party": "XCITY organiser - reference example", "organisation": "XCITY"},
    "agent": {"name": "Claude (Cowork)", "model": "claude-opus-5-5", "runtime": "Cloud sandbox, Python 3, this repository's scripts only"},
    "autonomy": {"class": "human_supervised",
                 "human_role": ("The organiser's design lead commissioned a reference example, asked that it answer all three "
                                "scales as a city rather than a compute town, confirmed the three key nodes the agent proposed "
                                "(N01, N02, N10), and chose the image tool. The agent made every "
                                "design decision and wrote every file; no human edited the package.")},
    "render_note": ("A compact low-rise city of courtyard houses on a regular grid of 300 m superblocks with tree-lined "
                    "streets and narrow irrigation channels, a central square under a solar canopy, olive orchards and "
                    "poplar windbreaks to the west against the agrivoltaic fields, solar fields, greenhouses and a small "
                    "data campus on the terrace beyond a low bluff to the east."),
    "render_rules": ("No private cars anywhere in the city: the streets carry only people, bicycles, small white delivery "
                     "robots and white driverless electric shuttles."),
    "nodes": NODES,
    "nodes_reason": ("Arrival (N01) decides what the city says it is; housing (N02) is where heat, earthquakes, water and robots "
                     "meet every day; the main square (N10) has to work at 45 C and in the Zonda. If these three work for "
                     "people, the rest of the plan is arithmetic."),
    "tradeoff": {
        "objective": "Growth speed: the city does not grow faster than its measured water allows",
        "why": "Nobody knows the aquifer's recharge. A city sized on hope is the one irreversible mistake a desert city can make.",
        "consequence": "Phase two waits for 24 months of published drawdown data and a second licence; land and housing come to market more slowly; some people who want to move in wait.",
        "who_bears": "The developer and investors, through slower returns, and households on the waiting list; not the aquifer and not the people already living here."},
    "design_depth": {
        "tier1_structure": {"evidence": ["geometry/structure.geojson", "figures/fig-01-structure.png"]},
        "tier2_master": {"evidence": ["geometry/master_area.geojson", "geometry/land_use.geojson", "geometry/buildings.geojson",
                                      "figures/fig-02-master-plan.png", "figures/fig-03-land-use-density.png"]},
        "tier3_nodes": {n: {"plan": "figures/node-%s-plan.png" % n, "aerial": "figures/node-%s-aerial.png" % n,
                            "eye_level": "figures/node-%s-eye.png" % n} for n in NODES},
    },
    "updated": datetime.date.today().isoformat(),
})
xc.write_json(os.path.join(PKG, "manifest.json"), man)
print("jobs", jobs, "dwellings", dwell, "residents", residents, "children", children)
print("water total", w_tot, "dom", w_dom, "comp", w_comp, "agri", w_agri, "land", w_land, "ind", w_ind, "reclaimed", reclaimed, "fresh", fresh)
print("pv ha", round(pv_ha), "mwp", pv_mwp, "orchard ha", round(orch_ha), "north ha", round(north_ha), "greenhouse ha", round(green_ha, 1))
print("city GWh", city_gwh, "facility GWh", facility_gwh, "IT GWh", round(it_gwh))
