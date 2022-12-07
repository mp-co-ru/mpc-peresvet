import json

def get_id(d: dict) -> dict:
    if "id" in d.keys():
        yield {"id": d["id"], "type": d["type"]}
    else:
        for key in d.keys():
            yield from get_id(d[key])

with open("workshop_ids.json", "r") as f:
    w = json.load(f)

ids = list(get_id(w))
print(f"Length: {len(ids)}")

with open("ids.json", "w") as f:
    json.dump({"ids": ids}, f, indent=4)
