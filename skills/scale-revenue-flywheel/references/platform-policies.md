# Platform and content policy gates

Read current official documentation again before production activation because platform requirements change.

## Universal rules

- Use official APIs or a user-authorized publishing service.
- Obtain the account owner's authorization and requested approval level.
- Do not simulate human engagement, buy/fake engagement, scrape private data, evade rate limits, rotate accounts to escape enforcement, or automate account warmup.
- Verify rights for images, video, music, voices, trademarks, testimonials, and likenesses.
- Disclose commercial relationships and synthetic/altered media when required.
- Do not publish deceptive claims, fabricated demonstrations, or invented customer outcomes.
- Keep a content hash and platform idempotency key to prevent duplicates.
- Stop automatically on authentication failure, rejection spikes, warnings, or unclear publication state.

## TikTok

TikTok's Content Posting API Direct Post flow requires querying creator information, presenting required metadata, and obtaining explicit creator consent. Unaudited clients are restricted to private visibility. Production public posting therefore requires a compliant audited integration or an authorized publisher that satisfies TikTok's requirements.

Default Cake-Latte mode: `review_required`.

Required checks:

- Account/integration is authorized and eligible
- Correct privacy, comment, duet, stitch, branded-content, and commercial-content settings
- Creator sees or has approved required metadata
- Content complies with synthetic-media, music, advertising, and community rules
- No hidden automation or interaction farming

Official reference: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post

## YouTube

Use `videos.insert` with OAuth authorization. Unverified API projects may have uploaded videos restricted to private until compliance audit. Set audience and synthetic-media declarations accurately. Use resumable uploads and idempotent publication records.

Default Cake-Latte mode: `review_required` until the API project and channel workflow are verified.

Official references:

- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/youtube/v3/docs/videos

## Instagram and Facebook

Use Meta's supported publishing APIs or an authorized publisher. Confirm account type, Page/business linkage, media container processing, publishing quota, commercial disclosure, and current permissions before activation.

Default Cake-Latte mode: `review_required`.

## X, LinkedIn, Threads, Pinterest, Reddit, and others

Each connector must define:

- Supported account and post types
- Required OAuth scopes
- Rate and posting limits
- Media rules
- Scheduling support
- Analytics availability
- Review and commercial-content requirements

If the requirement is unknown, generate a draft and stop before publishing.

## Autonomous publishing modes

`draft_only` — generate and package; never schedule or publish.  
`review_required` — require a recorded approval per item.  
`auto_after_template_approval` — publish only content matching an approved template, offer, account, and risk class; retain caps and stop conditions.  
`auto_publish` — use only when the platform flow permits it and the user explicitly authorizes the exact account, content class, and limits.

Publishing mode never overrides platform consent, audit, disclosure, or legal requirements.
