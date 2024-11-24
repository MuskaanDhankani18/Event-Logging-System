from cerberus import Validator

# Define the schema
event_schema = {
    "event_type": {"type": "string", "required": True, "allowed": ["INFO", "ERROR", "DEBUG"]},
    "timestamp": {"type": "datetime", "required": True},
    "source_app_id": {"type": "string", "required": True},
    "data_payload": {"type": "dict", "required": True},
    "previous_hash": {"type": "string", "nullable": True},  # First log might not have a previous_hash
}

# Initialize the validator
validator = Validator(event_schema)
