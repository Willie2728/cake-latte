import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  AudioLines,
  Blocks,
  Bot,
  Box,
  Check,
  ChevronRight,
  CircleDot,
  Code2,
  Command,
  Database,
  ExternalLink,
  Eye,
  Globe2,
  KeyRound,
  Layers3,
  LockKeyhole,
  Menu,
  Mic,
  Network,
  Play,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
  WandSparkles,
  X,
  Zap,
} from 'lucide-react'
import { Brand } from './components/Brand'
import { FlywheelConsole } from './components/FlywheelConsole'
import { KamGuide } from './components/KamGuide'
import { SkillDeck } from './components/SkillDeck'
import { categories, connectors, skills } from './data'
import type { Connector, Skill, View } from './types'

const nav: Array<{ id: View; label: string; icon: typeof Sparkles }> = [
  { id: 'home', label: 'Discover', icon: Sparkles },
  { id: 'library', label: 'Capabilities', icon: Layers3 },
  { id: 'connectors', label: 'Connectors', icon: Network },
  { id: 'flywheel', label: 'Flywheel', icon: CircleDot },
  { id: 'studio', label: 'Studio', icon: WandSparkles },
]

function ConnectorMark({ connector, small = false }: { connector: Connector; small?: boolean }) {
  return (
    <span className={`connector-mark ${small ? 'connector-mark--small' : ''}`} style={{ '--connector': connector.accent } as React.CSSProperties}>
      {connector.mark}
    </span>
  )
}

