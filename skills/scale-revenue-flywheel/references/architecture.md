# Multi-agent architecture

## System boundary

Use one orchestrator and several narrow specialists. Do not let every agent publish, read secrets, change offers, or modify budgets.

```text
OpenClaw scheduler
  └─ Orchestrator
      ├─ Market intelligence agent ── Firecrawl/search/product evidence
      ├─ Creative strategist ──────── experiment backlog and allocation
      ├─ Producer pool ────────────── scripts, visuals, captions, variants
      ├─ Brand/policy reviewer ───── claims, rights, disclosure, duplication
      ├─ Publisher ───────────────── Postiz or official channel APIs
      ├─ Growth analyst ──────────── platform and product analytics
      └─ Revenue analyst ─────────── Stripe attribution and margin
```

## Shared artifacts

| Artifact | Owner | Consumers |
| --- | --- | --- |
| `campaign.json` | Orchestrator | All agents, read-only except orchestrator |
| Evidence ledger | Intelligence | Strategist, reviewer |
| Experiment backlog | Strategist | Producers, orchestrator |
| Content batch | Producers | Reviewer, publisher |
| Approval ledger | Reviewer/user | Publisher, orchestrator |
| Publication ledger | Publisher | Analysts |
| Metrics snapshots | Analysts | Strategist, orchestrator |
| Learning ledger | Growth analyst | All agents |

## Agent contracts

### Orchestrator

Inputs: campaign economics, queue health, latest metrics, policies.  
Outputs: prioritized work, agent assignments, approval requests, pause/resume decisions.  
May: write campaign state, allocate work.  
May not: invent performance, expose secrets, silently widen approval.

### Market intelligence

Inputs: product, audience, research questions.  
Outputs: cited observations, language patterns, opportunity gaps, uncertainty.  
May: read public sources and approved analytics.  
May not: copy competitor creative or collect unnecessary personal data.

### Creative strategist

Inputs: evidence ledger, learning ledger, economics.  
Outputs: falsifiable hypotheses, experiment cells, weekly portfolio allocation.  
Prefer one major variable per experiment. Keep an explicit control.

### Producer pool

Inputs: one experiment cell and channel brief.  
Outputs: channel-native structured content, media prompts, captions, CTA.  
May not: publish or claim results that are not in evidence.

### Brand and policy reviewer

Inputs: content, sources, rights records, campaign prohibitions, platform policy.  
Outputs: approve, revise, or reject with exact reasons.  
Escalate regulated topics, likeness use, health/financial claims, minors, political content, uncertain rights, or missing disclosures.

### Publisher

Inputs: approved content, connected account, schedule, platform payload.  
Outputs: platform post ID, URL, timestamp, payload checksum, error.  
May not: bypass approval, daily caps, platform consent, audit, or privacy restrictions.

### Growth analyst

Inputs: platform, site, product, and campaign events.  
Outputs: normalized funnel metrics, confidence, winners, losers, anomalies.  
Optimize for the deepest sufficiently sampled metric.

### Revenue analyst

Inputs: Stripe Checkout/Payment Link events, refunds, price, margin, attribution ID.  
Outputs: new MRR, recognized revenue, contribution margin, payback, attribution confidence.  
Never treat gross purchases as profit.

## Concurrency rules

- Parallelize independent research questions, format variants, and platform adaptations.
- Serialize campaign-priority changes, approvals, publishing, budget changes, and winner promotion.
- Limit one writer per shared artifact or use append-only event records.
- Use idempotency keys for publishing and webhook processing.
- Retry transient failures with exponential backoff; quarantine ambiguous outcomes to prevent duplicate posts.

## Scaling gates

Add volume only when:

1. Tracking from content ID to downstream event is healthy.
2. At least three independent posts support the pattern.
3. Unit economics are positive or the experiment has an explicit learning budget.
4. Brand/policy rejection and duplicate rates are within limits.
5. The channel account has no unresolved policy warnings.

Add a new account or agent only for a distinct market, offer, language, or channel strategy—not to flood the same audience.
