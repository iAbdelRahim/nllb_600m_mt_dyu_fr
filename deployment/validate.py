import json
import jsonschema
from jsonschema import validate

# Define the JSON schema
schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Generated schema for Root",
    "type": "object",
    "properties": {
        "inputs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "shape": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        }
                    },
                    "datatype": {
                        "type": "string"
                    },
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "name",
                    "shape",
                    "datatype",
                    "data"
                ]
            }
        }
    },
    "required": [
        "inputs"
    ]
}

# Example JSON to be validated
input_json = {
    "inputs": [
        {
            "name": "input-0",
            "shape": [1],
            "datatype": "BYTES",
            "data": ["i tɔgɔ bi cogodɔ"]
        }
    ]
}

# Validate JSON
try:
    validate(instance=input_json, schema=schema)
    print("Given JSON data is Valid")
except jsonschema.exceptions.ValidationError as err:
    print("Given JSON data is Invalid")
    print(err)
