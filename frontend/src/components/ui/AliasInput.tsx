import { useState, type KeyboardEvent } from 'react'
import { X } from 'lucide-react'
import { clsx } from 'clsx'

interface AliasInputProps {
  value: string[]
  onChange: (aliases: string[]) => void
  placeholder?: string
  className?: string
}

export default function AliasInput({
  value,
  onChange,
  placeholder = 'Escribe un alias y presiona Enter',
  className,
}: AliasInputProps) {
  const [input, setInput] = useState('')

  const add = () => {
    const trimmed = input.trim().toUpperCase()
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed])
    }
    setInput('')
  }

  const remove = (alias: string) => onChange(value.filter((a) => a !== alias))

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      add()
    } else if (e.key === 'Backspace' && input === '' && value.length > 0) {
      remove(value[value.length - 1])
    }
  }

  return (
    <div
      className={clsx(
        'min-h-[42px] flex flex-wrap gap-1.5 px-3 py-2 border border-slate-200 rounded-lg bg-white',
        'focus-within:ring-2 focus-within:ring-brand-500 focus-within:border-transparent',
        className,
      )}
    >
      {value.map((alias) => (
        <span
          key={alias}
          className="inline-flex items-center gap-1 px-2 py-0.5 bg-brand-100 text-brand-800 text-xs font-medium rounded"
        >
          {alias}
          <button
            type="button"
            onClick={() => remove(alias)}
            className="hover:text-brand-600 transition-colors"
            aria-label={`Eliminar alias ${alias}`}
          >
            <X className="w-3 h-3" />
          </button>
        </span>
      ))}
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKey}
        onBlur={add}
        placeholder={value.length === 0 ? placeholder : ''}
        className="flex-1 min-w-[140px] text-sm outline-none bg-transparent text-slate-800 placeholder:text-slate-400"
      />
    </div>
  )
}
