import json
import re
import os
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
        
        # Clean up matches to remove timing prefixes like "1m"
        cleaned_matches = []
        for resource, action in matches:
            # Remove timing prefixes (like "1m", "2s", etc.) from the action
            cleaned_action = re.sub(r'^\d+[msh]\s*', '', action)
            cleaned_matches.append((resource, cleaned_action))
        matches = cleaned_matches
        
        changes = Counter()
        resource_details = []
        
        for resource, action in matches:
            match = re.match(r'(\w+)\.(\w+)\["([^"]*)"\]', resource)
            if match:
                res_type = match.group(1).replace("1m", "")
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
    # Check if we're running in GitHub Actions
    github_step_summary = os.environ.get('GITHUB_STEP_SUMMARY')
    
    output_lines = []
    
    output_lines.append("📊 Deployment Summary (Applied Changes):")
    output_lines.append("=" * 50)

    added, changed, destroyed, changes, resource_details = parse_apply_output()
    
    output_lines.append("### Apply Summary:")
    output_lines.append(f"✅ Resources added: {added}")
    output_lines.append(f"🛠 Resources changed: {changed}")
    output_lines.append(f"🗑 Resources destroyed: {destroyed}")

    if not changes and not resource_details:
        output_lines.append("\n### Status: Infrastructure is up to date!")
        # Still print to console and write to summary
        print("\n".join(output_lines))
        if github_step_summary:
            with open(github_step_summary, 'a') as f:
                f.write("## 🚀 Infrastructure Deployment Summary\n\n")
                f.write("\n".join(output_lines))
        return

    output_lines.append("\n### Resource Changes:")
    # Filter to only show aws_s3_bucket and aws_iam_role resources
    allowed_resources = ['aws_s3_bucket', 'aws_iam_role']
    filtered_changes = {k: v for k, v in changes.items() if k[1] in allowed_resources}
    for (action, res_type), count in sorted(filtered_changes.items()):
        icon = "✅" if action == "create" else "🛠" if action == "update" else "🗑"
        output_lines.append(f"{icon} {action.title()}: {count} {res_type}(s)")

    output_lines.append("\n" + "=" * 50)

    current_resources = get_current_state()
    if current_resources:
        # Filter to only show aws_s3_bucket and aws_iam_role resources
        allowed_resources = ['aws_s3_bucket', 'aws_iam_role']
        filtered_resources = [r for r in current_resources if r["type"] in allowed_resources]
        output_lines.append(f"\n### Current Infrastructure State:")
        output_lines.append(f"Total S3 bucket and IAM role resources deployed: {len(filtered_resources)}")
        by_type = Counter([r["type"] for r in filtered_resources])
        for res_type, count in sorted(by_type.items()):
            output_lines.append(f"• {res_type}: {count} resource(s)")

    config = get_config_info()
    if config:
        output_lines.append(f"\n### Configuration:")
        output_lines.append(f"Project: {config.get('project', 'N/A')}")
        if config.get("buckets"):
            output_lines.append(f"Buckets configured: {len(config['buckets'])}")
            for bucket in config["buckets"]:
                output_lines.append(f"  • {bucket['name']} (prefix: {bucket['prefix']})")

    output_lines.append(f"\n### Deployment Timestamp:")
    output_lines.append(f"Completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Print to console
    print("\n".join(output_lines))
    
    # Write to GitHub Step Summary if available
    if github_step_summary:
        with open(github_step_summary, 'a') as f:
            f.write("## 🚀 Infrastructure Deployment Summary\n\n")
            f.write("\n".join(output_lines))
            f.write("\n")

if __name__ == "__main__":
    main()
