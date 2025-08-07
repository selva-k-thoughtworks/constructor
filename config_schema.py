"""
Schema definition for config.yaml validation
"""

# Schema for config.yaml validation
CONFIG_SCHEMA = {
    'project': {
        'type': 'string', 
        'required': True, 
        'empty': False, 
        'default': 'default-project'
    },
    'buckets': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string', 
                    'required': True, 
                    'empty': False, 
                    'default': 'default-bucket'
                },
                'prefix': {
                    'type': 'string', 
                    'required': True, 
                    'empty': False, 
                    'default': 'default-prefix'
                },
                'iam_role_name': {
                    'type': 'string', 
                    'required': True, 
                    'empty': False, 
                    'default': 'default-role'
                },
                'write_prefix': {
                    'type': 'string', 
                    'required': True, 
                    'empty': False, 
                    'default': 'default/write/'
                }
            }
        }
    }
}

# Default values for easy access
DEFAULT_VALUES = {
    'project': 'default-project',
    'bucket_defaults': {
        'name': 'default-bucket',
        'prefix': 'default-prefix',
        'iam_role_name': 'default-role',
        'write_prefix': 'default/write/'
    }
} 