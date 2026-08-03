# Revenue Flywheel launch assessment

Verified 3 August 2026 for Wilkerson Collective Inc.

## Executive decision

Build this as an original, governed multi-guide operating system—not as a copy of another marketer's play. Use one orchestrator with five specialist Knowledge Guides, Blotato as the initial publishing API, Firecrawl for public-source intelligence, OpenAI as the default model and media provider, Stripe plus product analytics for revenue attribution, and the existing MacBook Pro for development/failover.

The MacBook Pro is sufficient for a pilot. For reliable 24/7 production, purchase a dedicated Mac mini after the accounts and tracking path work end to end. Five API-backed guides do not require five GPUs or five separate computers.

Continuous operation means the system is always monitoring, preparing, checking, measuring, and recovering. It does not mean posting without limits. Account health, content quality, rights, platform policy, and verified downstream revenue are the scale gates.

## Five-guide design

| Guide | Owns | Primary services | May not do alone |
| --- | --- | --- | --- |
| Signal Guide | Market, audience, competitor, and trend evidence | Firecrawl, search, product data | Copy competitor creative or scrape private data |
| Story Guide | Hypotheses, hooks, experiment portfolio, briefs | OpenAI model router | Invent claims or declare a winner without evidence |
| Media Guide | Scripts, images, video, voice, captions, channel variants | GPT Image 2, Sora adapter, Base44, optional Crayo | Use unlicensed media or publish |
| Distribution Guide | Validation, scheduling, idempotent publishing, status | Blotato; Postiz/direct APIs as fallback | Bypass approval, platform audit, or daily caps |
| Revenue Guide | Funnel metrics, Stripe reconciliation, marginal economics | Stripe, product analytics, platform metrics | Treat views or checkout clicks as revenue |

One orchestrator owns campaign priorities, budgets, approvals, account-health circuit breakers, and the append-only audit trail.

## Vendor assessment

### Blotato — use first

The official Starter plan is **$29/month** with a seven-day trial, 20 connected social accounts, 1,250 AI media credits, API/MCP access, and up to 900 TikTok posts per month. The trial excludes the API; generating the API key starts the paid subscription. The API publishes to nine platforms and returns an asynchronous `postSubmissionId` that must be polled to a terminal result.

Important scaling detail: Blotato's current help documentation limits Starter to three unique TikTok accounts per 24 hours and ten posts per account. Creator is **$97/month**, includes 40 social accounts and 5,000 media credits, and removes that Starter account restriction. Therefore:

- Pilot: Starter, no more than three TikTok accounts active in one day.
- Five TikTok accounts posting daily: budget for Creator or obtain written confirmation of a different allowance.
- Do not generate an API key during the trial until ready for the paid plan.

