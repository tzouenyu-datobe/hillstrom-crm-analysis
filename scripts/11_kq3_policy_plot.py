
import pandas as pd

policy_data = pd.DataFrame({
    "policy": [
        "P0 | No Email",
        "P1 | Random Men's",
        "P2 | Random Women's",
        "P3 | Newbie-first Men's"
    ],
    "emails_sent": [0, 32000, 32000, 32000],
    "incremental_profit": [
        0,
        8254.20,
        3834.13,
        10688.00
    ]
})

policy_data["profit_per_email"] = (
    policy_data["incremental_profit"]
    / policy_data["emails_sent"].replace(0, float("nan"))
)

print(policy_data.to_string(index=False))


import matplotlib.pyplot as plt

# Sort policies by estimated incremental profit
plot_data = policy_data.sort_values(
    "incremental_profit",
    ascending=True
).reset_index(drop=True)

# Highlight P3 as the highest simulated estimate
colors = [
    "#2563EB" if policy.startswith("P3") else "#94A3B8"
    for policy in plot_data["policy"]
]

fig, ax = plt.subplots(figsize=(9, 3.8))

bars = ax.barh(
    plot_data["policy"],
    plot_data["incremental_profit"],
    color=colors,
    height=0.55
)

# Value labels
for bar, value in zip(
    bars,
    plot_data["incremental_profit"]
):
    ax.text(
        value + 180,
        bar.get_y() + bar.get_height() / 2,
        f"{value:,.0f}",
        va="center",
        fontsize=10
    )

ax.set_xlim(0, 12500)
ax.set_xlabel("Estimated Incremental Profit")
ax.set_title(
    "Estimated Incremental Profit by Allocation Policy",
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
ax.set_axisbelow(True)


# Compare P3 against P1
p1_profit = policy_data.loc[
    policy_data["policy"].str.startswith("P1"),
    "incremental_profit"
].iloc[0]

p3_profit = policy_data.loc[
    policy_data["policy"].str.startswith("P3"),
    "incremental_profit"
].iloc[0]

profit_lift_pct = (p3_profit / p1_profit - 1) * 100

# Add simulated improvement annotation
fig.text(
    0.20, 0.13,
    f"P3 vs P1: +{profit_lift_pct:.2f}% "
    "estimated incremental profit",
    fontsize=10,
    fontweight="bold",
    color="#2563EB"
)

# Scenario assumptions and limitations
fig.text(
    0.20, 0.055,
    "Assumptions: 40% contribution margin | "
    "Email cost: 0.05 | Budget: 1,600 | "
    "32,000 emails per active policy.",
    fontsize=8,
    color="#6B7280"
)

fig.text(
    0.20, 0.025,
    "Scenario simulation using estimated subgroup effects; "
    "policy superiority is not statistically established.",
    fontsize=8,
    color="#6B7280"
)

plt.tight_layout(rect=[0, 0.19, 1, 1])

fig.savefig(
    "output/Figure_3_KQ3_Policy_Profit.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

