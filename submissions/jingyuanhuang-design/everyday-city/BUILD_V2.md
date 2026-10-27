# Current V2 build

Run from repository root with the project Python environment. Canonical current geometry, crop geometry, metrics and proposal are in this package. Preserve them when rebuilding the presentation. tools/redesign_v2.py and tools/integrate_v2.py record the initial migration; rerunning them resets later operating changes.

Current presentation build order:
1. tools/finalize_v2.py audits current geometry and source identities.
2. tools/diagrams_v2.py then tools/operating_diagrams_v2.py.
3. tools/scene_v2.py, then scripts/render_views.py for the eight registered cameras.
4. Inspect controls, generate or retain matching finishes, and update image_provenance.json. A geometry change requires fresh visual comparison.
5. tools/publish_v2.py writes the27-page main booklet, visual-first A0 and15-page technical appendix.
6. tools/register_artifacts_v2.py records actual custom authoring inputs/output hashes.
7. scripts/self_check_submission.py; inspect final PDFs visually.

Agricultural source: geometry/crops.geojson plus assets.geojson. reviews/redesign-v2/agriculture-account.json contains crop area and assumed irrigation. Operational plans and commissioning maps use the same geometry. Earlier V1 is withdrawn and retained under reviews/withdrawn-v1/. No automatic result establishes independent design approval or resource rights.

V3: canonical C02 courtyard surfaces are geometry/courtyard_details.geojson. tools/courtyard_revision_v3.py records the geometry refinement; regenerate diagrams after it. tools/territorial_axon_v3.py exports the formal source-based whole-site view. Current C02/overall finishes are media/v3; earlier selected images are historical under reviews/redesign-v3/before.

V4 current territory: tools/functional_revision_v4.py retains V3 local works, archives superseded territorial geometry and draws new allocations. After diagrams_v2.py and operating_diagrams_v2.py, run functional_diagrams_v4.py to write the authoritative whole-site/coverage/axon plates. Run check_functional_v4.py for area identity and retained-control checks. Do not run territorial_axon_v3.py over V4 outputs. Functional reference is Whitepaper V7 page5; overlapping coverage and exclusive land are separate.

V5 current build: canonical compact-v5 geometry; do not rerun older migration scripts. Current QA is check_compact_v5.py. Rebuild finaliser (V5 aware), coordinated/operating/functional/compact diagrams, native scene/controls, matching media/v5 finishes, publish_v2.py, register_artifacts_v2.py and self_check_submission.py.29-page main /15-page technical appendix.
