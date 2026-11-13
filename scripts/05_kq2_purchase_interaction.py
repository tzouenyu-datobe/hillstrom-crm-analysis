
# KQ2 | Step 2.9
# Purchase Preference: Interaction Contrasts
#
# Data source:
# PostgreSQL Step 2.8 output (uplift, SE)
# Reference group: Mens Only
#
# No raw CSV or database connection required.

from math import sqrt

results = {
    "Mens vs No Email": {
        "Both": (1.8250, 0.6810),
        "Mens Only": (0.6827, 0.2222),
        "Womens Only": (0.6157, 0.1766),
    },
    "Womens vs No Email": {
        "Both": (0.1619, 0.4976),
        "Mens Only": (0.2784, 0.2051),
        "Womens Only": (0.6316, 0.1717),
    },
    "Womens vs Mens": {
        "Both": (-1.6631, 0.6792),
        "Mens Only": (-0.4044, 0.2430),
        "Womens Only": (0.0159, 0.2085),
    },
}

reference_group = "Mens Only"

for comparison, groups in results.items():
    ref_effect, ref_se = groups[reference_group]

    for group in ["Both", "Womens Only"]:
        effect, se = groups[group]

        interaction = effect - ref_effect
        interaction_se = sqrt(se**2 + ref_se**2)

        ci_lower = interaction - 1.96 * interaction_se
        ci_upper = interaction + 1.96 * interaction_se

        print(f"{comparison} | {group} vs {reference_group}")
        print(f"  Interaction: {interaction:.4f}")
        print(
            f"  95% CI: "
            f"[{ci_lower:.4f}, {ci_upper:.4f}]"
        )
        print(
            f"  Excludes zero: "
            f"{ci_lower > 0 or ci_upper < 0}"
        )
        print()
