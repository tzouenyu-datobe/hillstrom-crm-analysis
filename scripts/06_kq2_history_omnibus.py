
# KQ2 | Step 2.10
# History Segment: Omnibus Interaction Test
#
# Data source: Hillstrom CSV
# Model: Spend ~ Treatment * History Segment
# Test: HC3-robust joint F-test

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

# 1. Locate data relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Update the filename if your CSV has a different name
DATA_PATH = DATA_DIR / "hillstrom.csv"

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"CSV not found: {DATA_PATH}\n"
        "Check the filename in your data/ folder."
    )

# 2. Load and validate
df = pd.read_csv(DATA_PATH)

required_columns = {"spend", "segment", "history_segment"}
missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

if len(df) != 64000:
    raise ValueError(f"Expected 64000 rows, got {len(df)}")

if df[list(required_columns)].isna().any().any():
    raise ValueError("Missing values in required columns")

print(f"Rows: {len(df):,}")
print(f"Treatments: {df['segment'].nunique()}")
print(f"History segments: {df['history_segment'].nunique()}")

# 3. Regression with interaction
formula = (
    'spend ~ '
    'C(segment, Treatment(reference="No E-Mail"))'
    ' * C(history_segment)'
)

model = smf.ols(formula, data=df).fit(cov_type="HC3")

# 4. Identify all interaction coefficients
interaction_terms = [
    name
    for name in model.params.index
    if ":" in name
]

print(f"Interaction coefficients: {len(interaction_terms)}")

if len(interaction_terms) != 12:
    raise ValueError(
        f"Expected 12 interaction terms, "
        f"got {len(interaction_terms)}"
    )

# 5. Joint hypothesis: all interactions = 0
hypothesis = ", ".join(
    f"{name} = 0"
    for name in interaction_terms
)

test = model.f_test(hypothesis)

print("\n=== History Segment Omnibus Test ===")
print(f"F-statistic: {float(test.fvalue):.4f}")
print(f"p-value: {float(test.pvalue):.6f}")
print(f"Numerator df: {int(test.df_num)}")
print(f"Denominator df: {float(test.df_denom):.0f}")
print(f"Reject H0 at 0.05: {float(test.pvalue) < 0.05}")
