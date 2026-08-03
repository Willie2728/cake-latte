# Measurement and optimization

## North-star hierarchy

Use the deepest metric with adequate sample size:

1. Contribution margin or attributable new MRR
2. Purchases, paid conversions, or activated trials
3. Qualified signups
4. Qualified landing sessions
5. Link clicks and profile visits
6. Completion, saves, shares, and meaningful comments
7. Views and impressions

Virality is a distribution outcome. Revenue requires an offer, landing experience, activation path, retention, and attribution. A viral post with no qualified action is not a winner.

## Required identifiers

Assign one immutable `content_id` before publishing. Carry it through:

- `utm_content=<content_id>`
- Site analytics campaign properties
- Signup/activation event properties
- Stripe `client_reference_id` or Checkout Session metadata
- Publication and metrics ledgers

Do not place secrets or personal data in UTM values or Stripe client reference IDs.

## $5,000 MRR model

Let:

- `T` = target MRR
- `C` = current MRR
- `A` = average monthly revenue per customer
- `r` = monthly churn rate
- `n` = months to target
- `x` = required new paying customers per month

Approximate retained current MRR at the target date:

```text
C_retained = C × (1-r)^n
```

Assuming the same number of customers is added monthly:

```text
x = (T - C_retained) / (A × Σ[j=0..n-1](1-r)^j)
```

This is a planning model, not a forecast. Add tax, refunds, failed payments, annual plans, upgrades, downgrades, and cohort retention when real data exists.

## Funnel math

For each content item and experiment cell, calculate:

```text
view_rate = views / impressions
completion_rate = completions / views
share_rate = shares / views
click_rate = link_clicks / views
signup_rate = signups / link_clicks
trial_rate = trials / signups
purchase_rate = purchases / trials or purchases / signups
revenue_per_1k = (new_mrr + one_time_revenue - refunds) / impressions × 1000
contribution_per_1k = (revenue × gross_margin - content_cost - attributed_spend) / impressions × 1000
```

Avoid comparing raw counts across platforms or observation windows. Use rates, cohorts, and matched time windows.

## Evidence thresholds

Defaults are deliberately conservative and configurable:

- Attention decision: at least 1,000 views
- Traffic decision: at least 50 clicks
- Revenue decision: at least 3 purchases
- Pattern promotion: at least 3 independent posts, not three edits of one post

When evidence is below the threshold, label the result `learning`, not `winner` or `loser`.

## Portfolio allocation

- Exploit: 60% of capacity to proven audience/problem/format combinations
- Explore: 20% to new audiences, formats, or channels
- Challenger: 20% to a deliberate alternative to the current best pattern

Promote a challenger only when it beats the control on the deepest credible metric. Retain a small exploration allocation even after a winner emerges.

## Diagnosis tree

| Symptom | Likely layer | Next experiment |
| --- | --- | --- |
| Low impressions | Distribution/account/format | Channel-native format, timing, packaging |
| Views but low completion | Hook/pacing | Opening promise, first frame, duration |
| Completion but low clicks | CTA/offer bridge | Specific next step, proof, link path |
| Clicks but low signup | Landing/message match | Match hook language, load speed, friction |
| Signups but low activation | Product onboarding | Shorter time-to-value, guided activation |
| Trials but low paid | Value/price/retention | Paywall, packaging, lifecycle messaging |
| Revenue but low margin | Cost or refund quality | Targeting, promise accuracy, cost controls |

Change one major variable per cell whenever possible.

## Reporting

Daily report:

- System and connector health
- Posts published, failed, and awaiting approval
- Material metric changes and anomalies
- Spend/cost against limits
- Immediate pause conditions

Weekly report:

- MRR and target gap
- Cohort retention and refund signals
- Experiment decisions with evidence
- Capacity allocation for next week
- Funnel bottleneck and next test
- Risks and user decisions required
