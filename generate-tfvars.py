import yaml
import json

with open("config.yaml") as f:
    config = yaml.safe_load(f)

tfvars = {
    "buckets": config["buckets"]
}

with open("terraform.tfvars.json", "w") as f:
    json.dump(tfvars, f, indent=2)
