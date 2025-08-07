import json
import re
from collections import Counter
from datetime import datetime

def parse_apply_output():
    """Parse terraform apply output to extract resource changes"""
    try:
        with open("apply-output.txt", "r") as f:
            apply_output = f.read()
        
        # Look for summary at the end of the apply
        apply_summary_pattern = r'Apply complete! Resources: (\d+) added, (\d+) changed, (\d+) destroyed'
        summary_match = re.search(apply_summary_pattern, apply_output)
        
        added, changed, destroyed = 0, 0, 0
        if summary_match:
            added = int(summary_match.group(1))
            changed = int(summary_match.group(2))
            destroyed = int(summary_match.group(3))

        # Parse detailed changes
        resource_pattern = r'(\w+\.\w+\["[^"]*"\]):\s*(Creating|Creation complete|Updating|Update complete|Destroying|Destruction complete|Refreshing state)'
        matches = re.findall(resource_pattern, apply_output)
        
        changes = Counter()
        resource_details = []
        
        for resource, action in matches:
            match = re.match(r'(\w+)\.(\w+)\["([^"]*)"\]', resource)
            if match:
                res_type = match.group(1)
                res_name = match.group(2)
                res_key = match.group(3)
                
                if "complete" in action.lower():
                    if "creation" in action.lower():
                        changes[("create", res_type)] += 1
                        resource_details.append({
                            'type': res_type, 'name': res_name, 'key': res_key, 'action': 'created'
                        })
                    elif "update" in action.lower():
                        changes[("update", res_type)] += 1
                        resource_details.append({
                            'type': res_type, 'name': res_name, 'key': res_key, 'action': 'updated'
                        })
                    elif "destruction" in action.lower():
                        changes[("delete", res_type)] += 1
                        resource_details.append({
                            'type': res_type, 'name': res_name, 'key': res_key, 'action': 'deleted'
                        })
        return added, changed, destroyed, changes, resource_details

    except FileNotFoundError:
        return 0, 0, 0, None, None

def get_current_state():
    """Get current infrastructure state"""
    try:
        with open("current-state.json", "r") as f:
            state = json.load(f)
        resources = state.get('values', {}).get('root_module', {}).get('resources', [])
        return resources
    except FileNotFoundError:
        return []

def get_config_info():
    """Get configuration information"""
    try:
        with open("config.yaml", "r") as f:
            import yaml
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

def main():
    print("📊 Deployment Summary (Applied Changes):")
    print("=" * 50)

    added, changed, destroyed, changes, resource_details = parse_apply_output()
    
    print("### Apply Summary:")
    print(f"✅ Resources added: {added}")
    print(f"🛠 Resources changed: {changed}")
    print(f"🗑 Resources destroyed: {destroyed}")

    if not changes and not resource_details:
        print("\n### Status: Infrastructure is up to date!")
        return

    print("\n### Resource Changes:")
    for (action, res_type), count in sorted(changes.items()):
        icon = "✅" if action == "create" else "🛠" if action == "update" else "🗑"
        print(f"{icon} {action.title()}: {count} {res_type}(s)")

    print("\n### Detailed Resource Information:")
    for res in resource_details:
        print(f"• {res['action'].title()}: {res['type']} '{res['name']}' (key: {res['key']})")

    print("\n" + "=" * 50)

    current_resources = get_current_state()
    if current_resources:
        print(f"\n### Current Infrastructure State:")
        print(f"Total resources deployed: {len(current_resources)}")
        by_type = Counter([r["type"] for r in current_resources])
        for res_type, count in sorted(by_type.items()):
            print(f"• {res_type}: {count} resource(s)")

    config = get_config_info()
    if config:
        print(f"\n### Configuration:")
        print(f"Project: {config.get('project', 'N/A')}")
        if config.get("buckets"):
            print(f"Buckets configured: {len(config['buckets'])}")
            for bucket in config["buckets"]:
                print(f"  • {bucket['name']} (prefix: {bucket['prefix']})")

    print(f"\n### Deployment Timestamp:")
    print(f"Completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

if __name__ == "__main__":
    main()
