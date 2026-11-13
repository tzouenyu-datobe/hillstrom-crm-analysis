# Does Email Marketing Actually Drive Incremental Profit?

**From Conversion Rates to Incremental Profit**

*CRM Analytics Case Study | Randomized Experiment · SQL · Python · Customer Segmentation · Policy Simulation*

## 1. Executive Summary — The Business Decision

**Business problem.** A retail CRM team wants to know **whether to send marketing emails, which email version to use, and which customers to target to generate more profit**. Higher conversion or revenue after a campaign does not necessarily mean the campaign caused those purchases: some customers would have bought anyway. The analysis therefore starts with *incremental spending* and uses explicit business assumptions to assess potential *incremental profit*.

**Data and approach.** This case uses Hillstrom's **64,000-customer randomized retail email experiment** with a **two-week outcome window**. Three connected questions guide the analysis. **KQ1–KQ2 estimate effects from experimental outcomes; KQ3 simulates profit** using estimated effects and hypothetical campaign economics. The profit figures are **not observed business profits**.

| Key question | Main finding | Business decision |
| --- | --- | --- |
| **KQ1 · Does email generate additional spending?** | Relative to No Email, **Men's Email added an estimated 0.770 spend units per assigned customer** over two weeks. | Establish whether sending email creates value beyond purchases that would happen anyway. |
| **KQ2 · Is there a useful customer targeting opportunity?** | We compared **historical spending tiers, new/existing status, and past merchandise preferences**. New/existing status showed a relatively actionable exploratory pattern, but no reliable segment-effect difference was established after the specified statistical checks. | Carry one **testable targeting hypothesis** into the policy simulation, rather than treating the highest estimate as a proven winner. |
| **KQ3 · Which allocation might generate more incremental profit?** | For a **hypothetical 64,000-customer audience**, assuming **40% contribution margin, 0.05 cost per email, a 1,600 budget cap, and 32,000 sends**, **Newbie-first Men's Email** produced **10,688 simulated incremental profit**, **29.49% above** random Men's Email allocation. | Compare four candidates—**No Email, Random Men's, Random Women's, and Newbie-first Men's**—using profit and budget checks; validate the promising policy in a future randomized test. |

**Recommendation.** The randomized experiment found positive incremental spending for both email variants, with a larger effect for **Men's Email**. **Prioritize Men's Email for the next campaign evaluation**, subject to real costs and margins. The Newbie-first policy has the highest simulated profit, but its apparent advantage is not yet proven. **Next, verify actual campaign economics and run a prospective randomized policy comparison of Random Men's versus Newbie-first Men's**, with an appropriate no-email control or holdout to estimate incremental profit before scaling.

## 2. Data Overview — What We Know and What We Assume

**Experimental design.** The **Hillstrom / MineThatData Email Marketing Dataset** contains **64,000 rows**, one per customer, randomly assigned to three groups. The **No E-Mail group** provides a baseline for estimating the *intention-to-treat (ITT)* effect of email assignment. The dataset does not confirm that every assigned customer actually received, opened, or read an email.

| Experimental group | Customers | Role |
| --- | ---: | --- |
| Men's E-Mail | 21,307 | Email version A |
| Women's E-Mail | 21,387 | Email version B |
| No E-Mail | 21,306 | Control |
| **Total** | **64,000** | |

**Key field definitions.** Men's/Women's Email are **message variants, not recipient genders**. The `mens` and `womens` fields indicate **historical purchases of merchandise categories**, not customer gender. In particular, `history_segment` is derived from `history`; these are two representations of one underlying spending measure.

| Fields | Meaning | Use in analysis |
| --- | --- | --- |
| `segment` | Randomized email assignment | KQ1–KQ2: compare treatment with control |
| `spend` | Two-week customer spending, **including zeros** | Primary outcome: incremental spend per assigned customer |
| `conversion`, `visit` | Post-treatment purchase and visit outcomes | Secondary outcomes, **not targeting variables** |
| `history`, `history_segment` | Historical spend and seven original spend tiers | KQ2: past customer value |
| `newbie` | New (`1`) or existing (`0`) customer | KQ2: lifecycle-based segmentation |
| `mens`, `womens` | Historical merchandise purchase flags | KQ2: past category preferences |

**Segmentation design.** I selected **three pre-treatment dimensions** that correspond to meaningful CRM decisions: prior spending, customer lifecycle, and merchandise preference. Each was analyzed separately—**seven spending tiers, two new/existing groups, and three purchase-preference groups** (*Mens Only, Womens Only, Both*). Crossing them would create up to **42 subgroup combinations**, increasing sparse-cell uncertainty and opportunities for overly optimistic findings from repeated exploration.

