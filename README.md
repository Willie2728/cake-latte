# Cake-Latte

Cake-Latte by Verloray AI OS is an original conversational capability system for Wilkerson Collective Inc. It combines a skills marketplace, API connector library, workflow composer, and an ever-present voice guide named KAM ERON.

The prototype deliberately does not copy LarryBrain source code, branding, paid skill packages, or proprietary catalog content. It demonstrates an original product that can provide comparable public-facing workflows through open skills, first-party capabilities, and user-owned connectors.

## What works in this prototype

- Responsive, cinematic single-page product interface
- Swipeable, keyboard-accessible 3D capability cover flow
- Capability search and outcome/category filtering
- Add/install state with confirmation feedback
- Model-agnostic connector map and interactive connector ledger
- Workflow composition studio with a runnable blueprint state
- Persistent, draggable KAM ERON guide on every product view
- KAM becomes translucent when dragged over readable page content
- Browser speech recognition and speech synthesis when supported
- Typed conversational routing when voice recognition is unavailable
- Reduced-motion support and semantic navigation
- Installable `scale-revenue-flywheel` skill with multi-agent content operations, Postiz payloads, Stripe attribution, experiment scoring, and $5K MRR planning
- Interactive Revenue Flight Deck with five Knowledge Guide contracts, a live capacity model, launch-cost ledger, hardware profile, and activation checklist
- Blotato payload preview, guarded publishing, and asynchronous publication reconciliation; Postiz remains an optional fallback

## Run locally

```powershell
pnpm install
pnpm dev
```

Production build:

```powershell
pnpm build
```

## Brand

**Name:** Cake-Latte  
**Product brand:** Verloray AI OS  
**Company:** Wilkerson Collective Inc.  
**Positioning:** A conversational capability system  
**Tagline:** Every capability, in conversation.  
**Guide:** KAM ERON

The logo is an original orbital mark: a central human intention with capabilities aligning around it. The master vector is at `public/constellate-mark.svg`.

Five Cake-Latte logo directions with the tagline “Intelligence, beautifully orchestrated.” are available at `public/logo-concepts.html`.

The public interface is ready for a Render static-site deployment using the included `render.yaml`. See `docs/DEPLOYMENT.md` for the owner authorization steps and the separate backend requirements for continuous agent operation.

## Production path

The UI is intentionally front-end complete but uses simulated connector and installation state. Production requires an authenticated API, signed skill registry, permission scanner, local key vault/desktop bridge, OpenClaw adapter, Firecrawl jobs, Daily rooms, realtime model sessions, creator publishing, audit logging, and deployment infrastructure.

See [`docs/PRODUCT_BLUEPRINT.md`](docs/PRODUCT_BLUEPRINT.md) for the architecture and parity plan.

The Revenue Flywheel skill is under [`skills/scale-revenue-flywheel`](skills/scale-revenue-flywheel/SKILL.md). Its deterministic control plane is tested with `python skills/scale-revenue-flywheel/scripts/test_flywheel.py -v`.

The current pricing, platform, hardware, bandwidth, storage, and launch assessment is at [`docs/REVENUE_FLYWHEEL_ASSESSMENT.md`](docs/REVENUE_FLYWHEEL_ASSESSMENT.md).
