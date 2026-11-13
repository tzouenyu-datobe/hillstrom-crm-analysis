
import pandas as pd

df = pd.read_csv("output/newbie_uplift_with_ci.csv")

# Only compare email treatments against No E-Mail
plot_data = df[df["comparator"] == "No E-Mail"].copy()

# Translate segment codes
plot_data["segment"] = plot_data["newbie"].map({
    1: "New",
    0: "Existing"
})

# Calculate confidence interval distances
plot_data["err_lower"] = (
    plot_data["uplift"] - plot_data["ci_lower"]
)
plot_data["err_upper"] = (
    plot_data["ci_upper"] - plot_data["uplift"]
)

print(plot_data.to_string(index=False))


import matplotlib.pyplot as plt

# Arrange four comparisons
plot_data["label"] = (
    plot_data["segment"] + " | " + plot_data["treatment"]
)

plot_data = plot_data.sort_values(
    ["treatment", "newbie"],
    ascending=[True, False]
).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(9, 3.8))

y_pos = range(len(plot_data))

ax.errorbar(
    x=plot_data["uplift"],
    y=y_pos,
    xerr=[
        plot_data["err_lower"],
        plot_data["err_upper"]
    ],
    fmt="o",
    color="#2563EB",
    capsize=5,
    markersize=7,
    linewidth=2
)

# Zero-effect reference
ax.axvline(
    0,
    color="#9CA3AF",
    linestyle="--",
    linewidth=1
)


# Point-estimate labels
for i, row in plot_data.iterrows():
    ax.annotate(
        f'{row["uplift"]:+.3f}',
        xy=(row["uplift"], i),
        xytext=(0, -16),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        color="#1D4ED8"
    )

ax.set_yticks(list(y_pos))
ax.set_yticklabels(plot_data["label"])
ax.invert_yaxis()

ax.set_xlim(-0.4, 1.5)
ax.set_xlabel("Incremental Spend per Customer")
ax.set_title(
    "Email Incrementality by Customer Segment",
    loc="left",
    fontsize=13,
    fontweight="bold",
    pad=15
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

ax.tick_params(axis="y", length=0)
ax.grid(axis="x", alpha=0.12)


# Methodological note
fig.text(
    0.27, 0.02,
    "Note: ITT uplift vs No Email; 95% CI. "
    "New vs Existing differences are not "
    "statistically established after multiple-testing adjustment.",
    fontsize=8,
    color="#6B7280"
)

plt.tight_layout(rect=[0, 0.12, 1, 1])

fig.savefig(
    "output/Figure_2_KQ2_Segment_Heterogeneity.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

