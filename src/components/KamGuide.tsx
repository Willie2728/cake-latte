import { useEffect, useRef, useState } from 'react'
import { Grip, Mic, MicOff, Move, Send, Sparkles, Volume2, X } from 'lucide-react'
import type { View } from '../types'
import { KamPortrait } from './KamPortrait'

type SpeechRecognitionEventLike = { results: { 0: { 0: { transcript: string } } } }
type RecognitionLike = {
  lang: string
  interimResults: boolean
  maxAlternatives: number
  start: () => void
  stop: () => void
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: (() => void) | null
  onend: (() => void) | null
}
type RecognitionConstructor = new () => RecognitionLike

type KamGuideProps = {
  onNavigate: (view: View) => void
  externalPrompt?: string
  onPromptHandled?: () => void
}

const answers: Array<{ words: string[]; answer: string; view?: View }> = [
  { words: ['flywheel', 'tiktok', 'viral', 'mrr', 'revenue', 'agents'], answer: 'I opened the Revenue Flight Deck. It models five specialist Knowledge Guides, channel capacity, launch costs, hardware, approvals, and the path to verified revenue without treating views as income.', view: 'flywheel' },
  { words: ['crawl', 'research', 'website', 'market'], answer: 'I would begin with Field Scout, use Firecrawl to map the source material, then synthesize a cited brief. I opened the capability library for you.', view: 'library' },
  { words: ['api', 'connector', 'openai', 'daily', 'firecrawl'], answer: 'The connector fabric is model-agnostic. OpenAI can lead, while Anthropic, Gemini, or a local Ollama model remain swappable. I opened the connector map.', view: 'connectors' },
  { words: ['build', 'workflow', 'automation', 'create'], answer: 'Let’s compose the outcome as a workflow: trigger, reasoning, capabilities, approval boundary, and delivery. The studio is ready.', view: 'studio' },
  { words: ['skill', 'capability', 'library'], answer: 'Capabilities are organized by the result they produce, not by technical jargon. I opened the living library.', view: 'library' },
]