Sources: [pricing](https://www.blotato.com/pricing), [API quickstart](https://help.blotato.com/api/start), [publishing API](https://help.blotato.com/api/api-reference/publish-post), [posting limits](https://help.blotato.com/support/errors).

### Crayo — production workstation, API pending

Published annual pricing:

| Plan | Effective monthly price | Workflow credits | Export | Voice | Images | Storage | Tracked accounts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hobby | $13 | 50 | 40 min | 30 min | 100 | 25 GB | 1 |
| Clipper | $27 | 150 | 120 min | 120 min | 300 | 100 GB | 3 |
| Pro | $55 | 250 | 240 min | 180 min | 500 | 500 GB | 10 |

Crayo's official public pricing does not list a free plan or public automation API, and no supported public API documentation was found. Do not architect a 24/7 dependency around an assumed key. Use it manually for high-value clipping and templates until the account exposes documented API access and its terms are verified.

Source: [Crayo pricing](https://crayo.ai/pricing).

### Base44 — useful burst capacity, not bulk default

Current Base44 allowances:

| Plan | Annual price per month | Monthly price | Message credits | Integration credits |
| --- | ---: | ---: | ---: | ---: |
| Free | $0 | $0 | 25 | 100 |
| Starter | $16 | $20 | 100 | 2,000 |
| Builder | $40 | $50 | 250 | 10,000 |
| Pro | $80 | $100 | 500 | 20,000 |
| Elite | $160 | $200 | 1,200 | 50,000 |

Base44 supports built-in image and video generation. AI-chat video generation requires Starter or higher and consumes the prompt's message credits plus one additional credit. Video generated inside a live app consumes **five integration credits per generated second**. A 90-second output therefore represents 450 integration credits; five such outputs would exceed Starter's 2,000-credit monthly allowance before any other integration use.

Base44 does not publish a firm maximum generated-video duration in the cited documentation. Treat the observed 90-second result as account-specific evidence and validate the exact workflow before relying on it. Use Base44 for burst production or app-native generation, not as the assumed unlimited renderer.

Sources: [pricing](https://base44.com/pricing), [billing allowances](https://docs.base44.com/Account-and-billing/Billing-and-plans), [built-in media integrations](https://docs.base44.com/Integrations/built-in-integrations).

### Firecrawl — remain free initially

The current free plan provides 1,000 credits per month, roughly 1,000 standard scraped pages, with two concurrent requests. Hobby is $16/month when billed annually for 5,000 pages and five concurrent requests. Standard is $83/month annually for 100,000 pages and 50 concurrent requests.

Start free. Cache results, crawl only source pages needed for active hypotheses, and upgrade based on measured credit exhaustion—not agent count.

Source: [Firecrawl pricing](https://www.firecrawl.dev/pricing).

### OpenAI — primary intelligence and media router

- Use **GPT-5.6 Sol** for orchestration, complex strategy, and high-stakes review.
- Use Terra or Luna roles for high-volume classification/adaptation only after evaluations show acceptable quality.
- Use **GPT Image 2** as the default image generator. The API free tier is not supported; Tier 1 currently allows five images per minute.
- The documented Sora 2 rate is $0.10 per generated second at 720p; Sora 2 Pro is $0.30 per second. A 90-second equivalent would cost $9 or $27 before retries, but long-form output may need multiple clips and editing.
- A ChatGPT subscription does not fund OpenAI API calls. Create an API Platform project, service account/key, monthly budget, and alert thresholds separately.

Sources: [current model catalog](https://developers.openai.com/api/docs/models), [GPT Image 2](https://developers.openai.com/api/docs/models/gpt-image-2), [Sora 2](https://developers.openai.com/api/docs/models/sora-2).

## Social account topology

### TikTok

TikTok does not provide multiple channels inside one creator account in the YouTube sense. Plan on one profile per TikTok account, each separately created, secured, authorized, and represented by its own Blotato account ID. Multiple producer guides may serve one account, but the Distribution Guide must serialize writes and enforce its daily cap.

TikTok Direct Post requires an approved `video.publish` scope and creator authorization. Posts from unaudited API clients are private-only. Blotato can remove much of the integration work, but it does not remove content, disclosure, consent, or account-health obligations.

Source: [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started).

### YouTube

One Google Account can manage up to **100 YouTube channels**. Each channel still needs the correct identity/OAuth mapping in the publisher. The current Data API default includes 100 `videos.insert` calls per day in its granular upload quota. Uploads from unverified API projects remain private until the project passes audit.

Sources: [multiple channels](https://support.google.com/youtube/answer/3046356), [Data API overview](https://developers.google.com/youtube/v3/getting-started), [video upload](https://developers.google.com/youtube/v3/docs/videos/insert).

### Launch channel order

1. TikTok, Instagram Reels, YouTube Shorts, and Facebook Reels.
2. LinkedIn only for business/operator narratives and product evidence.
3. X, Threads, Reddit, Pinterest, and Bluesky only after a channel-native thesis exists. Do not dump identical short-form posts everywhere.

## Hardware assessment

### Pilot—buy nothing yet

Use the existing MacBook Pro for the first end-to-end dry run. The workload is mainly API calls, scheduling, JSON/SQLite/Postgres operations, ffmpeg validation/transcoding, and dashboard delivery. Confirm its memory, free storage, macOS version, and wired-network option before launch.

### Recommended 24/7 control plane

**Mac mini M4 Pro, 24 GB unified memory, 1 TB SSD, Gigabit Ethernet** is sufficient for five API-backed guides. Choose **48 GB** if you expect local quantized models, many concurrent code/build jobs, or a larger hot analytics cache. Apple's current M4 Pro provides a 12-core CPU, 16-core GPU, hardware H.264/HEVC/ProRes/AV1 media engines, 273 GB/s memory bandwidth, and optional 10Gb Ethernet.

Add:

- 4 TB external SSD or NAS for active media and local backups.
- UPS with graceful shutdown and automatic restart configuration.
- Encrypted off-machine backup or object storage.
- Wired network. Ten-gigabit Ethernet is unnecessary unless a fast NAS or multi-gig service can use it.
- MacBook Pro as development console and documented failover.

Apple's current M4 Pro starting configuration is $1,599; a 48 GB/1 TB configuration is listed at $2,499, with 10Gb Ethernet adding $100. Buy for reliability and memory headroom, not because each guide needs a separate CPU.

Sources: [Mac mini specifications](https://www.apple.com/mac-mini/specs/), [48 GB/1 TB configuration](https://www.apple.com/shop/buy-mac/mac-mini/m4-pro-chip-12-core-cpu-16-core-gpu-48gb-memory-1tb-storage).

### Network and storage

- Minimum: 100 Mbps symmetric, unlimited data, wired connection.
- Recommended: 300 Mbps or faster symmetric, business-class router, automatic failover if outages would be material.
- Six 65 MB masters per day with three working copies: about 35 GB/month.
- Twenty masters per day with the same assumptions: about 114 GB/month.
- Multiple platform uploads add outbound bandwidth but not equivalent retained storage when variants share the same master.
- Keep 90 days of hot assets, then archive. A 4 TB active volume leaves substantial room for proxies, retries, captions, thumbnails, and logs.

Sustained local generative video is a separate GPU workload. If cloud media costs become greater than a dedicated rendering machine's total cost, assess an NVIDIA GPU workstation separately; do not oversize the Mac mini control plane to solve that problem.

## Launch budget

### Lean pilot

| Item | Monthly commitment |
| --- | ---: |
| Blotato Starter | $29 |
| Firecrawl Free | $0 |
| Base44 Free | $0 |
| Crayo | $0 initially |
| OpenAI API | Usage-capped |
| Stripe | Transaction-based |
| Existing MacBook Pro | $0 new hardware |

Set the initial OpenAI project limit low, test ten to twenty human-reviewed pieces, and measure cost per approved asset. The minimum fixed software commitment is therefore $29/month plus API usage.

### Five-TikTok-account operating tier

Expect Blotato Creator at $97/month unless Blotato confirms a different allowance in writing. Add Base44 or Crayo only when they replace a measured bottleneck or reduce cost per approved asset. Avoid purchasing overlapping media subscriptions before the content format is validated.

## Safe initial volume

Start with one offer, one narrow audience, and one landing page:

- Week 1: draft-only; 10–20 pieces; validate media, UTM, analytics, and Stripe test events.
- Week 2: one account per core channel; one to two approved posts per day; verify asynchronous post status and public URL.
- Weeks 3–4: five to six master concepts per day, adapted to at most four platforms. This is 20–24 native variants per day, not 24 duplicated uploads.
- Scale an account, channel, format, or producer one dimension at a time after three or more independent posts show credible downstream value.

The operating target is qualified activation and attributable recurring revenue. Virality is an uncertain input, not a deliverable and not the primary optimization metric.

## Owner setup required

1. Create organizational emails and a password-manager vault; enable MFA and recovery contacts.
2. Create and verify the social accounts, pages, or channels. Record owner, recovery method, region, niche, and current account status.
3. Create the Blotato account, connect the initial channels, and test the seven-day UI trial. Generate the API key only when ready to start the paid plan.
4. Create an OpenAI API Platform project with a service account/key, monthly limit, and alerts. Do not place keys in prompts or campaign files.
5. Create Firecrawl, analytics, and Stripe test credentials.
6. Configure Stripe products/prices, webhook endpoint, refunds, and `utm_content`/content-ID attribution.
7. Confirm the offer, product URL, initial audience, ARPU, prohibited claims, and approval owner.
8. Pass platform publishing audits or use an already-authorized publisher flow.

## Current implementation state

- Built: five-guide contracts, campaign economics, content queue, review/approval gate, unique content IDs, UTM attribution, metrics ingestion, scoring, reporting, OpenClaw schedule specification, and the interactive Revenue Flight Deck.
- Added now: Blotato payload preview, guarded submission, and asynchronous status reconciliation.
- Still simulated: UI metrics and connector state.
- Blocked on owner input: real product/offer URL, audience, credentials, social accounts, Stripe configuration, and final publishing authorization.
- Not promised: virality, income, or uninterrupted external-platform availability.
