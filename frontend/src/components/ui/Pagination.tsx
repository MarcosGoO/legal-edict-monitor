import { ChevronLeft, ChevronRight } from 'lucide-react'
import { clsx } from 'clsx'

interface PaginationProps {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
  onPageSizeChange?: (size: number) => void
}

export default function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
  onPageSizeChange,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1
  const to = Math.min(page * pageSize, total)

  const btnBase =
    'flex items-center justify-center w-8 h-8 rounded-md text-sm font-medium transition-colors'

  return (
    <div className="flex items-center justify-between gap-4 mt-4 pt-4 border-t border-ink-700/40">
      <p className="text-xs text-ink-600 flex-shrink-0">
        {total === 0 ? 'Sin resultados' : `${from}–${to} de ${total}`}
      </p>

      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className={clsx(btnBase, 'text-ink-600 hover:bg-ink-800 disabled:opacity-40 disabled:cursor-not-allowed')}
          aria-label="Página anterior"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        {Array.from({ length: totalPages }, (_, i) => i + 1)
          .filter((p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
          .reduce<(number | '...')[]>((acc, p, i, arr) => {
            if (i > 0 && p - (arr[i - 1] as number) > 1) acc.push('...')
            acc.push(p)
            return acc
          }, [])
          .map((p, i) =>
            p === '...' ? (
              <span key={`ellipsis-${i}`} className="w-8 text-center text-xs text-ink-600">
                …
              </span>
            ) : (
              <button
                key={p}
                onClick={() => onPageChange(p as number)}
                className={clsx(
                  btnBase,
                  p === page
                    ? 'bg-gold-500 text-ink-950 font-semibold'
                    : 'text-ink-600 hover:bg-ink-800',
                )}
              >
                {p}
              </button>
            ),
          )}

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className={clsx(btnBase, 'text-ink-600 hover:bg-ink-800 disabled:opacity-40 disabled:cursor-not-allowed')}
          aria-label="Página siguiente"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {onPageSizeChange && (
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="text-xs text-ink-600 border border-ink-700/60 rounded-md px-2 py-1 bg-ink-900 focus:outline-none focus:ring-1 focus:ring-gold-500"
        >
          {[10, 20, 50].map((s) => (
            <option key={s} value={s}>
              {s} / pág.
            </option>
          ))}
        </select>
      )}
    </div>
  )
}
