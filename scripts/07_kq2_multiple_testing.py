
# KQ2 | Step 2.11
# Holm correction for 9 exploratory interaction contrasts
#
# Data source:
# Step 2.5 and Step 2.8 PostgreSQL outputs
# Interaction SE = sqrt(SE_group1^2 + SE_group2^2)
#
# Note: Uses rounded SE values from prior outputs.

from math import sqrt, erfc

tests = [
    # Newbie: New - Existing
    ("Newbie | Mens vs Control", 0.3820, 0.1869, 0.2226),
    ("Newbie | Womens vs Control", 0.6183, 0.1689, 0.1987),
    ("Newbie | Womens vs Mens", 0.2363, 0.2239, 0.2276),

    # Purchase preference: Both - Mens Only
    ("Both | Mens vs Control", 1.1423, 0.6810, 0.2222),
    ("Both | Womens vs Control", -0.1165, 0.4976, 0.2051),
    ("Both | Womens vs Mens", -1.2587, 0.6792, 0.2430),

    # Purchase preference: Womens Only - Mens Only
    ("Womens Only | Mens vs Control", -0.0670, 0.1766, 0.2222),
    ("Womens Only | Womens vs Control", 0.3532, 0.1717, 0.2051),
    ("Womens Only | Womens vs Mens", 0.4203, 0.2085, 0.2430),
]

results = []

for name, effect, se1, se2 in tests:
    se = sqrt(se1**2 + se2**2)
    z = effect / se
    p = erfc(abs(z) / sqrt(2))

    results.append({
        "name": name,
        "effect": effect,
        "p": p
    })

# Holm step-down adjusted p-values
ordered = sorted(results, key=lambda x: x["p"])
m = len(ordered)
running_max = 0.0

for i, result in enumerate(ordered):
    adjusted = min(1.0, (m - i) * result["p"])
    running_max = max(running_max, adjusted)
    result["holm_p"] = running_max

print("=== KQ2 Interaction: Holm Correction ===")

for result in ordered:
    print(result["name"])
    print(f"  Interaction: {result['effect']:.4f}")
    print(f"  Raw p-value: {result['p']:.6f}")
    print(f"  Holm-adjusted p: {result['holm_p']:.6f}")
    print(f"  Significant: {result['holm_p'] < 0.05}")
    print()
