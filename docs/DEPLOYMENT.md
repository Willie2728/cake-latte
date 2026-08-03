# Cake-Latte deployment

## What this deployment publishes

The current `render.yaml` deploys the Cake-Latte React/Vite interface as a Render static site. It includes the product UI, KAM ERON browser voice features, the Revenue Flight Deck, and the downloadable logo gallery.

This static deployment does **not** run the autonomous revenue flywheel continuously. The control plane requires a separate authenticated API/worker deployment with a durable database, job queue, object storage, scheduler, monitoring, and server-side secrets. Never place OpenAI, Blotato, Firecrawl, Stripe, or social-platform secret keys in the Vite frontend.

## Prepared configuration

- Render Blueprint: `render.yaml`
- Build: `pnpm install --frozen-lockfile && pnpm build`
- Publish directory: `dist`
- Runtime pin: Node `22.22.0`
- Render plan: free static site
- Automatic deployment: every commit to the linked branch
- SPA fallback: `/*` rewrites to `/index.html`; existing files remain directly accessible
- Secret and local campaign state exclusions: `.gitignore`

## One-time owner authorization

1. Sign in to GitHub and decide whether the Cake-Latte repository is private or public. Private is recommended until launch content and business configuration are finalized.
2. Create the GitHub repository or authorize Codex/GitHub tooling to create it, then push the local `main` branch.
3. Sign in to Render and connect the GitHub account. Give Render access to the Cake-Latte repository.
4. In Render, create a **Blueprint** from the repository. Render reads `render.yaml`, creates the static site, builds it, and assigns an `onrender.com` address.
5. Optionally connect a custom domain after the first successful deployment and update DNS at the domain registrar.

No API keys are required for the static site. The later private worker deployment will prompt for secrets inside Render or the local Mac control plane; secrets must never be committed to GitHub.

## Future production services

The operational system should be deployed separately from the public interface:

- private API service for authenticated commands and webhooks
- background worker for research, media jobs, publishing, and reconciliation
- PostgreSQL for campaigns, approvals, experiments, and attribution
- queue/key-value service for scheduled and retryable jobs
- object storage for generated media
- monitoring, alerting, spending limits, and a kill switch

The static site can go live first. Activating autonomous publishing should happen only after the worker, account authorizations, platform audits, budget limits, and approval policies are verified.
