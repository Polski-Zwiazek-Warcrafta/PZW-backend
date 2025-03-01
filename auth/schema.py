user_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "password_hash"],
        "properties": {
            "username": {
                "bsonType": "string",
                "description": "Must be a string and is required"
            },
            "password_hash": {
                "bsonType": "string",
                "description": "Hashed password"
            },
            "isAdmin": {
                "bsonType": "bool",
                "description": "Admin flag, defaults to false",
            },
            "createdAt": {
                "bsonType": ["date", "null"],
                "description": "Timestamp of creation"
            },
            "updatedAt": {
                "bsonType": ["date", "null"],
                "description": "Timestamp of last update"
            },
            "deletedAt": {
                "bsonType": ["date", "null"],
                "description": "Timestamp of deletion (nullable)"
            }
        }
    }
}