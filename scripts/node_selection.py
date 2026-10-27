"""Node selection policy, shared by scaffolding and gate G9 (stdlib only)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def selection_errors(node_ids, package_path=None):
    with (ROOT / "brief/site-package/nodes/design_nodes.json").open(encoding="utf-8") as f:
        policy = json.load(f)
    valid = {node["id"] for node in policy["nodes"]}
    if len(node_ids) != 3 or len(set(node_ids)) != 3 or not set(node_ids) <= valid:
        return ["Choose three different node IDs from A01-A03, B01-B03 or C01-C04."]
    return ["Choose exactly one node from %s (%s)." % (group["en"], ", ".join(group["node_ids"]))
            for group in policy["groups"] if len(set(node_ids) & set(group["node_ids"])) != 1]
