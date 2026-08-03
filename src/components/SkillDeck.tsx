import { useMemo, useRef, useState } from 'react'
import { ArrowLeft, ArrowRight, Check, Plus, Sparkles } from 'lucide-react'
import type { Skill } from '../types'

type SkillDeckProps = {
  items: Skill[]
  activeId?: string
  onSelect?: (skill: Skill) => void
  onInstall?: (skill: Skill) => void
  installed?: Set<string>
  compact?: boolean
}

export function SkillDeck({ items, activeId, onSelect, onInstall, installed = new Set(), compact = false }: SkillDeckProps) {
  const initialIndex = Math.max(0, items.findIndex((item) => item.id === activeId))
  const [active, setActive] = useState(initialIndex)
  const pointerStart = useRef<number | null>(null)
  const safeActive = items.length ? Math.min(active, items.length - 1) : 0

  const visible = useMemo(() => {
    if (!items.length) return []
    return items.map((item, index) => {
      let offset = index - safeActive
      const half = items.length / 2
      if (offset > half) offset -= items.length
      if (offset < -half) offset += items.length
      return { item, index, offset }
    }).filter(({ offset }) => Math.abs(offset) <= (compact ? 2 : 3))
  }, [items, safeActive, compact])

  const move = (amount: number) => {
    if (!items.length) return
    const next = (safeActive + amount + items.length) % items.length
    setActive(next)
    onSelect?.(items[next])
  }

  if (!items.length) {
    return <div className="deck-empty">No capability matches that request. Try a broader phrase.</div>
  }

  return (
    <div
      className={`skill-deck ${compact ? 'skill-deck--compact' : ''}`}
      onPointerDown={(event) => { pointerStart.current = event.clientX }}
      onPointerUp={(event) => {
        if (pointerStart.current === null) return
        const distance = event.clientX - pointerStart.current
        if (Math.abs(distance) > 40) move(distance > 0 ? -1 : 1)
        pointerStart.current = null
      }}
      onKeyDown={(event) => {
        if (event.key === 'ArrowLeft') move(-1)
        if (event.key === 'ArrowRight') move(1)
      }}
      role="region"
      aria-label="Swipeable capability deck"
      tabIndex={0}
    >
      <div className="deck-stage">
        {visible.map(({ item, index, offset }) => {
          const isActive = offset === 0
          const transform = `translate3d(calc(${offset} * clamp(78px, 10vw, 146px)), ${Math.abs(offset) * 18}px, ${-Math.abs(offset) * 90}px) rotateY(${offset * -17}deg) rotateZ(${offset * 1.5}deg) scale(${1 - Math.abs(offset) * .09})`
          return (
            <article
              key={item.id}
              className={`skill-card ${isActive ? 'is-active' : ''}`}
              style={{
                '--accent': item.accent,
                '--accent-2': item.accent2,
                '--card-transform': transform,
                '--card-opacity': Math.abs(offset) > 2 ? '.24' : isActive ? '1' : '.62',
                zIndex: 20 - Math.abs(offset),
              } as React.CSSProperties}
              onClick={() => {
                setActive(index)
                onSelect?.(item)
              }}
              data-readable
            >
              <div className="skill-card__grain" />
              <header className="skill-card__head">
                <span className="skill-card__glyph">{item.glyph}</span>
                <span className="skill-card__runtime">{item.runtime}</span>
              </header>
              <div className="skill-card__orbit" aria-hidden="true">
                <span />
                <span />
                <span />
              </div>
              <div className="skill-card__content">
                <p>{item.category}</p>
                <h3>{item.name}</h3>
                <span>{item.outcome}</span>
              </div>
              <footer className="skill-card__foot">
                <span>{item.installs} uses</span>
                {isActive && onInstall && (
                  <button
                    className="card-install"
                    onClick={(event) => {
                      event.stopPropagation()
                      onInstall(item)
                    }}
                    aria-label={`${installed.has(item.id) ? 'Installed' : 'Add'} ${item.name}`}
                  >
                    {installed.has(item.id) ? <Check size={15} /> : <Plus size={15} />}
                  </button>
                )}
              </footer>
            </article>
          )
        })}
      </div>
      <div className="deck-controls">
        <button onClick={() => move(-1)} aria-label="Previous capability"><ArrowLeft size={18} /></button>
        <div className="deck-progress" aria-label={`${safeActive + 1} of ${items.length}`}>
          <span style={{ width: `${((safeActive + 1) / items.length) * 100}%` }} />
        </div>
        <span className="deck-count">{String(safeActive + 1).padStart(2, '0')} / {String(items.length).padStart(2, '0')}</span>
        <button onClick={() => move(1)} aria-label="Next capability"><ArrowRight size={18} /></button>
      </div>
      <div className="deck-hint"><Sparkles size={14} /> drag, swipe, or use arrow keys</div>
    </div>
  )
}