function App() {
  const [view, setView] = useState<View>('home')
  const [mobileNav, setMobileNav] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [kamPrompt, setKamPrompt] = useState('')
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const [selected, setSelected] = useState<Skill>(skills[0])
  const [installed, setInstalled] = useState<Set<string>>(() => new Set(['guardrail']))
  const [connectorState, setConnectorState] = useState<Set<string>>(() => new Set(['openclaw', 'firecrawl', 'daily']))
  const [toast, setToast] = useState('')
  const [blueprintReady, setBlueprintReady] = useState(false)

  const filteredSkills = useMemo(() => {
    const needle = search.trim().toLowerCase()
    return skills.filter((skill) => {
      const categoryMatch = category === 'All' || skill.category === category
      const searchMatch = !needle || [skill.name, skill.description, skill.outcome, skill.provider, ...skill.tags].join(' ').toLowerCase().includes(needle)
      return categoryMatch && searchMatch
    })
  }, [category, search])

  useEffect(() => {
    if (filteredSkills.length && !filteredSkills.some((skill) => skill.id === selected.id)) {
      setSelected(filteredSkills[0])
    }
  }, [filteredSkills, selected.id])

  const notify = (message: string) => {
    setToast(message)
    window.setTimeout(() => setToast(''), 2500)
  }

  const install = (skill: Skill) => {
    setInstalled((current) => new Set([...current, skill.id]))
    notify(`${skill.name} added to your workspace`)
  }

  const submitPrompt = () => {
    if (!prompt.trim()) return
    setKamPrompt(prompt)
    setPrompt('')
  }

  return (
    <div className="app-shell">
      <div className="ambient ambient--one" />
      <div className="ambient ambient--two" />
      <div className="noise" />

      <header className="topbar">
        <button className="brand-button" onClick={() => setView('home')} aria-label="Cake-Latte home">
          <Brand />
        </button>
        <nav className={`main-nav ${mobileNav ? 'is-open' : ''}`} aria-label="Primary navigation">
          {nav.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                className={view === item.id ? 'is-active' : ''}
                onClick={() => { setView(item.id); setMobileNav(false) }}
              >
                <Icon size={15} /> {item.label}
              </button>
            )
          })}
        </nav>
        <div className="top-actions">
          <span className="local-pill"><ShieldCheck size={14} /> local-first</span>
          <button className="launch-button" onClick={() => setView('studio')}>Open studio <ArrowRight size={15} /></button>
          <button className="menu-button" onClick={() => setMobileNav((value) => !value)} aria-label="Toggle navigation">
            {mobileNav ? <X size={19} /> : <Menu size={19} />}
          </button>
        </div>
      </header>

      <main>
        {view === 'home' && (
          <>
            <section className="hero page-pad">
              <div className="hero-copy" data-readable>
                <div className="eyebrow"><span /> THE CONVERSATIONAL CAPABILITY SYSTEM</div>
                <h1>Don’t browse for a tool.<br /><em>Ask for an outcome.</em></h1>
                <p className="hero-lede">One luminous interface for skills, APIs, agents, and automation—with KAM ERON beside you on every screen.</p>
                <div className="ask-bar">
                  <div className="ask-orb"><AudioLines size={21} /></div>
                  <input
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    onKeyDown={(event) => { if (event.key === 'Enter') submitPrompt() }}
                    placeholder="Tell KAM what you want to accomplish…"
                    aria-label="Tell KAM what you want to accomplish"
                  />
                  <button onClick={submitPrompt}><ArrowRight size={19} /></button>
                </div>
                <div className="prompt-chips">
                  <span>Try:</span>
                  {['Research a market', 'Build a campaign', 'Connect my tools'].map((example) => (
                    <button key={example} onClick={() => { setPrompt(example); setKamPrompt(example) }}>{example}</button>
                  ))}
                </div>
                <div className="proof-row">
                  <div><strong>100%</strong><span>model-agnostic</span></div>
                  <div><strong>BYOK</strong><span>keys stay yours</span></div>
                  <div><strong>VOICE</strong><span>native by design</span></div>
                </div>
              </div>

              <div className="hero-deck" data-readable>
                <div className="deck-label"><span>LIVE CAPABILITY DECK</span><span>Swipe to explore</span></div>
                <SkillDeck
                  items={skills.filter((skill) => skill.featured || ['meeting-memory', 'guardrail'].includes(skill.id))}
                  activeId={selected.id}
                  onSelect={setSelected}
                  onInstall={install}
                  installed={installed}
                  compact
                />
                <button className="explore-all" onClick={() => setView('library')}>Explore all capabilities <ArrowRight size={16} /></button>
              </div>
            </section>

            <section className="signal-strip" aria-label="Supported technology">
              <div className="signal-strip__track">
                {[...connectors, ...connectors].map((connector, index) => (
                  <span key={`${connector.id}-${index}`}><ConnectorMark connector={connector} small /> {connector.name}</span>
                ))}
              </div>
            </section>

            <section className="difference page-pad" data-readable>
              <div className="section-intro">
                <p>THE DIFFERENCE</p>
                <h2>A marketplace that behaves like a <em>conversation.</em></h2>
                <span>The interface recedes. Your intention becomes the navigation.</span>
              </div>
              <div className="difference-grid">
                <article className="feature-panel feature-panel--wide">
                  <div className="feature-number">01</div>
                  <div className="feature-visual intent-visual">
                    <span className="intent-dot"><Mic size={18} /></span>
                    <span className="intent-line" />
                    <span className="intent-result"><Zap size={18} /> outcome</span>
                  </div>
                  <h3>Intent, not interface</h3>
                  <p>Speak naturally. KAM finds the capabilities, explains the plan, and asks before consequential actions.</p>
                </article>
                <article className="feature-panel">
                  <div className="feature-number">02</div>
                  <div className="mini-orbit"><span /><span /><span /><i /></div>
                  <h3>Any model. One fabric.</h3>
                  <p>OpenAI by default. Anthropic, Gemini, and local models by policy or task.</p>
                </article>
                <article className="feature-panel">
                  <div className="feature-number">03</div>
                  <div className="vault-visual"><LockKeyhole size={28} /><span>LOCAL</span></div>
                  <h3>Trust is visible</h3>
                  <p>Keys stay local, permissions are legible, and every capability carries a risk ledger.</p>
                </article>
              </div>
            </section>
          </>
        )}

        {view === 'library' && (
          <section className="library-page page-pad">
            <div className="page-heading" data-readable>
              <div>
                <p className="eyebrow"><span /> LIVING CAPABILITY LIBRARY</p>
                <h1>Choose capabilities,<br /><em>compound outcomes.</em></h1>
              </div>
              <div className="page-stat"><strong>{skills.length}</strong><span>launch capabilities</span></div>
            </div>
            <div className="library-tools">
              <label className="search-box"><Search size={18} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by outcome, provider, or capability…" /></label>
              <div className="category-row">
                {categories.map((item) => <button className={category === item ? 'is-active' : ''} onClick={() => setCategory(item)} key={item}>{item}</button>)}
              </div>
            </div>
            <div className="library-stage">
              <SkillDeck items={filteredSkills} activeId={selected.id} onSelect={setSelected} onInstall={install} installed={installed} />
              <aside className="skill-detail" style={{ '--accent': selected.accent } as React.CSSProperties} data-readable>
                <div className="skill-detail__top"><span>{selected.category}</span><span><CircleDot size={13} /> reviewed</span></div>
                <h2>{selected.name}</h2>
                <p>{selected.description}</p>
                <div className="outcome-box"><Sparkles size={16} /><div><span>DELIVERS</span><strong>{selected.outcome}</strong></div></div>
                <dl>
                  <div><dt>Provider</dt><dd>{selected.provider}</dd></div>
                  <div><dt>Runtime</dt><dd>{selected.runtime}</dd></div>
                  <div><dt>Security</dt><dd>Permission manifest + scan</dd></div>
                </dl>
                <div className="tag-row">{selected.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
                <button className="primary-action" onClick={() => install(selected)}>
                  {installed.has(selected.id) ? <><Check size={17} /> Added to workspace</> : <><Plus size={17} /> Add capability</>}
                </button>
              </aside>
            </div>
          </section>
        )}

        {view === 'connectors' && (
          <section className="connectors-page page-pad">
            <div className="page-heading" data-readable>
              <div>
                <p className="eyebrow"><span /> MODEL-AGNOSTIC FABRIC</p>
                <h1>Your tools, aligned.<br /><em>Your keys, protected.</em></h1>
              </div>
              <button className="diagram-button"><Eye size={16} /> View data flow</button>
            </div>

            <div className="fabric-map" data-readable>
              <div className="fabric-core"><img src="/constellate-mark.svg" alt="" /><span>CAKE-LATTE<br /><b>ROUTER</b></span></div>
              <div className="fabric-ring fabric-ring--one" />
              <div className="fabric-ring fabric-ring--two" />
              {connectors.slice(0, 8).map((connector, index) => (
                <button
                  key={connector.id}
                  className={`fabric-node fabric-node--${index + 1} ${connectorState.has(connector.id) ? 'is-connected' : ''}`}
                  onClick={() => {
                    setConnectorState((current) => {
                      const next = new Set(current)
                      if (next.has(connector.id)) next.delete(connector.id); else next.add(connector.id)
                      return next
                    })
                  }}
                  style={{ '--connector': connector.accent } as React.CSSProperties}
                >
                  <ConnectorMark connector={connector} />
                  <span>{connector.name}<small>{connectorState.has(connector.id) ? 'connected' : 'available'}</small></span>
                </button>
              ))}
              <div className="flow-pulse flow-pulse--one" />
              <div className="flow-pulse flow-pulse--two" />
            </div>

            <div className="connector-ledger">
              <div className="connector-ledger__heading"><span>CONNECTOR LEDGER</span><span>{connectorState.size} active</span></div>
              <div className="connector-rows">
                {connectors.map((connector) => (
                  <article key={connector.id} data-readable>
                    <ConnectorMark connector={connector} />
                    <div><h3>{connector.name}</h3><p>{connector.type} · {connector.detail}</p></div>
                    <span className="protocol"><KeyRound size={13} /> {connector.protocol}</span>
                    <button
                      className={connectorState.has(connector.id) ? 'is-connected' : ''}
                      onClick={() => setConnectorState((current) => {
                        const next = new Set(current)
                        if (next.has(connector.id)) next.delete(connector.id); else next.add(connector.id)
                        return next
                      })}
                    >
                      {connectorState.has(connector.id) ? <><Check size={14} /> Connected</> : <><Plus size={14} /> Connect</>}
                    </button>
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}

        {view === 'studio' && (
          <section className="studio-page page-pad">
            <div className="page-heading" data-readable>
              <div>
                <p className="eyebrow"><span /> COMPOSITION STUDIO</p>
                <h1>Describe the result.<br /><em>Compose the system.</em></h1>
              </div>
              <div className="studio-presence"><span /><b>KAM is in the room</b></div>
            </div>

            <div className="studio-grid">
              <aside className="studio-brief" data-readable>
                <span className="panel-label">OUTCOME BRIEF</span>
                <h2>Build a weekly market intelligence brief</h2>
                <p>Monitor five competitors, flag meaningful changes, synthesize what it means, and deliver every Monday.</p>
                <div className="brief-field"><span>AUDIENCE</span><strong>Executive team</strong><ChevronRight size={15} /></div>
                <div className="brief-field"><span>DELIVERY</span><strong>Email + Notion</strong><ChevronRight size={15} /></div>
                <div className="brief-field"><span>APPROVAL</span><strong>Review before send</strong><ChevronRight size={15} /></div>
                <button className="voice-brief"><Mic size={17} /> Refine with KAM</button>
              </aside>

              <div className="flow-canvas" data-readable>
                <div className="canvas-toolbar"><span>WORKFLOW / MARKET-PULSE</span><div><button><Search size={14} /></button><button><Plus size={14} /></button></div></div>
                <div className="flow-nodes">
                  <div className="flow-node flow-node--trigger"><span><Play size={17} /></span><div><small>TRIGGER</small><strong>Monday · 7:00 AM</strong></div></div>
                  <div className="flow-wire flow-wire--1"><i /></div>
                  <div className="flow-node flow-node--crawl"><span><Globe2 size={17} /></span><div><small>CAPABILITY</small><strong>Field Scout</strong><em>5 sources · Firecrawl</em></div></div>
                  <div className="flow-wire flow-wire--2"><i /></div>
                  <div className="flow-node flow-node--reason"><span><Bot size={17} /></span><div><small>REASONING</small><strong>OpenAI primary</strong><em>Anthropic fallback</em></div></div>
                  <div className="flow-wire flow-wire--3"><i /></div>
                  <div className="flow-node flow-node--gate"><span><ShieldCheck size={17} /></span><div><small>HUMAN GATE</small><strong>Review & approve</strong></div></div>
                  <div className="flow-wire flow-wire--4"><i /></div>
                  <div className="flow-node flow-node--deliver"><span><Zap size={17} /></span><div><small>DELIVER</small><strong>Notion + email</strong></div></div>
                </div>
                <div className="canvas-legend"><span><i className="green" /> local/private</span><span><i className="gold" /> approval gate</span><span><i className="blue" /> external API</span></div>
              </div>

              <aside className="studio-inspector" data-readable>
                <span className="panel-label">SYSTEM CHECK</span>
                <div className="readiness-ring"><span>{blueprintReady ? '100' : '84'}<small>%</small></span></div>
                <ul>
                  <li><Check size={14} /> Skills permission-scanned</li>
                  <li><Check size={14} /> Secrets remain local</li>
                  <li><Check size={14} /> Fallback model defined</li>
                  <li className={blueprintReady ? '' : 'is-pending'}>{blueprintReady ? <Check size={14} /> : <CircleDot size={14} />} Delivery authorization</li>
                </ul>
                <button className="primary-action" onClick={() => { setBlueprintReady(true); notify('Blueprint compiled and ready to review') }}>
                  {blueprintReady ? <><Check size={17} /> Blueprint ready</> : <><Command size={17} /> Compile blueprint</>}
                </button>
                <button className="secondary-action"><Code2 size={16} /> Export as skill package</button>
              </aside>
            </div>
          </section>
        )}
        {view === 'flywheel' && <FlywheelConsole onNotify={notify} />}
      </main>

      <footer className="site-footer page-pad">
        <Brand compact />
        <p>Every capability, in conversation.</p>
        <div><span>© 2026 Verloray AI OS · Wilkerson Collective Inc.</span><button>Security</button><button>Architecture</button><button>Terms</button></div>
      </footer>

      <KamGuide
        onNavigate={(next) => {
          setView(next)
          if (next === 'library') {
            setSearch('')
            setCategory('All')
          }
        }}
        externalPrompt={kamPrompt}
        onPromptHandled={() => setKamPrompt('')}
      />
      {toast && <div className="toast"><Check size={16} /> {toast}</div>}
    </div>
  )
}

export default App
