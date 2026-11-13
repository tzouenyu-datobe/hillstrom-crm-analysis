
# KQ3 Step 4.1 — Simulation Inputs

# 1. Business assumptions
eligible_audience = 64_000
contribution_margin = 0.40
email_cost = 0.05
budget_cap = 1_600

# 2. Historical customer distribution (KQ2)
customer_counts = {
    "new": 32_144,
    "existing": 31_856,
}

# 3. Spend uplift estimates (KQ2)
spend_uplift = {
    "new": {
        "mens": 0.9600,
        "womens": 0.7323,
    },
    "existing": {
        "mens": 0.5780,
        "womens": 0.1140,
    },
}

# 4. Derived budget constraint
max_emails = int(budget_cap / email_cost)

print("Eligible audience:", eligible_audience)
print("Historical customer counts:", customer_counts)
print("Maximum emails:", max_emails)
print("Spend uplift estimates:", spend_uplift)


# KQ3 Step 4.2 — Incremental Profit Function

def calculate_incremental_profit(
    n_sent,
    uplift,
    margin,
    cost_per_email
):
    incremental_revenue = n_sent * uplift
    incremental_contribution = incremental_revenue * margin
    campaign_cost = n_sent * cost_per_email

    incremental_profit = (
        incremental_contribution - campaign_cost
    )

    return incremental_profit


# Test: New customers receiving Men's Email
test_profit = calculate_incremental_profit(
    n_sent=1000,
    uplift=spend_uplift["new"]["mens"],
    margin=contribution_margin,
    cost_per_email=email_cost
)

print("Test incremental profit:", test_profit)


# KQ3 Step 4.3 — Customer Distribution

new_share = customer_counts["new"] / eligible_audience
existing_share = customer_counts["existing"] / eligible_audience

assert sum(customer_counts.values()) == eligible_audience
assert abs(new_share + existing_share - 1) < 1e-10

print("New customer share:", round(new_share, 4))
print("Existing customer share:", round(existing_share, 4))


# KQ3 Step 4.3 — Policy Allocations

random_new = round(max_emails * new_share)
random_existing = max_emails - random_new

newbie_first_new = min(customer_counts["new"], max_emails)
newbie_first_existing = max_emails - newbie_first_new

policies = {
    "P0_No_Email": {
        "new": 0,
        "existing": 0,
        "email_type": None,
    },
    "P1_Random_Mens": {
        "new": random_new,
        "existing": random_existing,
        "email_type": "mens",
    },
    "P2_Random_Womens": {
        "new": random_new,
        "existing": random_existing,
        "email_type": "womens",
    },
    "P3_Newbie_First_Mens": {
        "new": newbie_first_new,
        "existing": newbie_first_existing,
        "email_type": "mens",
    },
}

for name, policy in policies.items():
    print(
        name,
        "New:", policy["new"],
        "Existing:", policy["existing"],
        "Total:", policy["new"] + policy["existing"]
    )


# KQ3 Step 4.3 — Allocation Validation

for name, policy in policies.items():
    total_sent = policy["new"] + policy["existing"]

    assert total_sent <= max_emails, name
    assert policy["new"] <= customer_counts["new"], name
    assert policy["existing"] <= customer_counts["existing"], name
    assert total_sent * email_cost <= budget_cap, name

print("All policy allocations passed validation.")


# KQ3 Step 4.4 — Policy Profit Calculation

policy_results = []

for name, policy in policies.items():
    email_type = policy["email_type"]
    total_sent = policy["new"] + policy["existing"]

    if email_type is None:
        total_profit = 0.0
    else:
        new_profit = calculate_incremental_profit(
            n_sent=policy["new"],
            uplift=spend_uplift["new"][email_type],
            margin=contribution_margin,
            cost_per_email=email_cost
        )

        existing_profit = calculate_incremental_profit(
            n_sent=policy["existing"],
            uplift=spend_uplift["existing"][email_type],
            margin=contribution_margin,
            cost_per_email=email_cost
        )

        total_profit = new_profit + existing_profit

    profit_per_email = (
        total_profit / total_sent if total_sent > 0 else None
    )

    policy_results.append({
        "policy": name,
        "emails_sent": total_sent,
        "incremental_profit": total_profit,
        "profit_per_email": profit_per_email,
    })

