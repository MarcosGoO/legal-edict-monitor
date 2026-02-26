import { clsx } from 'clsx'

interface MonoValueProps {
  value: string | null | undefined
  className?: string
  /** Copy to clipboard on click */
  copyable?: boolean
}

export default function MonoValue({ value, className, copyable }: MonoValueProps) {
  if (!value) return <span className="text-slate-400">—</span>

  const handleClick = () => {
    if (copyable && value) {
      navigator.clipboard.writeText(value).catch(() => {})
    }
  }

  return (
    <span
      className={clsx(
        'font-mono text-sm tracking-tight text-slate-800',
        copyable && 'cursor-pointer hover:text-brand-500 transition-colors',
        className,
      )}
      onClick={copyable ? handleClick : undefined}
      title={copyable ? 'Clic para copiar' : undefined}
    >
      {value}
    </span>
  )
}