**Data checks and limitations.**
- **Data validity:** Initial checks found **no SQL NULLs in the 12 fields** and no invalid values in the tested binary columns. Blank strings, categorical balance, and duplicate-row integrity were **not fully verified**.
- **Sparse outcomes:** **63,422/64,000 (99.10%)** customers had zero spend; only **578** purchased. Subgroup estimates can be sensitive to a few transactions.
- **Missing business inputs:** Actual contribution margin, email cost, campaign budget, creative/SKU details, and customer lifetime value are unavailable. **The source currency is not confirmed**, so monetary results retain the original data unit.

**What this supports—and does not.**
- **KQ1:** Randomized groups support a comparison of incremental spending versus No Email.
- **KQ2:** Pre-treatment customer attributes allow exploratory comparison of segment responses, **not automatic proof that targeting works**.
- **KQ3:** With real campaign economics unavailable, allocation results must be labeled **hypothetical profit simulations**.

## 3. Analytical Journey — Key Decisions and Human–AI Iteration

**How the work evolved.** The analysis progressed through repeated business questions, statistical checks, code execution, and review. I defined the decision problem, challenged the interpretations, and chose the evidence thresholds and scope. AI helped explore methods, develop SQL/Python analyses, and identify trade-offs. The following are **decision changes that affected the business recommendation**, not a list of AI tools.

### 3.1 KQ1 — Measure What Marketing Actually Adds

**Decision 1 — Change the success metric.** Conversion and observed revenue alone cannot distinguish marketing-caused purchases from organic demand. I therefore made **incremental spend per randomized customer** the primary metric: the difference in mean `spend` between each email group and No Email, **including customers who spent zero**. Conversion and visit remain secondary outcomes.

**Decision 2 — Check whether sparse spending changes the conclusion.** Because nearly all customers spent nothing, I tested whether the estimated effects remained credible using **bootstrap confidence intervals** and **Holm adjustment for the three primary spend comparisons**. The direction and statistical interpretation held. I did not attribute the differences to email creative or product price because the dataset cannot test those explanations. **Having established campaign-level uplift, the next question was whether customer segments should receive different treatments.**

### 3.2 KQ2 — Compare Three Targeting Ideas Before Selecting One

**Decision question.** If Men's Email creates incremental spending on average, **could targeting improve the allocation further?** Instead of assuming which customers would respond best, I compared three operationally meaningful segmentation ideas using characteristics available *before* the email was sent.

| Segmentation idea | What we learned | Decision |
| --- | --- | --- |
| **Historical spending (7 tiers)** | Some tiers showed large estimated uplift, but many had **very few actual purchasers**, making the results unstable. The overall interaction test did not meet the 5% threshold. | **Do not** choose recipients simply because a historical spending tier has a high uplift estimate. |
| **New vs existing (2 groups)** | **New customers had higher estimated uplift under both email variants.** The groups were large enough to be a practical starting point, though the effect differences were not firmly established. | **Carry forward as a practical exploratory hypothesis** for the KQ3 simulation. |
| **Past merchandise preferences (3 groups)** | Some preference groups looked promising, but comparisons did not provide reliable evidence of differences in email effects. | **Do not** build the first allocation policy around product preference. |

**Decision 3 — Test differences *between* segments, not just uplift *within* them.** A positive effect for new customers does not by itself prove they respond more strongly than existing customers. We checked **treatment-by-segment interactions** and adjusted nine specified comparisons (three Newbie, six purchase-preference) using **Holm**. **None remained significant after adjustment**; the historical-spending interaction was assessed separately (HC3 omnibus **p = 0.0527**). This means the available evidence **does not validate a differentiated targeting rule**, not that all customers are identical.

**Decision 4 — Select a hypothesis, not a winner.** New/existing status was chosen for KQ3 because it is interpretable, available before sending, and showed a consistent directional pattern—not because statistical testing proved it superior to other dimensions. We **stopped additional significance hunting** and treated **Newbie-first Men's Email** as an economic scenario requiring future validation.

### 3.3 KQ3 — Turn a Targeting Hypothesis into a Budget Decision

**Decision 5 — Move from spend to profit, with assumptions visible.** More incremental spending does not necessarily mean more profit. Since the dataset lacks real unit economics, I compared **four specified policies** using *estimated spend uplift × assumed contribution margin − assumed email cost*, subject to a budget cap. The model evaluates **candidate allocations**, not every possible targeting policy.

**Decision 6 — Keep allocation fixed when testing costs.** An early design considered changing send volumes whenever email cost changed. I instead held each policy's allocation fixed to isolate the effect of cost, then checked **budget feasibility separately**. This made an important business distinction visible: a policy may show positive *modeled* profit while **exceeding the available budget**. The budget is a cap, not an obligation to spend it all.

