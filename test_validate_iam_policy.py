import yaml
import json
import sys

CONFIG_FILE = "config.yaml"
PLAN_FILE = "plan.json"

# Load config.yaml
with open(CONFIG_FILE) as f:
    config = yaml.safe_load(f)

# Load plan.json
with open(PLAN_FILE) as f:
    plan = json.load(f)

resources = plan["planned_values"]["root_module"]["resources"]

# Index resources by type, name, and index
policy_resources = {r["index"]: r["values"] for r in resources if r["type"] == "aws_iam_policy" and r["name"] == "bucket_write_policy"}
role_resources = {r["index"]: r["values"] for r in resources if r["type"] == "aws_iam_role" and r["name"] == "bucket_writer"}
attachment_resources = {r["index"]: r["values"] for r in resources if r["type"] == "aws_iam_role_policy_attachment" and r["name"] == "attach_policy"}

all_passed = True
for bucket in config["buckets"]:
    bucket_name = bucket["name"]
    bucket_full_name = f"{bucket['prefix']}-{bucket['name']}"
    write_prefix = bucket["write_prefix"]
    if not write_prefix.endswith("/"):
        write_prefix += "/"
    expected_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:PutObject"],
                "Resource": f"arn:aws:s3:::{bucket_full_name}/{write_prefix}*"
            }
        ]
    }
    expected_role_name = bucket["iam_role_name"]

    # Validate policy content
    policy_vals = policy_resources.get(bucket_name)
    if not policy_vals:
        print(f"[FAIL] No policy found for bucket '{bucket_name}'")
        all_passed = False
        continue
    actual_policy_str = policy_vals["policy"]
    try:
        actual_policy = json.loads(actual_policy_str)
    except Exception as e:
        print(f"[FAIL] Could not parse policy JSON for bucket '{bucket_name}': {e}")
        all_passed = False
        continue
    if actual_policy == expected_policy:
        print(f"[PASS] Policy for bucket '{bucket_name}' matches expected policy.")
    else:
        print(f"[FAIL] Policy for bucket '{bucket_name}' does not match expected policy.")
        print("Expected:", json.dumps(expected_policy, indent=2))
        print("Actual:", json.dumps(actual_policy, indent=2))
        all_passed = False

    # Validate role and attachment
    role_vals = role_resources.get(bucket_name)
    if not role_vals:
        print(f"[FAIL] No role found for bucket '{bucket_name}'")
        all_passed = False
        continue
    if role_vals["name"] != expected_role_name:
        print(f"[FAIL] Role name for bucket '{bucket_name}' is '{role_vals['name']}', expected '{expected_role_name}'")
        all_passed = False
    else:
        print(f"[PASS] Role name for bucket '{bucket_name}' matches expected.")

    expected_policy_arn = policy_vals["arn"]
    if expected_policy_arn in role_vals["managed_policy_arns"]:
        print(f"[PASS] Role '{expected_role_name}' has correct policy attached.")
    else:
        print(f"[FAIL] Role '{expected_role_name}' does not have correct policy attached.")
        print(f"Expected policy ARN: {expected_policy_arn}")
        print(f"Actual managed_policy_arns: {role_vals['managed_policy_arns']}")
        all_passed = False

    # Validate role-policy attachment resource
    attach_vals = attachment_resources.get(bucket_name)
    if not attach_vals:
        print(f"[FAIL] No role-policy attachment found for bucket '{bucket_name}'")
        all_passed = False
        continue
    if attach_vals["role"] == expected_role_name and attach_vals["policy_arn"] == expected_policy_arn:
        print(f"[PASS] Attachment for bucket '{bucket_name}' links correct role and policy.")
    else:
        print(f"[FAIL] Attachment for bucket '{bucket_name}' does not link correct role and policy.")
        print(f"Expected role: {expected_role_name}, actual: {attach_vals['role']}")
        print(f"Expected policy ARN: {expected_policy_arn}, actual: {attach_vals['policy_arn']}")
        all_passed = False

if not all_passed:
    sys.exit(1)