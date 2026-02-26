import { useState } from 'react'

interface TextParseTabProps {
  onProcess: (text: string) => void
  isLoading: boolean
}

const MIN_CHARS = 10
const EXAMPLE =
  'El radicado 11001310300120230012300 corresponde al proceso seguido por JOSÉ MARÍA RODRÍGUEZ GARCÍA con CC 12345678 ante el Juzgado Primero Civil del Circuito.'

export default function TextParseTab({ onProcess, isLoading }: TextParseTabProps) {
  const [text, setText] = useState('')
  const tooShort = text.trim().length > 0 && text.trim().length < MIN_CHARS

  return (
    <div className="space-y-3">
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          placeholder={`Pega texto con entidades legales colombianas…\n\nEjemplo:\n${EXAMPLE}`}
          className="w-full px-3 py-2.5 text-sm border border-slate-200 rounded-lg bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent resize-none"
        />
        <span className="absolute bottom-2.5 right-3 text-xs text-slate-400 pointer-events-none">
          {text.length} caracteres
        </span>
      </div>

      {tooShort && (
        <p className="text-xs text-amber-600">
          Mínimo {MIN_CHARS} caracteres para procesar.
        </p>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => onProcess(text.trim())}
          disabled={text.trim().length < MIN_CHARS || isLoading}
          className="flex-1 py-2.5 bg-brand-500 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Extrayendo entidades…' : 'Extraer entidades'}
        </button>
        {text && (
          <button
            onClick={() => setText('')}
            className="px-4 py-2.5 text-sm text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
          >
            Limpiar
          </button>
        )}
      </div>
    </div>
  )
}
