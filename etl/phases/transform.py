import json

def transform(lines):
    for line in lines:
        raw = json.loads(line)
        yield {
            "external_id": raw["id"],
            "name": raw["name"].strip(),
            "email": raw["email"].lower(),
            "updated_at": raw["updated_at"],
        }
