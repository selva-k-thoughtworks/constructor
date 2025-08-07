import json
import re
from collections import Counter
from datetime import datetime

def parse_apply_output():
    """Parse terraform apply output to extract resource changes"""
    try:
        with open("apply-output.txt", "r") as f:
            apply_output = f.read()
        
        # Parse the apply output to extract resource creation/updates
        resource_pattern = r'(\w+\.\w+\["[^"]*"\]):\s*(Creating|Creation complete|Updating|Update complete|Destroying|Destruction complete)'
        matches = re.findall(resource_pattern, apply_output)
        
        if matches:
            changes = Counter()
            resource_details = []
            
            for resource, action in matches:
                # Extract resource type and name
                parts = resource.split('.')
                res_type = parts[0]
                res_name = parts[1].split('[')[0]
                res_key = re.search(r'\["([^"]*)"\]', resource).group(1)
                
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
        
        print("### Resource Changes:")
        for (actions, res_type), count in sorted(changes.items()):
            label = actions_map.get(actions, "/".join(actions))
            print(f"{label}: {count} {res_type}(s)")
        
        print("\n### Detailed Resource Information:")
        for detail in resource_details:
            print(f"• {detail['action'].title()}: {detail['type']} '{detail['name']}' (key: {detail['key']})")
        
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
        
    else:
        print("No resource changes found in apply output")
        print("Debug: First 500 chars of apply output:")
        try:
            with open("apply-output.txt", "r") as f:
                print(f.read()[:500])
        except FileNotFoundError:
            print("Apply output file not found")

if __name__ == "__main__":
    main()
