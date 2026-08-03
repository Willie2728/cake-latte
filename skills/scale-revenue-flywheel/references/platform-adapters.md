# Platform adapters

## Blotato (launch publisher)

Blotato is the default publishing adapter for the initial launch. It provides one paid REST/MCP surface for nine platforms, multiple accounts per platform, asynchronous status reconciliation, and optional media templates.

Environment:

```text
BLOTATO_API_KEY=<stored locally; never commit>
BLOTATO_BASE_URL=https://backend.blotato.com/v2
```

Core operations:

```text
GET  /users/me/accounts
GET  /users/me/accounts/{accountId}/subaccounts
POST /posts
GET  /posts/{postSubmissionId}
```

The free trial does not include API access. Generating an API key begins the paid subscription. Store a Blotato `account_id` per platform/account in campaign configuration; Facebook and LinkedIn Pages also require a subaccount/page ID.

Preview an approved payload:

```bash
python scripts/flywheel.py blotato-payload --workspace <campaign-dir> \
  --content-id <id> --account-id <blotato-account-id>
```

Submit only with a matching recorded approval and explicit execution flag:

```bash
python scripts/flywheel.py blotato-send --workspace <campaign-dir> \
  --content-id <id> --account-id <blotato-account-id> \
  --approved-by <reviewer> --execute
```

The create call returns `postSubmissionId`; it is not proof of publication. Reconcile it with `blotato-status` until `published` or `failed`. Do not blindly retry an ambiguous submission.

Official references:

- https://help.blotato.com/api/start
- https://help.blotato.com/api/api-reference/publish-post
- https://help.blotato.com/api/publish-post/get-post

## Postiz (self-hostable fallback)

Postiz can provide one authorized API surface for multiple connected social channels. Its public API currently exposes integrations and create/schedule post operations, with channel-specific settings.

Environment:

```text
POSTIZ_API_KEY=<stored locally; never commit>
POSTIZ_BASE_URL=https://api.postiz.com/public/v1
```

Core operations:

```text
GET  /integrations
POST /posts
```

Use the integration ID returned by Postiz; do not confuse it with a public username. Preview the generated payload before execution.

Required channel settings include:

- TikTok: privacy, duet, stitch, comments, automatic music, brand/commercial toggles, posting method
- YouTube: title, type, audience declaration, tags, thumbnail when applicable
- Instagram: integration type and post type

Official references:

- https://docs.postiz.com/public-api/introduction
- https://docs.postiz.com/public-api/integrations/list
- https://docs.postiz.com/public-api/posts/create

## Firecrawl

Use Firecrawl for public web research and structured extraction. Store source URL, retrieval time, and the distinction between extracted fact and model inference. Do not crawl authenticated/private surfaces without authorization.

Environment:

```text
FIRECRAWL_API_KEY=<stored locally; never commit>
```

## OpenAI

Use the Responses API or Agents SDK for tool-using workflows and traces. Keep model selection configurable; the initialized example uses `gpt-5.6-sol` as the current resolved primary model. Use a cheaper configured model for high-volume classification only after evals show it meets the task threshold.

Environment:

```text
OPENAI_API_KEY=<stored locally; never commit>
```

Do not put keys in prompts, generated content, campaign JSON, logs, or analytics.

## Stripe

Use UTM fields to trace acquisition and a non-sensitive content ID as `client_reference_id` or Checkout Session metadata. Reconcile `checkout.session.completed`, subscription lifecycle, refunds, and disputes through verified webhooks.

Environment:

```text
STRIPE_SECRET_KEY=<stored locally; never commit>
STRIPE_WEBHOOK_SECRET=<stored locally; never commit>
```

Do not trust client-side purchase events as final revenue. Verify webhook signatures and use idempotent event processing.

Official references:

- https://docs.stripe.com/payment-links/url-parameters
- https://docs.stripe.com/metadata
- https://docs.stripe.com/webhooks

## Direct adapters

Prefer direct official APIs when they provide needed analytics, reliability, or policy controls that the aggregator lacks. Every adapter must expose:

```text
health()
capabilities()
authorize()
validate(content, account)
preview(content, account)
publish(approved_content, idempotency_key)
status(publication_id)
metrics(publication_id, window)
revoke()
```

Never add a connector that cannot preview its exact outbound action or reconcile an ambiguous publish result.

## Media adapters

- **OpenAI:** default reasoning and image generation; optional metered video generation. API billing is separate from ChatGPT subscriptions.
- **Base44:** useful for burst generation and app-embedded media. Live-app video generation consumes integration credits per generated second; treat it as a metered adapter, not unlimited rendering.
- **Crayo:** useful as a creator workstation for clipping, captions, voiceovers, and format production. Do not place it in an autonomous path until the account exposes a documented, supported API and its commercial terms allow the workflow.

Every generated asset must retain prompt/model/provider, cost, rights status, synthetic-media flag, and parent content ID.