**Decision 7 — Do not turn a simulated winner into a live policy.** Newbie-first was selected and evaluated using the same experiment, which creates a risk of **in-sample selection bias (winner's curse)**. Its profit advantage is a reason to **design a policy-level experiment**, not to roll it out as a proven improvement.

## 4. Evidence — What the Results Show

### KQ1 — Incremental Spending

![Figure 1: Campaign incremental spend](output/Figure_1_KQ1_Incrementality.png)

| Comparison | Spend uplift per assigned customer | 95% CI |
| --- | ---: | --- |
| Men's Email − No Email | **+0.7698** | [0.4851, 1.0545] |
| Women's Email − No Email | **+0.4244** | [0.1690, 0.6799] |
| Women's Email − Men's Email | **−0.3454** | [−0.6583, −0.0326] |

**Finding.** Both email versions increased average spend versus No Email; Men's Email showed the larger estimate. The displayed intervals are **normal-approximation 95% CIs**, with the primary spend conclusions also supported by bootstrap and spend-only Holm checks. **This supports evaluating Men's Email first**, but does not identify which creative or product characteristics explain its performance.

### KQ2 — Why New vs Existing Was Explored

![Figure 2: New vs existing uplift estimates](output/Figure_2_KQ2_Segment_Heterogeneity.png)

| Customer | Men's Email uplift | Women's Email uplift |
| --- | ---: | ---: |
| New (`newbie=1`) | **+0.9600** | +0.7323 |
| Existing (`newbie=0`) | +0.5780 | +0.1140 |

**Finding.** New customers had higher point-estimated uplift for both versions. But for Men's Email, the **new-versus-existing effect difference** was **+0.3820** with a 95% CI of **[−0.1877, 0.9517]**, which includes zero. **The chart illustrates an opportunity worth testing, not evidence that Newbie-first allocation is already superior.**

### KQ3 — Simulated Incremental Profit

![Figure 3: Policy profit comparison](output/Figure_3_KQ3_Policy_Profit.png)

**Four policies under the baseline scenario in Section 1.** P1 and P2 allocate the 32,000 sends **proportionally to the assumed new/existing audience mix**; their “Random” labels describe the *candidate policy*, not an actual random draw in the simulation. P3 prioritizes new customers for Men's Email. Each customer receives at most one email. The assumed new/existing population split (32,144 / 31,856) still needs a raw-data cross-check.

| Policy | Emails sent | **Simulated** incremental profit |
| --- | ---: | ---: |
| P0 · No Email | 0 | 0.00 |
| P1 · Random Men's | 32,000 | 8,254.20 |
| P2 · Random Women's | 32,000 | 3,834.13 |
| P3 · Newbie-first Men's | 32,000 | **10,688.00** |

**Finding.** P3's simulated incremental profit exceeded P1's by **2,433.80 (+29.49%)**. Under the tested fixed allocations and contribution margins of **20–50%**, P3 retained the highest modeled estimate. But at a cost of **0.08 or 0.10 per email**, 32,000 sends would cost **2,560 or 3,200**, above the **1,600 budget**. The scenarios remain useful diagnostics, but those fixed-volume allocations are **not budget-feasible**.

## 5. Business Recommendations — What Should the CRM Team Do Next?

**Act on the experimental evidence.** **Prioritize Men's Email as the next campaign candidate** because its incremental spending estimate exceeds No Email and the alternative email version. Confirm the real contribution margin and send cost before turning this into a profit-based rollout decision.

**Test the targeting hypothesis before rollout.** The Newbie-first policy looked better in the simulation, while KQ2 did not establish a reliable Men's Email effect difference between new and existing customers. Run a **prospective randomized policy comparison between P1 and P3**, keeping audience eligibility, send volume, and budget comparable. Include a suitable **no-email control/holdout** and predefine **incremental profit** as the decision metric.

**Keep the decision conditional.** Reassess feasibility if unit costs or audience composition change. The measured outcome covers **two weeks**, not long-term retention or customer lifetime value. Distinguish **experimentally estimated campaign effects**, **exploratory subgroup signals**, and **simulated policy profits** when communicating the recommendation.

## 6. Repository & Reproducibility

```text
hillstrom-crm/
├── data/          # Original and analysis-ready datasets
├── sql/           # Profiling and treatment-effect analysis
├── scripts/       # Statistical tests, policy simulation, plots
├── output/        # Exported CSV results and figures
├── .gitignore
└── README.md
```

**Recreate the figures.** With the required Python libraries installed, run these commands **from the repository root**:

```bash
python scripts/09_kq1_incrementality_plot.py
python scripts/10_kq2_segment_plot.py
python scripts/11_kq3_policy_plot.py
```

**What is reproducible.** Figure 2 reads `output/newbie_uplift_with_ci.csv`; Figures 1 and 3 plot previously computed values stored inside the scripts. The commands **regenerate the visualizations**, not the full SQL-to-policy analytical pipeline. A fully independent end-to-end run and pinned dependency environment have not yet been verified.