for result in policy_results:
    print(
        result["policy"],
        "| Emails:", result["emails_sent"],
        "| Profit:", round(result["incremental_profit"], 2),
        "| Profit/Email:",
        round(result["profit_per_email"], 4)
        if result["profit_per_email"] is not None
        else "N/A"
    )


# KQ3 Step 4.5 — Policy Comparison

profit_lookup = {
    result["policy"]: result["incremental_profit"]
    for result in policy_results
}

baseline_profit = profit_lookup["P1_Random_Mens"]
newbie_first_profit = profit_lookup["P3_Newbie_First_Mens"]

absolute_improvement = newbie_first_profit - baseline_profit

relative_improvement = (
    absolute_improvement / baseline_profit * 100
)

print("P3 vs P1 absolute improvement:", round(absolute_improvement, 2))
print("P3 vs P1 relative improvement:", round(relative_improvement, 2), "%")


# KQ3 Step 5.1 — Contribution Margin Sensitivity

margin_scenarios = [0.20, 0.30, 0.40, 0.50]

margin_results = []

for margin in margin_scenarios:
    for name, policy in policies.items():
        email_type = policy["email_type"]

        if email_type is None:
            profit = 0.0
        else:
            profit = sum(
                calculate_incremental_profit(
                    n_sent=policy[segment],
                    uplift=spend_uplift[segment][email_type],
                    margin=margin,
                    cost_per_email=email_cost
                )
                for segment in ["new", "existing"]
            )

        margin_results.append({
            "margin": margin,
            "policy": name,
            "profit": round(profit, 2)
        })

for result in margin_results:
    print(
        f"Margin: {result['margin']:.0%}",
        f"| {result['policy']}",
        f"| Profit: {result['profit']:.2f}"
    )


# KQ3 Step 5.2 — Email Cost Sensitivity
# Fixed allocation: do not recalculate max_emails

cost_scenarios = [0.02, 0.05, 0.08, 0.10]

cost_results = []

for cost in cost_scenarios:
    for name, policy in policies.items():
        email_type = policy["email_type"]
        total_sent = policy["new"] + policy["existing"]

        if email_type is None:
            profit = 0.0
        else:
            profit = sum(
                calculate_incremental_profit(
                    n_sent=policy[segment],
                    uplift=spend_uplift[segment][email_type],
                    margin=contribution_margin,
                    cost_per_email=cost
                )
                for segment in ["new", "existing"]
            )

        total_cost = total_sent * cost
        within_budget = total_cost <= budget_cap

        cost_results.append({
            "email_cost": cost,
            "policy": name,
            "emails_sent": total_sent,
            "total_cost": total_cost,
            "profit": round(profit, 2),
            "within_budget": within_budget
        })

for result in cost_results:
    print(
        f"Cost: {result['email_cost']:.2f}",
        f"| {result['policy']}",
        f"| Profit: {result['profit']:.2f}",
        f"| Budget feasible: {result['within_budget']}"
    )


# KQ3 Step 5.3 — Break-even Email Cost

for name, policy in policies.items():
    total_sent = policy["new"] + policy["existing"]
    email_type = policy["email_type"]

    if total_sent == 0:
        print(name, "| Break-even Cost: N/A")
        continue

    weighted_uplift = sum(
        policy[segment] * spend_uplift[segment][email_type]
        for segment in ["new", "existing"]
    ) / total_sent

    break_even_cost = weighted_uplift * contribution_margin

    print(
        name,
        "| Break-even Cost:",
        round(break_even_cost, 4)
    )
