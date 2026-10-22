# Domain vocabulary and Horn clauses for report validation live here.
MATERIALS = {"stone", "ceramic", "metal", "wood", "textile"}
DAMAGE = {"crack", "loose_base", "fading", "rot", "corrosion"}
SEVERITIES = {"none", "minor", "major"}
FACT_SYMBOLS = (
    {f"material_{value}" for value in MATERIALS}
    | {f"damage_{value}" for value in DAMAGE}
    | {f"severity_{value}" for value in SEVERITIES}
)


# Complete a triggering fact set with the fields required by the report schema.
def report_from_facts(facts, report_id):
    facts = set(facts)
    if not facts <= FACT_SYMBOLS:
        raise ValueError("unknown report facts")
    materials = sorted(value for value in MATERIALS if f"material_{value}" in facts)
    severities = sorted(value for value in SEVERITIES if f"severity_{value}" in facts)
    if len(materials) > 1 or len(severities) > 1:
        raise ValueError("conflicting report facts")
    damage = sorted(value for value in DAMAGE if f"damage_{value}" in facts)
    return {
        "id": report_id,
        "material": materials[0] if materials else "stone",
        "damage": damage,
        "severity": severities[0] if severities else ("minor" if damage else "none"),
    }


# Store each rule as its premises and conclusion.
def rule(conclusion, *premises):
    return frozenset(premises), conclusion


CLAUSES = [
    rule("inorganic", "material_stone"),
    rule("inorganic", "material_ceramic"),
    rule("inorganic", "material_metal"),
    rule("organic", "material_wood"),
    rule("organic", "material_textile"),
    *[rule("has_damage", f"damage_{d}") for d in sorted(DAMAGE)],
    rule("structural_risk", "damage_crack", "damage_loose_base"),
    rule("invalid:rot_on_inorganic", "damage_rot", "inorganic"),
    rule("invalid:corrosion_on_organic", "damage_corrosion", "organic"),
    rule("invalid:none_but_damaged", "severity_none", "has_damage"),
    rule("invalid:structural_risk_marked_minor", "structural_risk", "severity_minor"),
    # Lab 4 also had invalid:corrosion_on_ceramic and invalid:crack_on_textile here.
    # The Lab 5 reference data contains cracked textiles, so that rule called 6 trusted
    # reports impossible, and corroded ceramic is unusual rather than contradictory.
    # Both claims were about rarity, so they belong to the likelihood layer in quality.py.
]
