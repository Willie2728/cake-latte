---
name: scale-revenue-flywheel
description: Build, operate, and optimize a governed multi-agent content-to-revenue system across TikTok, Instagram Reels, YouTube Shorts, and other social channels. Use when an agent must research a market, create short-form content variants, schedule or publish through approved APIs, attribute traffic and Stripe revenue, run experiments, target MRR, coordinate multiple specialist agents, or maintain a continuous 24/7 growth loop without copying proprietary marketing skills.
---

# Scale Revenue Flywheel

Build a measurable loop: research → create → review → distribute → attribute → learn → reallocate. Optimize for qualified revenue, not views alone. Never promise virality, revenue, or a completion date.

## Operating contract

1. Keep credentials in environment variables or an approved local vault. Never print, store, or transmit secret values in campaign files.
2. Use official APIs or a user-authorized publisher such as Blotato or Postiz. Do not automate consumer UI interactions, fake engagement, account warmup, evasion, or rate-limit bypasses.
3. Make research, drafting, scoring, and scheduling autonomous. Require the approval level in the campaign configuration for publishing, price changes, spend, customer messages, claims, or destructive actions.
4. Respect platform disclosure, consent, audit, copyright, music, synthetic-media, and commercial-content requirements. Read [platform-policies.md](references/platform-policies.md) before enabling a publishing channel.
5. Treat every performance claim as a hypothesis until verified by attributable events.
6. Preserve an audit trail linking every post to its hypothesis, creative, CTA, destination, approval, cost, and measured outcome.

## Start or resume a campaign

### 1. Establish the economics

Collect only the information required to model the goal:

- Offer, product URL, audience, problem, and differentiated result
- Current MRR, target MRR, target date, monthly price/ARPU, churn, and gross margin
- Conversion events: landing view, signup, activation, trial, purchase, renewal, refund
- Approved platforms, accounts, daily caps, and publishing modes
- Brand voice, prohibited claims, regulated topics, and review owner

If values are missing, state assumptions and initialize a draft campaign. Use:

```bash
python scripts/flywheel.py init --workspace <campaign-dir> \
  --business "Wilkerson Collective Inc." --offer "<offer>" \
  --landing-url "https://example.com" --target-mrr 5000 \
  --arpu 49 --target-days 90
```

Then edit `<campaign-dir>/campaign.json`. Validate with:

```bash
python scripts/flywheel.py health --workspace <campaign-dir>
python scripts/flywheel.py model-target --workspace <campaign-dir>
```

Use [campaign.example.json](assets/campaign.example.json) as the field reference. Read [measurement.md](references/measurement.md) before changing KPI weights or target assumptions.

### 2. Research before generating

Use Firecrawl, browser research, search APIs, customer evidence, product analytics, reviews, support themes, and the product itself. Do not copy competitor creative.

Produce:

- Three audience/problem theses
- A hook library grounded in observed language
- Offer-to-audience fit risks
- Format and channel hypotheses
- A list of falsifiable experiments

Store evidence and source URLs in the campaign workspace. Separate observations from inference.

### 3. Orchestrate specialist agents

Follow [architecture.md](references/architecture.md). Use these roles:

- **Orchestrator:** owns priorities, budgets, approvals, and audit trail
- **Market intelligence:** gathers evidence and opportunity gaps
- **Creative strategist:** converts evidence into hypotheses and test cells
- **Producers:** generate channel-native scripts, visuals, captions, and variants
- **Brand and policy reviewer:** checks claims, rights, disclosure, safety, and duplication
- **Publisher:** packages approved variants for connected channels
- **Growth analyst:** measures attention, traffic, activation, revenue, and cost
- **Revenue analyst:** reconciles Stripe events and estimates contribution margin

Run roles in parallel only when they operate on independent artifacts. The orchestrator resolves conflicts and authorizes external writes.

### 4. Generate a portfolio, not isolated posts

Create a structured batch matching [content-batch.example.json](assets/content-batch.example.json). Each item must contain:

- One audience, problem, and hypothesis
- One hook and one primary CTA
- A channel-native body or shot/slide plan
- Media references or generation prompts
- Disclosure and rights status
- A unique experiment cell

