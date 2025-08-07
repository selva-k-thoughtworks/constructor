import json
from collections import Counter

# Try to read from apply result first, fallback to plan
try:
    with open("apply-result.json") as f:
        data = json.load(f)
    print("📊 Deployment Summary (Applied Changes):")
except FileNotFoundError:
    with open("plan.json") as f:
        data = json.load(f)
    print("📋 Plan Summary (Planned Changes):")

changes = Counter()
for res in data.get("resource_changes", []):
    action = tuple(res["change"]["actions"])
    res_type = res["type"]
    changes[(action, res_type)] += 1

actions_map = {
    ("create",): "✅ Created",
    ("update",): "🛠 Updated",
    ("delete",): "🗑 Deleted",
    ("no-op",): "⚠️ Unchanged",
    ("create", "delete"): "🔁 Replaced",
}

for (actions, res_type), count in sorted(changes.items()):
    label = actions_map.get(actions, "/".join(actions))
    print(f"{label}: {count} {res_type}(s)")