export function KamGuide({ onNavigate, externalPrompt, onPromptHandled }: KamGuideProps) {
  const [open, setOpen] = useState(false)
  const [listening, setListening] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [input, setInput] = useState('')
  const [transcript, setTranscript] = useState('I’m KAM ERON. Tell me the outcome you want—no hunting through menus required.')
  const [faded, setFaded] = useState(false)
  const [position, setPosition] = useState(() => ({ x: Math.max(18, window.innerWidth - 226), y: Math.max(86, window.innerHeight - 304) }))
  const drag = useRef<{ dx: number; dy: number } | null>(null)
  const recognition = useRef<RecognitionLike | null>(null)
  const shell = useRef<HTMLDivElement | null>(null)

  const speak = (text: string) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.97
    utterance.pitch = 0.91
    utterance.onstart = () => setSpeaking(true)
    utterance.onend = () => setSpeaking(false)
    window.speechSynthesis.speak(utterance)
  }

  const respond = (value: string, aloud = true) => {
    const clean = value.trim()
    if (!clean) return
    setInput('')
    const lower = clean.toLowerCase()
    const match = answers.find((entry) => entry.words.some((word) => lower.includes(word)))
    const answer = match?.answer ?? 'I can translate that into a capability plan. I’ll start in the studio, where we can choose models, connectors, permissions, and a delivery channel.'
    setTranscript(answer)
    setOpen(true)
    if (match?.view) onNavigate(match.view)
    else onNavigate('studio')
    if (aloud) speak(answer)
  }

  useEffect(() => {
    if (externalPrompt) {
      respond(externalPrompt, false)
      onPromptHandled?.()
    }
  }, [externalPrompt]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const Ctor = (window as unknown as { SpeechRecognition?: RecognitionConstructor; webkitSpeechRecognition?: RecognitionConstructor }).SpeechRecognition
      ?? (window as unknown as { webkitSpeechRecognition?: RecognitionConstructor }).webkitSpeechRecognition
    if (!Ctor) return
    const instance = new Ctor()
    instance.lang = 'en-US'
    instance.interimResults = false
    instance.maxAlternatives = 1
    instance.onresult = (event) => {
      const value = event.results[0][0].transcript
      setInput(value)
      setListening(false)
      respond(value)
    }
    instance.onerror = () => {
      setListening(false)
      setTranscript('I could not hear that clearly. You can type the request below, or try the microphone again.')
    }
    instance.onend = () => setListening(false)
    recognition.current = instance
    return () => instance.stop()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const move = (event: PointerEvent) => {
      if (!drag.current) return
      const x = Math.min(window.innerWidth - 178, Math.max(8, event.clientX - drag.current.dx))
      const y = Math.min(window.innerHeight - 220, Math.max(68, event.clientY - drag.current.dy))
      setPosition({ x, y })
      if (shell.current) {
        const rect = shell.current.getBoundingClientRect()
        const underneath = document.elementsFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2)
          .find((element) => !shell.current?.contains(element))
        setFaded(Boolean(underneath?.closest('[data-readable], h1, h2, h3, p, img, button, .skill-card')))
      }
    }
    const up = () => { drag.current = null }
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
    return () => {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
    }
  }, [])

  useEffect(() => {
    const keepKAMVisible = () => {
      const rect = shell.current?.getBoundingClientRect()
      const width = rect?.width ?? 178
      const height = rect?.height ?? 220
      const maxX = Math.max(8, window.innerWidth - width - 8)
      const maxY = Math.max(68, window.innerHeight - height - 8)
      setPosition((current) => ({
        x: Math.min(maxX, Math.max(8, current.x)),
        y: Math.min(maxY, Math.max(68, current.y)),
      }))
    }

    keepKAMVisible()
    window.addEventListener('resize', keepKAMVisible)
    return () => window.removeEventListener('resize', keepKAMVisible)
  }, [open])

  const toggleMic = () => {
    if (!recognition.current) {
      setOpen(true)
      setTranscript('Voice recognition is not available in this browser, but I’m still listening through the text field.')
      return
    }
    if (listening) {
      recognition.current.stop()
      setListening(false)
    } else {
      setOpen(true)
      setListening(true)
      recognition.current.start()
    }
  }

  return (
    <div
      ref={shell}
      className={`kam-shell ${open ? 'is-open' : ''} ${faded && !open ? 'is-faded' : ''}`}
      style={{ left: position.x, top: position.y }}
      aria-label="KAM ERON, conversational guide"
    >
      {open && (
        <div className="kam-dialog" data-readable>
          <header>
            <span><Sparkles size={14} /> KAM ERON</span>
            <button onClick={() => setOpen(false)} aria-label="Minimize KAM ERON"><X size={16} /></button>
          </header>
          <p>{transcript}</p>
          <div className="kam-input">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => { if (event.key === 'Enter') respond(input) }}
              placeholder="Ask for an outcome…"
              aria-label="Ask KAM ERON"
            />
            <button onClick={() => respond(input)} aria-label="Send request"><Send size={15} /></button>
          </div>
          <div className="kam-status"><Volume2 size={13} /> {speaking ? 'speaking' : listening ? 'listening' : 'voice ready'}</div>
        </div>
      )}
      <button
        className="kam-drag"
        aria-label="Move KAM ERON"
        onPointerDown={(event) => {
          drag.current = { dx: event.clientX - position.x, dy: event.clientY - position.y }
        }}
      >
        <Grip size={14} /><Move size={12} />
      </button>
      <button className="kam-avatar" onClick={() => setOpen((value) => !value)} aria-label="Talk with KAM ERON">
        <KamPortrait listening={listening} speaking={speaking} />
        <span className="kam-name">KAM <b>ERON</b></span>
      </button>
      <button className={`kam-mic ${listening ? 'is-live' : ''}`} onClick={toggleMic} aria-label={listening ? 'Stop listening' : 'Speak to KAM ERON'}>
        {listening ? <MicOff size={17} /> : <Mic size={17} />}
      </button>
    </div>
  )
}