Allocate the weekly portfolio approximately:

- 60% exploit proven patterns
- 20% explore new hooks, audiences, or formats
- 20% challenge the current winner

Do not publish near-duplicates across multiple accounts. Adapt structure, opening, pacing, framing, caption, and CTA to each channel.

Enqueue validated content:

```bash
python scripts/flywheel.py enqueue --workspace <campaign-dir> --input <content-batch.json>
```

### 5. Review and approve at the configured boundary

Run the brand/policy review before approval. Reject unsupported claims, impersonation, copyrighted media without rights, fabricated testimonials, deceptive scarcity, or missing synthetic/commercial disclosures.

```bash
python scripts/flywheel.py approve --workspace <campaign-dir> \
  --content-id <id> --approved-by <reviewer>
```

Use `review_required` until each channel integration has passed its required platform audit and the user explicitly changes the campaign configuration. TikTok Direct Post requires creator metadata and consent; an unaudited client is limited to private visibility.

### 6. Publish through approved connectors

Use [platform-adapters.md](references/platform-adapters.md) for Blotato, Postiz, and official API mapping. Blotato is the default launch publisher. Preview the exact outbound payload first:

```bash
python scripts/flywheel.py blotato-payload --workspace <campaign-dir> \
  --content-id <id> --account-id <blotato-account-id>
```

Execute only when the campaign and platform publishing modes permit it:

```bash
python scripts/flywheel.py blotato-send --workspace <campaign-dir> \
  --content-id <id> --account-id <blotato-account-id> \
  --approved-by <reviewer> --execute
```

The command requires `BLOTATO_API_KEY`, an approved content record, and an explicit execution flag. Reconcile the returned asynchronous submission with `blotato-status`; submission is not proof of publication. Postiz remains an optional self-hostable fallback. Record other direct-API publications with `record-publish`.

### 7. Attribute revenue

Every destination URL must include `utm_source`, `utm_medium`, `utm_campaign`, and unique `utm_content=<content-id>`. Pass the content ID into Stripe `client_reference_id` or Checkout Session metadata when applicable.

Ingest cumulative platform and funnel snapshots matching [metrics-batch.example.json](assets/metrics-batch.example.json):

```bash
python scripts/flywheel.py ingest-metrics --workspace <campaign-dir> --input <metrics.json>
python scripts/flywheel.py score --workspace <campaign-dir>
python scripts/flywheel.py report --workspace <campaign-dir>
```

Prefer, in order:

1. Contribution margin or attributable new MRR per 1,000 impressions
2. Paid conversion or activated signup rate
3. Qualified click rate
4. Completion, saves, and shares
5. Views

Use revenue as the winner criterion only when attribution and sample size are credible. Use an upstream proxy while evidence is sparse.

### 8. Operate continuously without posting continuously

Continuous means the system monitors, researches, prepares, evaluates, and recovers around the clock. It does not mean unlimited posts.

Use [deployment.md](references/deployment.md) for the dedicated Mac/OpenClaw schedule. Recommended loop:

- Research and trend refresh: every 6 hours
- Queue and connector health: every 15 minutes
- Publishing: at approved channel windows and daily caps
- Metrics ingestion: every 4–6 hours
- Optimization: nightly
- Strategy and economics review: weekly

Pause automatically when authentication fails, policy risk rises, duplicates appear, metrics drop sharply, destination tracking breaks, or spend exceeds its approved limit.

## Scaling decision

Scale a pattern only after it demonstrates repeatable downstream value across multiple posts. Increase volume, channels, accounts, or agent workers one dimension at a time. Keep a 10–20% exploration budget.

Do not clone content across accounts, conceal automation, or manufacture engagement. Add a new agent only when the existing queue has measurable capacity constraints or a distinct audience/channel thesis.

## Completion criteria

Report:

- What is automated and what still requires approval
- Connected and blocked channels
- Current MRR, target gap, and modeled customer requirement
- Published experiments and attributable outcomes
- Winning and retired hypotheses
- Next allocation decision
- Risks, missing permissions, and required user actions

Never report the $5,000 MRR objective as achieved without verified revenue data.
