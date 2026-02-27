import { useRef, useState, type DragEvent } from 'react'
import { UploadCloud, FileText, X, AlertCircle } from 'lucide-react'
import { clsx } from 'clsx'

const MAX_SIZE_MB = 50
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

interface PdfUploadTabProps {
  onProcess: (file: File) => void
  isLoading: boolean
}

export default function PdfUploadTab({ onProcess, isLoading }: PdfUploadTabProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [sizeError, setSizeError] = useState(false)
  const [dragging, setDragging] = useState(false)

  const accept = (f: File) => {
    if (f.size > MAX_SIZE_BYTES) { setSizeError(true); setFile(null); return }
    setSizeError(false)
    setFile(f)
  }

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && f.type === 'application/pdf') accept(f)
  }

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) accept(f)
  }

  const handleClear = () => { setFile(null); setSizeError(false); if (inputRef.current) inputRef.current.value = '' }

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !file && inputRef.current?.click()}
        className={clsx(
          'relative border-2 border-dashed rounded-xl p-10 text-center transition-colors',
          !file && 'cursor-pointer',
          dragging
            ? 'border-gold-500 bg-gold-900/30'
            : file
            ? 'border-emerald-500 bg-emerald-50'
            : 'border-ink-700/60 hover:border-gold-500/50 bg-ink-800/30',
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={onFileChange}
          className="sr-only"
        />

        {file ? (
          <div className="flex items-center justify-center gap-3">
            <FileText className="w-8 h-8 text-emerald-400 flex-shrink-0" />
            <div className="text-left">
              <p className="text-sm font-semibold text-parchment truncate max-w-xs">{file.name}</p>
              <p className="text-xs text-ink-600">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); handleClear() }}
              className="ml-2 p-1.5 rounded-full text-ink-600 hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <UploadCloud className="w-10 h-10 text-ink-600 mx-auto" />
            <div>
              <p className="text-sm font-medium text-parchment/80">
                Arrastra un PDF aquí o <span className="text-gold-500">selecciona un archivo</span>
              </p>
              <p className="text-xs text-ink-600 mt-1">Solo archivos PDF · Máximo {MAX_SIZE_MB} MB</p>
            </div>
          </div>
        )}
      </div>

      {sizeError && (
        <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          El archivo supera el límite de {MAX_SIZE_MB} MB.
        </div>
      )}

      <button
        onClick={() => file && onProcess(file)}
        disabled={!file || isLoading}
        className="w-full py-2.5 bg-gold-500 text-ink-950 text-sm font-medium rounded-lg hover:bg-gold-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Procesando documento…' : 'Procesar documento'}
      </button>
    </div>
  )
}
