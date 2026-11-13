
import pandas as pd

# KQ1: ITT spend uplift relative to No Email
plot_data = pd.DataFrame({
    "comparison": [
        "Men's Email vs No Email",
        "Women's Email vs No Email"
    ],
    "uplift": [0.7698, 0.4244],
    "ci_lower": [0.4851, 0.1690],
    "ci_upper": [1.0545, 0.6799]
})

# Calculate asymmetric error-bar distances
plot_data["err_lower"] = plot_data["uplift"] - plot_data["ci_lower"]
plot_data["err_upper"] = plot_data["ci_upper"] - plot_data["uplift"]

print(plot_data.to_string(index=False))


import matplotlib.pyplot as plt

# Plot positions
y_pos = range(len(plot_data))


fig, ax = plt.subplots(figsize=(9, 2.8))

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
    markersize=8,
    linewidth=2
)

# Zero-effect reference
ax.axvline(0, color="#9CA3AF", linestyle="--", linewidth=1)

# Add point-estimate labels
for i, row in plot_data.iterrows():
    ax.annotate(
        f'+{row["uplift"]:.3f}',
        xy=(row["uplift"], i),
        xytext=(0, -17),
        textcoords="offset points",
        ha="center",
        fontsize=10,
        color="#1D4ED8"
    )

ax.set_yticks(list(y_pos))
ax.set_yticklabels(plot_data["comparison"])
ax.invert_yaxis()

ax.set_xlim(-0.08, 1.20)
ax.set_ylim(1.45, -0.45)

ax.set_xlabel("Incremental Spend per Customer")
ax.set_title(
    "Incremental Impact of Email Campaigns",
    loc="left",
    fontsize=13,
    fontweight="bold",
    pad=16
)

# Remove unnecessary borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

ax.tick_params(axis="y", length=0)
ax.grid(axis="x", alpha=0.12)


# Statistical and methodological note
fig.text(
    0.24, 0.02,
    "Note: Points represent ITT spend uplift; "
    "error bars show 95% confidence intervals. "
    "Outcome window: 2 weeks.",
    fontsize=8,
    color="#6B7280"
)

plt.tight_layout(rect=[0, 0.10, 1, 1])

# Export before displaying
fig.savefig(
    "Figure_1_KQ1_Incrementality.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

