#!/usr/bin/env python3
"""
Config validation script for config.yaml
Validates schema and sets default values for missing fields
"""

import yaml
import sys
from cerberus import Validator
from config_schema import CONFIG_SCHEMA

def validate_config(config_path='config.yaml'):
    """
    Validate config.yaml against schema and set defaults for missing values
    
    Args:
        config_path (str): Path to the config file
        
    Returns:
        dict: Validated config with defaults set
    """
    try:
        # Load existing config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        print(f"Loaded config from {config_path}")
        
        # Validate against schema
        v = Validator(CONFIG_SCHEMA, allow_unknown=False)
        if not v.validate(config):
            print("❌ Config validation failed:")
            for field, errors in v.errors.items():
                print(f"  {field}: {errors}")
            return None
        
        # Get validated config with defaults
        validated_config = v.document
        
        # Check if any defaults were applied
        original_keys = set()
        if 'buckets' in config:
            for bucket in config['buckets']:
                original_keys.update(bucket.keys())
        
        validated_keys = set()
        if 'buckets' in validated_config:
            for bucket in validated_config['buckets']:
                validated_keys.update(bucket.keys())
        
        if validated_keys - original_keys:
            print("⚠️  Default values were applied for missing fields")
        
        # Write back the validated config
        with open(config_path, 'w') as f:
            yaml.dump(validated_config, f, default_flow_style=False, sort_keys=False)
        
        print("✅ Config validated successfully and saved")
        return validated_config
        
    except FileNotFoundError:
        print(f"❌ Config file {config_path} not found")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def main():
    """Main function to run validation"""
    print("🔍 Validating config.yaml schema...")
    
    validated_config = validate_config()
    
    if validated_config:
        print("\n📋 Validated config:")
        print(f"  Project: {validated_config.get('project')}")
        print(f"  Buckets: {len(validated_config.get('buckets', []))}")
        for i, bucket in enumerate(validated_config.get('buckets', []), 1):
            print(f"    {i}. {bucket.get('name')} (prefix: {bucket.get('prefix')})")
        sys.exit(0)
    else:
        print("\n❌ Validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 