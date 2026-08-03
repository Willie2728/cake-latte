# Dedicated Mac and OpenClaw deployment

## Recommended boundary

Use the dedicated Mac mini or MacBook as the control plane. Keep the campaign workspace, encrypted secrets, state database, logs, and OpenClaw runtime on that machine. Store large rendered media in an approved object store or local volume with backups.

```text
Dedicated Mac
  ├─ OpenClaw gateway and scheduler
  ├─ Revenue Flywheel skill
  ├─ Campaign workspace and SQLite state
  ├─ Local secret manager/keychain
  ├─ Blotato adapter (Postiz optional fallback)
  └─ Media working directory

External services
  ├─ OpenAI / optional model providers
  ├─ Firecrawl
  ├─ Blotato, Postiz fallback, or official social APIs
  ├─ Stripe
  └─ Product/site analytics
```

## Prerequisites

- Current Python 3
- OpenClaw configured and running as a supervised service
- `scale-revenue-flywheel` installed in the selected OpenClaw workspace skill root
- Environment variables stored outside the repository
- Authenticated social integrations and platform audits where required
- Reliable time synchronization, disk encryption, backups, and restart policy

## Hardware profile for five API-backed guides

Five logical guides do not require five local foundation models. When reasoning and media generation use external APIs, the dedicated Mac runs orchestration, queues, databases, media validation/transcoding, logs, and health supervision.

Recommended production control plane:

- Mac mini M4 Pro, 24 GB unified memory and 1 TB SSD minimum
- 48 GB unified memory preferred for heavier local models, concurrent builds, or a larger local analysis cache
- Wired Gigabit Ethernet; 10Gb Ethernet is useful only with a fast local NAS or multi-gig internet
- 4 TB external SSD or NAS for active media and local backups
- UPS sized to permit graceful shutdown; automatic restart after power loss
- Existing MacBook Pro as development console and documented failover, not the primary always-on host

Network and storage planning baseline:

- 100 Mbps symmetric minimum; 300 Mbps or faster with unlimited data recommended
- Six 65 MB master assets per day with three working copies is about 35 GB/month before long-term archive
- Twenty masters per day under the same assumption is about 114 GB/month
- Retain 90 days hot, archive older masters to object storage, and keep a separate backup

Local image/video generation changes this recommendation. Sustained local generative video should use a separate GPU workstation or service; do not oversize the control-plane Mac to solve a GPU-rendering workload it is not intended to carry.

## Schedule

Configure OpenClaw cron/background tasks using the current OpenClaw scheduler syntax. Recommended logical jobs:

| Job | Cadence | Action |
| --- | --- | --- |
| `flywheel-health` | Every 15 min | Check runtime, queue, auth presence, stale publications |
| `flywheel-research` | Every 6 hr | Refresh evidence and opportunity backlog |
| `flywheel-produce` | Every 2 hr | Fill approved experiment capacity |
| `flywheel-publish` | Every 15 min | Publish only due, approved items within caps |
| `flywheel-metrics` | Every 4 hr | Ingest platform, site, product, and revenue snapshots |
| `flywheel-optimize` | Nightly | Score, diagnose bottleneck, reallocate portfolio |
| `flywheel-review` | Weekly | Economics, cohort, risk, and strategy report |

Do not create a tight loop that continuously posts. Continuous operation means the service is always supervising and preparing work.

## Restart and idempotency

- Persist all state before external calls.
- Use stable content IDs and platform idempotency keys.
- Mark a publication `sending` before the call and reconcile status after restart.
- Quarantine ambiguous results; check the platform before retrying.
- Back off on rate limits and provider errors.
- Pause after repeated authentication or policy errors.

## Secrets

Prefer macOS Keychain, a dedicated secret manager, or OpenClaw's supported secret injection. Never commit `.env` or keys. The skill's `health` command reports only whether required names exist.

## Observability

Monitor:

- Job start, completion, duration, and result
- Queue depth and age
- Approval wait time
- Publish success, failure, and ambiguity
- Tracking completeness
- Cost per content item and daily limit
- Funnel anomalies and MRR reconciliation
- Platform warnings and account health

Send alerts to a user-approved channel. Do not include keys, full customer records, or sensitive event payloads.

## Initial rollout

1. Start with one product, one audience, one offer, and TikTok draft mode.
2. Validate tracking end to end with test Stripe events.
3. Publish five to ten human-reviewed experiments.
4. Enable scheduled publishing only for the validated template and account.
5. Add Instagram Reels, then YouTube Shorts, one at a time.
6. Add a second producer agent only when the first workflow is stable.
7. Expand offers or accounts after revenue attribution and retention are credible.
