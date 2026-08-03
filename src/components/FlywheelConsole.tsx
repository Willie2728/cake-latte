import { useMemo, useState, type CSSProperties } from 'react'
import {
  Activity,
  ArrowUpRight,
  BrainCircuit,
  Check,
  CircleDollarSign,
  CloudCog,
  Gauge,
  HardDrive,
  Pause,
  Play,
  Radio,
  Rocket,
  ScanSearch,
  Send,
  ShieldCheck,
  Sparkles,
  WandSparkles,
  Wifi,
} from 'lucide-react'

type FlywheelConsoleProps = {
  onNotify: (message: string) => void
}

const guides = [
  { id: 'signal', name: 'Signal Guide', role: 'Research', tool: 'Firecrawl', cadence: 'Every 6 hours', color: '#72e7ff', icon: ScanSearch },
  { id: 'strategy', name: 'Story Guide', role: 'Strategy', tool: 'OpenAI router', cadence: 'Continuous queue', color: '#e9ff77', icon: BrainCircuit },
  { id: 'media', name: 'Media Guide', role: 'Production', tool: 'GPT Image 2 + media adapters', cadence: 'Capacity gated', color: '#ff8f6b', icon: WandSparkles },
  { id: 'distribution', name: 'Distribution Guide', role: 'Publishing', tool: 'Blotato API', cadence: 'Approved windows', color: '#ff68b5', icon: Send },
  { id: 'growth', name: 'Revenue Guide', role: 'Measurement', tool: 'Stripe + analytics', cadence: 'Every 4 hours', color: '#8b82ff', icon: CircleDollarSign },
]

const vendors = [
  { name: 'Blotato', price: '$29/mo', allowance: '20 accounts · 1,250 AI credits', note: 'Paid plan required for API', state: 'launch', url: 'https://www.blotato.com/pricing' },
  { name: 'Firecrawl', price: '$0 start', allowance: '1,000 pages/mo · 2 concurrent', note: 'Upgrade only after measured use', state: 'free', url: 'https://www.firecrawl.dev/pricing' },
  { name: 'OpenAI', price: 'usage', allowance: 'Reasoning · image · video adapters', note: 'API billing is separate from ChatGPT', state: 'metered', url: 'https://developers.openai.com/api/docs/models' },
  { name: 'Base44', price: '$0 test', allowance: '100 integration credits/mo', note: 'Live video: 5 credits per generated second', state: 'burst', url: 'https://docs.base44.com/Integrations/built-in-integrations' },
  { name: 'Crayo', price: '$13/mo*', allowance: '50 workflows · 40 export minutes', note: 'Annual price; public API not verified', state: 'manual', url: 'https://crayo.ai/pricing' },
]

const launchSteps = [
  { label: 'Control plane and five-guide contracts', status: 'built' },
  { label: 'OpenAI project, budget cap, and service key', status: 'owner' },
  { label: 'Blotato paid API and authorized social accounts', status: 'owner' },
  { label: 'Stripe products, webhooks, and content attribution', status: 'owner' },
  { label: 'TikTok and YouTube production publishing approval', status: 'audit' },
]

