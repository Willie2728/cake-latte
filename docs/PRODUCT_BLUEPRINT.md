# Cake-Latte product blueprint

## Product thesis

Most AI products make people learn the interface before they can get value. Cake-Latte reverses that relationship. The user expresses an outcome in natural language; KAM ERON discovers the required capabilities, explains the plan, requests approval at consequential boundaries, and orchestrates the work.

Cake-Latte should feel like a living capability environment—not another grid of AI tool cards.

## Public reference audit

The LarryBrain public site currently presents:

- A searchable, category-filtered AI-agent skills marketplace
- Skill detail, free/pro labels, install counts, and an installation flow
- An API reference library organized by category and authentication type
- Agent-driven skill discovery and installation
- Local/BYOK execution and security-review claims
- Creator publishing, referrals, subscription access, documentation, and account flows

Cake-Latte maps those public workflows to an original system:

| Reference workflow | Cake-Latte approach |
| --- | --- |
| Browse skills | Conversational discovery plus a 3D capability deck |
| Search categories | Search by outcome, provider, tag, or category |
| API library | Visual connector fabric and detailed connector ledger |
| Install skill | Add a signed capability to a workspace constellation |
| Agent auto-discovery | KAM plans and recommends a capability chain |
| Local API keys | Desktop/local vault; short-lived session injection |
| Security review | Static scan, permission manifest, runtime sandbox, risk ledger |
| Publish | Creator studio, validation, signature, review, and versioning |
| Subscription gate | Open core; charge only for managed hosting and premium services |

Paid or proprietary third-party skills must not be copied. Equivalent capabilities should be written from scratch, licensed, contributed by their owners, or assembled from open-source components.

## Architecture

```text
Web / desktop UI
  └─ KAM presence layer
      ├─ typed intent
      ├─ browser voice fallback
      └─ Daily WebRTC session
          └─ realtime orchestrator
              ├─ OpenAI primary model adapter
              ├─ Anthropic / Gemini adapters
              ├─ Ollama local adapter
              ├─ capability planner
              └─ approval policy engine

Control plane
  ├─ identity and organizations
  ├─ capability registry and search
  ├─ signed package/version service
  ├─ creator publishing pipeline
  ├─ connector metadata and OAuth
  └─ audit/event ledger

Execution plane
  ├─ local desktop bridge / OpenClaw
  ├─ skill sandbox and permission broker
  ├─ Firecrawl crawl/extract jobs
  ├─ user-selected APIs
  └─ workflow scheduler and webhooks

Data plane
  ├─ Postgres metadata
  ├─ object storage for signed packages
  ├─ vector/search index
  └─ local encrypted secret vault
```

## Connector contracts

Every connector should implement the same minimum contract:

```ts
interface ConnectorAdapter {
  id: string
  capabilities(): Promise<CapabilityManifest>
  health(): Promise<HealthStatus>
  authorize(request: AuthorizationRequest): Promise<AuthorizationResult>
  execute(call: ToolCall, context: ExecutionContext): Promise<ToolResult>
  revoke(): Promise<void>
}
```

The model router should implement an equivalent contract so OpenAI is the preferred provider without becoming a hard dependency.

## KAM ERON

KAM is the persistent interaction and explanation layer, not decorative chrome.

Required behaviors:

- Present on every authenticated product route
- Draggable and minimizable
- Automatically translucent when covering meaningful content
- Voice, text, and optional live video/avatar modes
- Page-aware; understands the current selection and available actions
- Explains what will happen before external writes or consequential actions
- Never displays or repeats secret values
- Has a non-avatar accessibility mode with the same functionality

The prototype ships a stylized holographic stand-in and working browser voice controls. The production photorealistic rendition should be generated as an original character, then driven through a pluggable avatar provider over the Daily realtime media layer. Daily supplies WebRTC transport; a facial animation/avatar engine is still required.

## Security model

1. Treat every third-party skill as untrusted code.
2. Require a declared permission manifest and dependency inventory.
3. Scan source and package artifacts before signing.
4. Execute with least privilege in an isolated workspace.
5. Inject secrets only for the duration of an authorized call.
6. Default external writes, sends, purchases, and destructive actions to explicit approval.
7. Log capability, permission, destination, and outcome—never secret material.
8. Make the risk ledger visible in the UI before installation.

## Build phases

### Phase 1 — Product shell

Complete in this prototype: brand, capability deck, library, connector fabric, studio, KAM presence, responsive behavior, and interaction model.

### Phase 2 — Real registry and local runtime

- Account and organization model
- Postgres capability registry
- OpenClaw discovery/install adapter
- Signed packages, versioning, and rollbacks
- Local vault and desktop bridge
- Scanner and permission ledger

### Phase 3 — Realtime KAM

- Daily room/token service
- OpenAI realtime session adapter
- Speech interruption and turn detection
- Photorealistic avatar rendering provider
- Page/action context channel
- Consent, camera/microphone, and accessibility controls

### Phase 4 — Creator economy

- Creator onboarding and identity verification
- Capability SDK and validator
- Automated plus human review queue
- Usage, attribution, payouts, and dispute tools

### Phase 5 — Managed operations

- Schedules and background workflows
- Team governance and policy templates
- Observability, rate limits, billing, and support tooling
- Enterprise SSO and deployment controls

## Success measures

- Time from spoken intent to an approved plan
- Percentage of tasks completed without manual navigation
- Capability install-to-success rate
- Approval comprehension and reversal rate
- Connector reliability and provider-switch success
- Security findings prevented before execution
- KAM usefulness score, including accessibility mode
