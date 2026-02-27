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
          className="w-full px-3 py-2.5 text-sm border border-ink-700/60 rounded-lg bg-ink-800/50 text-parchment/90 placeholder:text-ink-600 focus:outline-none focus:ring-2 focus:ring-gold-500 focus:border-transparent resize-none"
        />
        <span className="absolute bottom-2.5 right-3 text-xs text-ink-600 font-mono pointer-events-none">
          {text.length} caracteres
        </span>
      </div>

      {tooShort && (
        <p className="text-xs text-amber-400">
          Mínimo {MIN_CHARS} caracteres para procesar.
        </p>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => onProcess(text.trim())}
          disabled={text.trim().length < MIN_CHARS || isLoading}
          className="flex-1 py-2.5 bg-gold-500 text-ink-950 text-sm font-medium rounded-lg hover:bg-gold-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Extrayendo entidades…' : 'Extraer entidades'}
        </button>
        {text && (
          <button
            onClick={() => setText('')}
            className="px-4 py-2.5 text-sm text-parchment/70 bg-ink-800 rounded-lg hover:bg-ink-700 transition-colors"
          >
            Limpiar
          </button>
        )}
      </div>
    </div>
  )
}