export function FlywheelConsole({ onNotify }: FlywheelConsoleProps) {
  const [selectedGuide, setSelectedGuide] = useState(guides[0])
  const [mastersPerDay, setMastersPerDay] = useState(6)
  const [simulationRunning, setSimulationRunning] = useState(true)
  const [reviewedSteps, setReviewedSteps] = useState<Set<number>>(() => new Set([0]))

  const projections = useMemo(() => {
    const platformVariants = mastersPerDay * 4
    const monthlyVariants = platformVariants * 30
    const monthlyStorageGb = Math.round((mastersPerDay * 30 * 65 * 3) / 1024)
    return { platformVariants, monthlyVariants, monthlyStorageGb }
  }, [mastersPerDay])

  return (
    <section className="flywheel-page page-pad">
      <div className="flywheel-heading" data-readable>
        <div>
          <p className="eyebrow"><span /> REVENUE FLIGHT DECK</p>
          <h1>Five guides. One<br /><em>compounding system.</em></h1>
          <p>Plan, govern, and measure an original multi-channel content engine. Every number below is a planning value until a live connector verifies it.</p>
        </div>
        <div className="planning-beacon"><i /><span>PLANNING MODE</span><small>no external posts</small></div>
      </div>

      <div className="metric-ribbon" data-readable>
        <article><span>TARGET MRR</span><strong>$5,000</strong><small>commercial objective</small></article>
        <article><span>VERIFIED MRR</span><strong>$0</strong><small>Stripe not connected</small></article>
        <article><span>MASTER IDEAS / DAY</span><strong>{mastersPerDay}</strong><small>{projections.platformVariants} native variants/day</small></article>
        <article><span>MONTHLY OUTPUT</span><strong>{projections.monthlyVariants}</strong><small>modeled, not scheduled</small></article>
      </div>

      <div className="flight-grid">
        <article className="guide-constellation" data-readable>
          <header>
            <div><span>KNOWLEDGE GUIDE CONSTELLATION</span><small>select a guide to inspect its contract</small></div>
            <button onClick={() => setSimulationRunning((current) => !current)}>
              {simulationRunning ? <Pause size={14} /> : <Play size={14} />}
              {simulationRunning ? 'Pause motion' : 'Resume motion'}
            </button>
          </header>

          <div className={`guide-orbit ${simulationRunning ? 'is-running' : ''}`}>
            <div className="orbit-track orbit-track--outer" />
            <div className="orbit-track orbit-track--inner" />
            <div className="orbit-core">
              <img src="/constellate-mark.svg" alt="" />
              <span>ORCHESTRATOR</span>
              <small>one writer per ledger</small>
            </div>
            {guides.map((guide, index) => {
              const Icon = guide.icon
              return (
                <button
                  key={guide.id}
                  className={`orbit-guide orbit-guide--${index + 1} ${selectedGuide.id === guide.id ? 'is-selected' : ''}`}
                  style={{ '--agent-color': guide.color } as CSSProperties}
                  onClick={() => setSelectedGuide(guide)}
                >
                  <span><Icon size={17} /></span>
                  <b>{guide.name}</b>
                  <small>{guide.role}</small>
                </button>
              )
            })}
          </div>

          <div className="guide-contract" style={{ '--agent-color': selectedGuide.color } as CSSProperties}>
            <div><span>ACTIVE CONTRACT</span><strong>{selectedGuide.name}</strong></div>
            <dl>
              <div><dt>Owns</dt><dd>{selectedGuide.role}</dd></div>
              <div><dt>Primary tool</dt><dd>{selectedGuide.tool}</dd></div>
              <div><dt>Cadence</dt><dd>{selectedGuide.cadence}</dd></div>
            </dl>
            <p><ShieldCheck size={15} /> Can prepare and analyze autonomously. Publishing, spend, claims, and account changes remain policy-gated.</p>
          </div>
        </article>

        <aside className="capacity-console" data-readable>
          <header><span>CAPACITY MODEL</span><Gauge size={16} /></header>
          <label>
            <span>Master concepts per day <b>{mastersPerDay}</b></span>
            <input type="range" min="2" max="20" value={mastersPerDay} onChange={(event) => setMastersPerDay(Number(event.target.value))} />
          </label>
          <div className="capacity-steps">
            <div><i style={{ width: `${Math.min(100, mastersPerDay * 5)}%` }} /><span>RESEARCH</span><b>{mastersPerDay * 3} source checks</b></div>
            <div><i style={{ width: `${Math.min(100, mastersPerDay * 4)}%` }} /><span>PRODUCTION</span><b>{mastersPerDay} masters</b></div>
            <div><i style={{ width: `${Math.min(100, mastersPerDay * 6)}%` }} /><span>DISTRIBUTION</span><b>{projections.platformVariants} variants</b></div>
          </div>
          <div className="capacity-facts">
            <div><HardDrive size={17} /><span><strong>~{projections.monthlyStorageGb} GB/mo</strong><small>working media estimate</small></span></div>
            <div><Wifi size={17} /><span><strong>100 Mbps minimum</strong><small>300+ symmetric preferred</small></span></div>
            <div><CloudCog size={17} /><span><strong>API-first compute</strong><small>local GPU not required</small></span></div>
          </div>
          <button className="simulation-button" onClick={() => onNotify('Capacity model recalculated locally; no platform or API was called')}>
            <Activity size={15} /> Run readiness simulation
          </button>
        </aside>
      </div>

      <div className="loop-rail" data-readable>
        {['Sense', 'Compose', 'Verify', 'Publish', 'Measure', 'Reinvest'].map((step, index) => (
          <div key={step}><span>{String(index + 1).padStart(2, '0')}</span><b>{step}</b>{index < 5 && <i />}</div>
        ))}
      </div>

      <div className="operations-grid">
        <article className="vendor-ledger" data-readable>
          <header><div><span>LAUNCH COST LEDGER</span><small>verified 03 Aug 2026</small></div><strong>$29 + usage</strong></header>
          {vendors.map((vendor) => (
            <a href={vendor.url} target="_blank" rel="noreferrer" key={vendor.name}>
              <div className={`vendor-state vendor-state--${vendor.state}`}><i />{vendor.state}</div>
              <div><b>{vendor.name}</b><small>{vendor.allowance}</small></div>
              <span>{vendor.price}</span>
              <p>{vendor.note}</p>
              <ArrowUpRight size={14} />
            </a>
          ))}
        </article>

        <article className="hardware-brief" data-readable>
          <header><span>DEDICATED CONTROL PLANE</span><Radio size={16} /></header>
          <div className="hardware-machine">
            <div className="machine-glow" />
            <span>MAC MINI</span>
            <strong>M4 PRO</strong>
            <small>24–48 GB · 1 TB · wired Ethernet</small>
          </div>
          <ul>
            <li><Check size={13} /> Five concurrent API-backed guides</li>
            <li><Check size={13} /> Hardware video encode/decode</li>
            <li><Check size={13} /> SQLite/Postgres, queues, logs, scheduler</li>
            <li><Check size={13} /> Existing MacBook becomes dev + failover</li>
          </ul>
          <p>Choose 48 GB only for heavier local models or many parallel build jobs. Cloud video generation does not justify a larger Mac by itself.</p>
        </article>

        <article className="launch-sequence" data-readable>
          <header><div><span>LAUNCH SEQUENCE</span><small>{reviewedSteps.size} of {launchSteps.length} reviewed</small></div><Rocket size={16} /></header>
          <div className="launch-list">
            {launchSteps.map((step, index) => (
              <button
                key={step.label}
                className={reviewedSteps.has(index) ? 'is-reviewed' : ''}
                onClick={() => setReviewedSteps((current) => new Set([...current, index]))}
              >
                <span>{reviewedSteps.has(index) ? <Check size={13} /> : index + 1}</span>
                <b>{step.label}</b>
                <small>{step.status === 'built' ? 'implemented' : step.status === 'owner' ? 'owner setup' : 'vendor audit'}</small>
              </button>
            ))}
          </div>
          <button className="arm-button" onClick={() => onNotify('Launch remains safely locked until accounts, keys, and publishing audits are verified')}>
            <Sparkles size={15} /> Review activation boundary
          </button>
        </article>
      </div>
    </section>
  )
}
