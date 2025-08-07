import json
import re
from collections import Counter
from datetime import datetime

def parse_apply_output():
    """Parse terraform apply output to extract resource changes"""
    try:
        with open("apply-output.txt", "r") as f:
            apply_output = f.read()
        
        # Look for the actual apply summary at the end
        apply_summary_pattern = r'Apply complete! Resources: (\d+) added, (\d+) changed, (\d+) destroyed'
        summary_match = re.search(apply_summary_pattern, apply_output)
        
        if summary_match:
            added = int(summary_match.group(1))
            changed = int(summary_match.group(2))
            destroyed = int(summary_match.group(3))
            
            print(f"### Apply Summary:")
            print(f"✅ Resources added: {added}")
            print(f"🛠 Resources changed: {changed}")
            print(f"🗑 Resources destroyed: {destroyed}")
            
            # If no changes, this was just a refresh
            if added == 0 and changed == 0 and destroyed == 0:
                print("\n### Status: No Changes Required")
                print("All resources are up to date with the current configuration.")
                return None, None
        
        # Parse the apply output to extract resource creation/updates
        resource_pattern = r'(\w+\.\w+\["[^"]*"\]):\s*(Creating|Creation complete|Updating|Update complete|Destroying|Destruction complete|Refreshing state)'
        matches = re.findall(resource_pattern, apply_output)
        
        if matches:
            changes = Counter()
            resource_details = []
            
            for resource, action in matches:
                # Extract resource type and name properly
                # Example: aws_s3_bucket.buckets["logs"] -> type: aws_s3_bucket, name: buckets, key: logs
                match = re.match(r'(\w+)\.(\w+)\["([^"]*)"\]', resource)
                if match:
                    res_type = match.group(1)  # aws_s3_bucket
                    res_name = match.group(2)  # buckets
                    res_key = match.group(3)   # logs
                    
                    if "complete" in action.lower():
                        if "creation" in action.lower():
                            changes[("create", res_type)] += 1
                            resource_details.append({
                                'type': res_type,
                                'name': res_name,
                                'key': res_key,
                                'action': 'created',
                                'full_name': resource
                            })
                        elif "update" in action.lower():
                            changes[("update", res_type)] += 1
                            resource_details.append({
                                'type': res_type,
                                'name': res_name,
                                'key': res_key,
                                'action': 'updated',
                                'full_name': resource
                            })
                        elif "destruction" in action.lower():
                            changes[("delete", res_type)] += 1
                            resource_details.append({
                                'type': res_type,
                                'name': res_name,
                                'key': res_key,
                                'action': 'deleted',
                                'full_name': resource
                            })
                elif "refreshing state" in action.lower():
                    # This is just a refresh, not a change
                    pass
            
            return changes, resource_details
        else:
            return None, None
            
    except FileNotFoundError:
        return None, None

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
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        return {}

def main():
    print("📊 Deployment Summary (Applied Changes):")
    print("=" * 50)
    
    # Parse apply output
    changes, resource_details = parse_apply_output()
    
    if changes:
        actions_map = {
            ("create",): "✅ Created",
            ("update",): "🛠 Updated", 
            ("delete",): "🗑 Deleted",
        }
        
        print("\n### Resource Changes:")
        for (actions, res_type), count in sorted(changes.items()):
            label = actions_map.get(actions, "/".join(actions))
            print(f"{label}: {count} {res_type}(s)")
        
        print("\n### Detailed Resource Information:")
        for detail in resource_details:
            print(f"• {detail['action'].title()}: {detail['type']} '{detail['name']}' (key: {detail['key']})")
    
    # Always show current state and configuration
    print("\n" + "=" * 50)
    
    # Get current state
    current_resources = get_current_state()
    if current_resources:
        print(f"\n### Current Infrastructure State:")
        print(f"Total resources deployed: {len(current_resources)}")
        
        resource_types = Counter()
        for res in current_resources:
            resource_types[res['type']] += 1
        
        for res_type, count in sorted(resource_types.items()):
            print(f"• {res_type}: {count} resource(s)")
    
    # Get configuration info
    config = get_config_info()
    if config:
        print(f"\n### Configuration:")
        print(f"Project: {config.get('project', 'N/A')}")
        print(f"Buckets configured: {len(config.get('buckets', []))}")
        for bucket in config.get('buckets', []):
            print(f"  • {bucket.get('name')} (prefix: {bucket.get('prefix')})")
    
    print(f"\n### Deployment Timestamp:")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    if not changes and not resource_details:
        print("\n### Status: Infrastructure is up to date!")
        print("No changes were required during this deployment.")

if __name__ == "__main__":
    main()
