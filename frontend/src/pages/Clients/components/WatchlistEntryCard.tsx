import type { WatchlistResponse } from '../../../types/api'
import MonoValue from '../../../components/ui/MonoValue'
import StatusBadge from '../../../components/ui/StatusBadge'

interface WatchlistEntryCardProps {
  entry: WatchlistResponse
}

export default function WatchlistEntryCard({ entry }: WatchlistEntryCardProps) {
  return (
    <div className="bg-ink-800/50 border border-ink-700/60 rounded-lg p-4 space-y-3 card-gold-hover">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <StatusBadge
          variant={entry.is_active ? 'success' : 'neutral'}
          label={entry.is_active ? 'Activa' : 'Inactiva'}
        />
        <span className="text-xs text-ink-600 font-mono">{entry.id.slice(0, 8)}…</span>
      </div>

      {/* Case numbers */}
      {entry.case_numbers.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-semibold text-ink-600 uppercase tracking-wider">
            Radicados vigilados
          </p>
          <div className="flex flex-wrap gap-1.5">
            {entry.case_numbers.map((n) => (
              <span
                key={n}
                className="inline-flex items-center px-2 py-0.5 bg-indigo-950/40 border border-indigo-700/40 rounded text-xs text-indigo-300"
              >
                <MonoValue value={n} copyable />
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Courts */}
      {entry.court_ids.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-semibold text-ink-600 uppercase tracking-wider">
            Despachos
          </p>
          <div className="flex flex-wrap gap-1.5">
            {entry.court_ids.map((c) => (
              <span
                key={c}
                className="px-2 py-0.5 bg-sky-950/40 border border-sky-700/40 rounded text-xs text-sky-300"
              >
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Empty state for case numbers */}
      {entry.case_numbers.length === 0 && entry.court_ids.length === 0 && (
        <p className="text-xs text-ink-600 italic">
          Vigilancia general (sin radicados ni despachos específicos)
        </p>
      )}
    </div>
  )
}
