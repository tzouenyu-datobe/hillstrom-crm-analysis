
import pandas as pd
import numpy as np

# 1. Read exported data
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
csv_path = project_root / "data" / "hillstrom_spend.csv"

df = pd.read_csv(csv_path)
# 2. Validate data
assert len(df) == 64000
assert df["spend"].notna().all()
assert set(df["segment"]) == {
    "Mens E-Mail",
    "Womens E-Mail",
    "No E-Mail"
}

# 3. Prepare treatment groups
groups = {
    name: group["spend"].to_numpy()
    for name, group in df.groupby("segment")
}

# 4. Bootstrap settings
rng = np.random.default_rng(42)
n_bootstrap = 2000

comparisons = [
    ("Mens E-Mail", "No E-Mail"),
    ("Womens E-Mail", "No E-Mail"),
    ("Womens E-Mail", "Mens E-Mail")
]

# 5. Bootstrap group means
bootstrap_means = {}

for name, values in groups.items():
    n = len(values)
    means = np.empty(n_bootstrap)

    for i in range(n_bootstrap):
        sample = rng.choice(values, size=n, replace=True)
        means[i] = sample.mean()

    bootstrap_means[name] = means

# 6. Estimate differences and percentile CI
for treatment, comparison in comparisons:
    observed_diff = (
        groups[treatment].mean()
        - groups[comparison].mean()
    )

    bootstrap_diff = (
        bootstrap_means[treatment]
        - bootstrap_means[comparison]
    )

    ci_lower, ci_upper = np.percentile(
        bootstrap_diff, [2.5, 97.5]
    )

    print(f"{treatment} vs {comparison}")
    print(f"  Observed uplift: {observed_diff:.4f}")
    print(f"  Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print()


# KQ1 | Robustness Check Step 2
# Holm correction for 3 Spend comparisons

from math import erfc, sqrt

# Values from PostgreSQL Step 2.2
# Difference and SE are rounded to 4 decimals.
tests = [
    ("Mens vs No Email", 0.7698, 0.1452),
    ("Womens vs No Email", 0.4244, 0.1303),
    ("Womens vs Mens", -0.3454, 0.1596),
]

# 1. Calculate two-sided p-values
results = []

for name, difference, se in tests:
    z = difference / se
    p_value = erfc(abs(z) / sqrt(2))

    results.append({
        "comparison": name,
        "p_value": p_value
    })

# 2. Sort p-values (smallest first)
results.sort(key=lambda x: x["p_value"])

# 3. Holm adjustment
m = len(results)
running_max = 0.0

for i, result in enumerate(results):
    adjusted = (m - i) * result["p_value"]
    running_max = max(running_max, adjusted)

    result["holm_p"] = min(running_max, 1.0)

# 4. Print results
print("\nHolm Multiple Comparison Correction")
print("-" * 55)

for result in results:
    significant = result["holm_p"] < 0.05

    print(result["comparison"])
    print(f"  Raw p-value: {result['p_value']:.6f}")
    print(f"  Holm-adjusted p-value: {result['holm_p']:.6f}")
    print(f"  Significant at 0.05: {significant}")
    print()
