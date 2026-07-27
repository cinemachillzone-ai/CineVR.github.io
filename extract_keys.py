import json, sys

def extract_keys(obj, keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            extract_keys(v, keys)
    elif isinstance(obj, list):
        for item in obj:
            extract_keys(item, keys)

if __name__ == "__main__":
    with open('micinema_catalog.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    unique_keys = set()
    extract_keys(data, unique_keys)
    for k in sorted(unique_keys):
        print(k)
