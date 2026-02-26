import { FileSearch } from 'lucide-react'
import type { DocumentProcessResponse, EntityType, ParseSummary } from '../../../types/api'
import { Card, CardBody, CardHeader } from '../../../components/ui/Card'
import EmptyState from '../../../components/ui/EmptyState'
import OcrSummaryCard from './OcrSummaryCard'
import EntityCard from './EntityCard'

// ── Summary bar ──────────────────────────────────────────────────────────────

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  radicados: { label: 'Radicados', color: 'bg-indigo-100 text-indigo-700 border-indigo-200' },
  nits:      { label: 'NITs',      color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  cedulas:   { label: 'Cédulas',   color: 'bg-amber-100 text-amber-700 border-amber-200' },
  names:     { label: 'Nombres',   color: 'bg-violet-100 text-violet-700 border-violet-200' },
  court_ids: { label: 'Juzgados',  color: 'bg-sky-100 text-sky-700 border-sky-200' },
}

function SummaryBar({ summary }: { summary: ParseSummary }) {
  const entries = Object.entries(summary).filter(([, count]) => count > 0)
  if (entries.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2">
      {entries.map(([key, count]) => {
        const meta = TYPE_LABELS[key] ?? { label: key, color: 'bg-slate-100 text-slate-600 border-slate-200' }
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
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
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
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {SECTION_TITLE[summaryKey]}
              </h3>
              <span className="text-xs text-slate-400">({entities.length})</span>
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
