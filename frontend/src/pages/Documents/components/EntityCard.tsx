import { Copy, Check } from 'lucide-react'
import { useState } from 'react'
import type { EntityResponse, EntityType } from '../../../types/api'

// ── Entity type metadata ─────────────────────────────────────────────────────

const ENTITY_META: Record<EntityType, { label: string; badge: string; section: string }> = {
  radicado: { label: 'Radicado',  badge: 'bg-indigo-950/60 text-indigo-300 border border-indigo-700/40',  section: 'radicados' },
  nit:      { label: 'NIT',       badge: 'bg-emerald-950/60 text-emerald-300 border border-emerald-700/40', section: 'nits'     },
  cedula:   { label: 'Cédula',    badge: 'bg-amber-950/60 text-amber-300 border border-amber-700/40',      section: 'cédulas'  },
  nombre:   { label: 'Nombre',    badge: 'bg-violet-950/60 text-violet-300 border border-violet-700/40',   section: 'nombres'  },
  court_id: { label: 'Juzgado',   badge: 'bg-sky-950/60 text-sky-300 border border-sky-700/40',            section: 'juzgados' },
}

// ── Confidence dot ───────────────────────────────────────────────────────────

function ConfidenceDot({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const [color, label] =
    pct >= 90 ? ['bg-emerald-400', 'Alta confianza']
    : pct >= 70 ? ['bg-amber-400', 'Confianza media']
    : ['bg-red-400', 'Baja confianza']

  return (
    <span className="flex items-center gap-1.5 text-xs text-ink-600">
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${color}`} />
      {label} · {pct}%
    </span>
  )
}

// ── Context snippet with highlight ──────────────────────────────────────────

function ContextSnippet({ context, normalized }: { context: string; normalized: string }) {
  if (!context) return null

  const idx = context.toLowerCase().indexOf(normalized.toLowerCase())
  if (idx === -1) {
    return (
      <p className="text-xs text-ink-600 italic font-display bg-ink-800/60 rounded px-2.5 py-2 border border-ink-700/40 leading-relaxed">
        "{context}"
      </p>
    )
  }

  const before = context.slice(0, idx)
  const match  = context.slice(idx, idx + normalized.length)
  const after  = context.slice(idx + normalized.length)

  return (
    <p className="text-xs text-ink-600 italic font-display bg-ink-800/60 rounded px-2.5 py-2 border border-ink-700/40 leading-relaxed">
      "{before}
      <mark className="bg-gold-900 text-gold-300 border border-gold-700/40 not-italic font-medium rounded-sm px-0.5">
        {match}
      </mark>
      {after}"
    </p>
  )
}

// ── Copy button ──────────────────────────────────────────────────────────────

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {}
  }

  return (
    <button
      onClick={copy}
      className="flex items-center gap-1 px-2 py-1 text-xs text-ink-600 bg-ink-800 rounded-md hover:bg-ink-700 transition-colors"
      title="Copiar valor"
    >
      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
      {copied ? 'Copiado' : 'Copiar'}
    </button>
  )
}

// ── Main component ───────────────────────────────────────────────────────────

export default function EntityCard({ entity }: { entity: EntityResponse }) {
  const meta = ENTITY_META[entity.type] ?? { label: entity.type, badge: 'bg-ink-800 text-ink-600 border border-ink-700/40', section: '' }
  const isDifferent = entity.raw !== entity.normalized

  return (
    <div className="bg-ink-900 border border-ink-700/60 rounded-xl p-4 space-y-3 card-gold-hover">
      {/* Type badge + confidence */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <span className={`px-2 py-0.5 rounded-md text-xs font-semibold ${meta.badge}`}>
          {meta.label}
        </span>
        <ConfidenceDot value={entity.confidence} />
      </div>

      {/* Normalized value — large monospace */}
      <div className="flex items-center justify-between gap-3">
        <p className="font-mono text-lg font-semibold text-parchment tracking-tight break-all">
          {entity.normalized}
        </p>
        <CopyButton value={entity.normalized} />
      </div>

      {/* Raw value (if different) */}
      {isDifferent && (
        <p className="text-xs text-ink-600">
          <span className="font-medium">Original:</span>{' '}
          <span className="font-mono">{entity.raw}</span>
        </p>
      )}

      {/* Context snippet */}
      {entity.context && (
        <ContextSnippet context={entity.context} normalized={entity.normalized} />
      )}
    </div>
  )
}
