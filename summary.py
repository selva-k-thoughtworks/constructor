import json
import re
from collections import Counter

print("📊 Deployment Summary (Applied Changes):")

# Try to parse the apply output first
try:
    with open("apply-output.txt", "r") as f:
        apply_output = f.read()
    
    # Parse the apply output to extract resource creation/updates
    resource_pattern = r'(\w+\.\w+\["[^"]*"\]):\s*(Creating|Creation complete|Updating|Update complete|Destroying|Destruction complete)'
    matches = re.findall(resource_pattern, apply_output)
    
    if matches:
        changes = Counter()
        for resource, action in matches:
            # Extract resource type from the resource name
            res_type = resource.split('.')[0]
            
            if "complete" in action.lower():
                if "creation" in action.lower():
                    changes[("create", res_type)] += 1
                elif "update" in action.lower():
                    changes[("update", res_type)] += 1
                elif "destruction" in action.lower():
                    changes[("delete", res_type)] += 1
        
        actions_map = {
            ("create",): "✅ Created",
            ("update",): "🛠 Updated", 
            ("delete",): "🗑 Deleted",
        }
        
        for (actions, res_type), count in sorted(changes.items()):
            label = actions_map.get(actions, "/".join(actions))
            print(f"{label}: {count} {res_type}(s)")
    else:
        print("No resource changes found in apply output")
        
except FileNotFoundError:
    # Fallback to plan.json if apply output not available
    try:
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
    except FileNotFoundError:
        print("❌ No apply output or plan data found")
