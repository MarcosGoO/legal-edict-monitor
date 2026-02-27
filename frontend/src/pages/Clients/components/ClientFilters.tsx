import { Search, Filter } from 'lucide-react'
import { useEffect, useState } from 'react'
import { clsx } from 'clsx'

type ActiveFilter = 'all' | 'active' | 'inactive'

interface ClientFiltersProps {
  search: string
  activeFilter: ActiveFilter
  onSearchChange: (v: string) => void
  onActiveFilterChange: (v: ActiveFilter) => void
}

const filterOptions: { value: ActiveFilter; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'active', label: 'Activos' },
  { value: 'inactive', label: 'Inactivos' },
]

export default function ClientFilters({
  search,
  activeFilter,
  onSearchChange,
  onActiveFilterChange,
}: ClientFiltersProps) {
  const [localSearch, setLocalSearch] = useState(search)

  // Debounce: propagate after 300ms of no typing
  useEffect(() => {
    const t = setTimeout(() => onSearchChange(localSearch), 300)
    return () => clearTimeout(t)
  }, [localSearch, onSearchChange])

  // Sync if parent resets
  useEffect(() => setLocalSearch(search), [search])

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Search */}
      <div className="relative flex-1 min-w-[200px] max-w-xs">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-600 pointer-events-none" />
        <input
          type="text"
          placeholder="Buscar por nombre o documento…"
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="w-full pl-9 pr-3 py-2 text-sm border border-ink-700/60 rounded-lg bg-ink-900 text-parchment/90 placeholder:text-ink-600 focus:outline-none focus:ring-2 focus:ring-gold-500 focus:border-transparent"
        />
      </div>

      {/* Active filter pills */}
      <div className="flex items-center gap-1 bg-ink-800 rounded-lg p-1">
        <Filter className="w-3.5 h-3.5 text-ink-600 ml-1.5" />
        {filterOptions.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => onActiveFilterChange(value)}
            className={clsx(
              'px-3 py-1 rounded-md text-xs font-medium transition-colors',
              activeFilter === value
                ? 'bg-gold-500 text-ink-950 font-semibold'
                : 'text-ink-600 hover:text-parchment',
            )}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
