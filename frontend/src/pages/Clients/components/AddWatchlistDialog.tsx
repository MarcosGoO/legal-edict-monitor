import { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { X, Plus } from 'lucide-react'
import type { WatchlistCreate } from '../../../types/api'

// Simple tag input for radicados / courts
function TagInput({
  value,
  onChange,
  placeholder,
  validate,
}: {
  value: string[]
  onChange: (v: string[]) => void
  placeholder: string
  validate?: (v: string) => string | null
}) {
  const [input, setInput] = useState('')
  const [error, setError] = useState<string | null>(null)

  const add = () => {
    const trimmed = input.trim()
    if (!trimmed) return
    if (validate) {
      const err = validate(trimmed)
      if (err) { setError(err); return }
    }
    if (!value.includes(trimmed)) onChange([...value, trimmed])
    setInput('')
    setError(null)
  }

  return (
    <div className="space-y-1.5">
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => { setInput(e.target.value); setError(null) }}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder={placeholder}
          className="flex-1 px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 font-mono"
        />
        <button
          type="button"
          onClick={add}
          className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-sm hover:bg-slate-200 transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
      <div className="flex flex-wrap gap-1.5">
        {value.map((v) => (
          <span key={v} className="inline-flex items-center gap-1 px-2 py-0.5 bg-indigo-50 text-indigo-800 text-xs rounded border border-indigo-200 font-mono">
            {v}
            <button type="button" onClick={() => onChange(value.filter((x) => x !== v))}>
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}

// Loose radicado format check: YYYY-NNNNN-NN-NN-NNN (hyphens or raw digits)
function validateRadicado(v: string): string | null {
  const clean = v.replace(/-/g, '')
  if (!/^\d{23}$/.test(clean)) return 'Formato inválido — debe tener 23 dígitos'
  return null
}

interface AddWatchlistDialogProps {
  clientId: string
  open: boolean
  onClose: () => void
  onSubmit: (data: WatchlistCreate) => Promise<void>
  isLoading: boolean
}

export default function AddWatchlistDialog({
  clientId,
  open,
  onClose,
  onSubmit,
  isLoading,
}: AddWatchlistDialogProps) {
  const [caseNumbers, setCaseNumbers] = useState<string[]>([])
  const [courtIds, setCourtIds] = useState<string[]>([])
  const [channels, setChannels] = useState<('whatsapp' | 'email')[]>(['email'])
  const [immediate, setImmediate] = useState(true)

  const toggleChannel = (ch: 'whatsapp' | 'email') =>
    setChannels((prev) =>
      prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch],
    )

  const handleSubmit = async () => {
    await onSubmit({
      client_id: clientId,
      case_numbers: caseNumbers,
      court_ids: courtIds,
      notification_preferences: { channels, immediate },
    })
    setCaseNumbers([])
    setCourtIds([])
    setChannels(['email'])
    setImmediate(true)
    onClose()
  }

  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/40" />
        <Dialog.Content className="fixed z-50 left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-xl shadow-xl p-6 focus:outline-none max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-5">
            <Dialog.Title className="text-sm font-semibold text-slate-800">
              Nueva configuración de vigilancia
            </Dialog.Title>
            <button onClick={onClose} className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Radicados a vigilar
              </label>
              <p className="text-xs text-slate-400">23 dígitos — p.ej. 11001310300120230012300</p>
              <TagInput
                value={caseNumbers}
                onChange={setCaseNumbers}
                placeholder="Radicado de 23 dígitos…"
                validate={validateRadicado}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Despachos judiciales
              </label>
              <TagInput
                value={courtIds}
                onChange={setCourtIds}
                placeholder="Nombre del juzgado o tribunal…"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Canales de notificación
              </label>
              <div className="flex gap-3">
                {(['email', 'whatsapp'] as const).map((ch) => (
                  <label key={ch} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={channels.includes(ch)}
                      onChange={() => toggleChannel(ch)}
                      className="w-4 h-4 rounded accent-brand-500"
                    />
                    <span className="text-sm text-slate-700 capitalize">{ch}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Frecuencia
              </label>
              <div className="flex gap-3">
                {[{ v: true, label: 'Inmediata' }, { v: false, label: 'Resumen diario' }].map(({ v, label }) => (
                  <label key={label} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={immediate === v}
                      onChange={() => setImmediate(v)}
                      className="accent-brand-500"
                    />
                    <span className="text-sm text-slate-700">{label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-3 mt-6 justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              disabled={isLoading || channels.length === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-brand-500 rounded-lg hover:bg-brand-700 transition-colors disabled:opacity-60"
            >
              {isLoading ? 'Guardando…' : 'Agregar vigilancia'}
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
