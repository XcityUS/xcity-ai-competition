# Current V2 build

Run from repository root with the project Python environment. Canonical current geometry, crop geometry, metrics and proposal are in this package. Preserve them when rebuilding the presentation. tools/redesign_v2.py and tools/integrate_v2.py record the initial migration; rerunning them resets later operating changes.

Current presentation build order:
1. tools/finalize_v2.py audits current geometry and source identities.
2. tools/diagrams_v2.py then tools/operating_diagrams_v2.py.
3. tools/scene_v2.py, then scripts/render_views.py for the eight registered cameras.
4. Inspect controls, generate or retain matching finishes, and update image_provenance.json. A geometry change requires fresh visual comparison.
5. tools/publish_v2.py writes the25-page main booklet, visual-first A0 and14-page technical appendix.
6. tools/register_artifacts_v2.py records actual custom authoring inputs/output hashes.
7. scripts/self_check_submission.py; inspect final PDFs visually.

Agricultural source: geometry/crops.geojson plus assets.geojson. reviews/redesign-v2/agriculture-account.json contains crop area and assumed irrigation. Operational plans and commissioning maps use the same geometry. Earlier V1 is withdrawn and retained under reviews/withdrawn-v1/. No automatic result establishes independent design approval or resource rights.
