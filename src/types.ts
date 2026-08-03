export type View = 'home' | 'library' | 'connectors' | 'flywheel' | 'studio'

export type Skill = {
  id: string
  name: string
  category: string
  description: string
  outcome: string
  provider: string
  accent: string
  accent2: string
  glyph: string
  runtime: string
  tags: string[]
  installs: string
  featured?: boolean
}

export type Connector = {
  id: string
  name: string
  type: string
  detail: string
  protocol: string
  accent: string
  mark: string
  status: 'ready' | 'optional' | 'local'
}
