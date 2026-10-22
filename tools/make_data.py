# make_data.py — writes the three data files. Deterministic: same output on every machine.
# Uses only random.Random(seed).random(), whose stream is stable across Python 3 versions.
import json, random, sys

MATERIALS = ["stone", "ceramic", "metal", "wood", "textile"]
DAMAGE = ["crack", "loose_base", "fading", "rot", "corrosion"]

MATERIAL_P = {"stone": .35, "ceramic": .15, "metal": .20, "wood": .20, "textile": .10}
DRIFTED_P  = {"stone": .10, "ceramic": .10, "metal": .10, "wood": .30, "textile": .40}

DAMAGE_P = {   # P(damage present | material)
    "stone":   {"crack": .35, "loose_base": .25, "fading": .20, "rot": 0,  "corrosion": 0},
    "ceramic": {"crack": .40, "loose_base": .05, "fading": .30, "rot": 0,  "corrosion": 0},
    "metal":   {"crack": .10, "loose_base": .10, "fading": .10, "rot": 0,  "corrosion": .60},
    "wood":    {"crack": .30, "loose_base": .10, "fading": .25, "rot": .50, "corrosion": 0},
    "textile": {"crack": .05, "loose_base": 0,   "fading": .50, "rot": .30, "corrosion": 0},
}

def pick(rng, dist):
    r, acc = rng.random(), 0.0
    for k, p in dist.items():
        acc += p
        if r < acc:
            return k
    return list(dist)[-1]

def make_report(rng, rid, material_p):
    material = pick(rng, material_p)
    damage = [d for d in DAMAGE if rng.random() < DAMAGE_P[material][d]]
    structural = "crack" in damage and "loose_base" in damage
    if not damage:
        severity = "none"
    elif structural:
        severity = "major"
    elif len(damage) == 1:
        severity = "minor" if rng.random() < .7 else "major"
    else:
        severity = "major" if rng.random() < .6 else "minor"
    return {"id": rid, "material": material, "damage": damage, "severity": severity}

def make_batch(seed, n, prefix, material_p):
    rng = random.Random(seed)
    return [make_report(rng, f"{prefix}{i:03d}", material_p) for i in range(1, n + 1)]

def write(path, reports):
    with open(path, "w") as f:
        for r in reports:
            f.write(json.dumps(r) + "\n")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    write(f"{out}/reference.jsonl", make_batch(1, 400, "ref", MATERIAL_P))

    batch_a = make_batch(2, 100, "a", MATERIAL_P)
    batch_a += [   # hand-planted problems
        {"id": "a-odd1", "material": "stone",   "damage": ["corrosion"],                   "severity": "minor"},
        {"id": "a-odd2", "material": "ceramic", "damage": ["crack", "fading", "corrosion"], "severity": "major"},
        {"id": "a-odd3", "material": "textile", "damage": ["crack", "loose_base"],         "severity": "major"},
        {"id": "a-bad1", "material": "stone",   "damage": ["rot"],                         "severity": "minor"},
        {"id": "a-bad2", "material": "marble",  "damage": ["crack"],                       "severity": "minor"},
    ]
    write(f"{out}/incoming_a.jsonl", batch_a)
    write(f"{out}/incoming_b.jsonl", make_batch(3, 100, "b", DRIFTED_P))
