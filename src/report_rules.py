# Domain vocabulary and Horn clauses for report validation live here.
MATERIALS = {"stone", "ceramic", "metal", "wood", "textile"}
DAMAGE = {"crack", "loose_base", "fading", "rot", "corrosion"}
SEVERITIES = {"none", "minor", "major"}


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
    # Corrosion describes a metal component, rather than a ceramic substrate.
    rule("invalid:corrosion_on_ceramic", "damage_corrosion", "material_ceramic"),
]
