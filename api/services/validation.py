def validate_json(data, required):
    return all(field in data for field in required)
