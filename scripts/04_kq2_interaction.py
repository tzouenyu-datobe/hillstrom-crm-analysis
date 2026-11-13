
# KQ2 | Step 2.6
# Newbie interaction contrasts
# Based on previously calculated uplift and SE

from math import sqrt

comparisons = {
    "Mens vs No Email": {
        "existing": (0.5780, 0.2226),
        "new": (0.9600, 0.1869)
    },
    "Womens vs No Email": {
        "existing": (0.1140, 0.1987),
        "new": (0.7323, 0.1689)
    },
    "Womens vs Mens": {
        "existing": (-0.4640, 0.2276),
        "new": (-0.2277, 0.2239)
    }
}

for name, values in comparisons.items():
    old_effect, old_se = values["existing"]
    new_effect, new_se = values["new"]

    interaction = new_effect - old_effect
    interaction_se = sqrt(old_se**2 + new_se**2)

    ci_lower = interaction - 1.96 * interaction_se
    ci_upper = interaction + 1.96 * interaction_se

    print(name)
    print(f"  Interaction: {interaction:.4f}")
    print(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"  Excludes zero: {ci_lower > 0 or ci_upper < 0}")
    print()
