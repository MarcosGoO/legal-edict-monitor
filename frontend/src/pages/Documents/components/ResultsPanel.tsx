import { FileSearch } from 'lucide-react'
import type { DocumentProcessResponse, EntityType, ParseSummary } from '../../../types/api'
import { Card, CardBody, CardHeader } from '../../../components/ui/Card'
import EmptyState from '../../../components/ui/EmptyState'
import OcrSummaryCard from './OcrSummaryCard'
import EntityCard from './EntityCard'

// ── Summary bar ──────────────────────────────────────────────────────────────

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  radicados: { label: 'Radicados', color: 'bg-indigo-950/40 text-indigo-400 border-indigo-800/40' },
  nits:      { label: 'NITs',      color: 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40' },
  cedulas:   { label: 'Cédulas',   color: 'bg-amber-950/40 text-amber-400 border-amber-800/40' },
  names:     { label: 'Nombres',   color: 'bg-violet-950/40 text-violet-400 border-violet-800/40' },
  court_ids: { label: 'Juzgados',  color: 'bg-sky-950/40 text-sky-400 border-sky-800/40' },
}

function SummaryBar({ summary }: { summary: ParseSummary }) {
  const entries = Object.entries(summary).filter(([, count]) => count > 0)
  if (entries.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2">
      {entries.map(([key, count]) => {
        const meta = TYPE_LABELS[key] ?? { label: key, color: 'bg-ink-800 text-ink-600 border-ink-700/40' }
        return (
          <a
            key={key}
            href={`#section-${key}`}
            className={`px-3 py-1 rounded-full text-xs font-semibold border ${meta.color} hover:opacity-80 transition-opacity`}
          >
            {count} {meta.label}
          </a>
        )
      })}
    </div>
  )
}

// ── Entity type to EntityType map ────────────────────────────────────────────

const SUMMARY_KEY_TO_TYPE: Record<string, EntityType> = {
  radicados: 'radicado',
  nits:      'nit',
  cedulas:   'cedula',
  names:     'nombre',
  court_ids: 'court_id',
}

const SECTION_TITLE: Record<string, string> = {
  radicados: 'Radicados',
  nits:      'NITs',
  cedulas:   'Cédulas',
  names:     'Nombres',
  court_ids: 'Juzgados',
}

// ── Main panel ───────────────────────────────────────────────────────────────

export default function ResultsPanel({ result }: { result: DocumentProcessResponse }) {
  if (!result.success || !result.parse) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center gap-2 p-3 bg-red-950/30 border border-red-700/40 rounded-lg text-sm text-red-400">
            <span className="font-semibold">Error:</span>
            <span>{result.error ?? 'No se pudo procesar el documento.'}</span>
          </div>
        </CardBody>
      </Card>
    )
  }

  const { parse, ocr } = result
  const totalCount = parse.entity_count

  return (
    <div className="space-y-4">
      {/* Header card */}
      <Card>
        <CardHeader
          title={`${totalCount} entidad${totalCount !== 1 ? 'es' : ''} encontrada${totalCount !== 1 ? 's' : ''}`}
          description={`Tiempo de procesamiento: ${parse.processing_time_ms.toFixed(0)} ms`}
        />
        <CardBody className="space-y-3">
          {ocr && <OcrSummaryCard ocr={ocr} />}
          <SummaryBar summary={parse.summary} />
        </CardBody>
      </Card>

      {/* Empty state */}
      {totalCount === 0 && (
        <Card>
          <CardBody>
            <EmptyState
              icon={FileSearch}
              title="No se encontraron entidades"
              description="El documento no contiene radicados, NITs, cédulas, nombres ni juzgados reconocibles."
            />
          </CardBody>
        </Card>
      )}

      {/* Entity sections grouped by type */}
      {Object.entries(SUMMARY_KEY_TO_TYPE).map(([summaryKey, entityType]) => {
        const entities = parse.entities.filter((e) => e.type === entityType)
        if (entities.length === 0) return null

        return (
          <div key={summaryKey} id={`section-${summaryKey}`} className="space-y-2 scroll-mt-6">
            <div className="flex items-center gap-2 px-1">
              <h3 className="text-xs font-semibold text-ink-600 uppercase tracking-wider">
                {SECTION_TITLE[summaryKey]}
              </h3>
              <span className="text-xs text-ink-600">({entities.length})</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {entities.map((entity, i) => (
                <EntityCard key={`${entity.type}-${i}`} entity={entity} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
