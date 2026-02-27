import { Cpu, FileCheck, Eye } from 'lucide-react'
import type { OCRResponse } from '../../../types/api'

const ENGINE_META: Record<string, { label: string; color: string }> = {
  native:    { label: 'PDF Nativo',    color: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
  tesseract: { label: 'Tesseract OCR', color: 'bg-blue-50 text-blue-700 border border-blue-200'         },
  textract:  { label: 'AWS Textract',  color: 'bg-violet-50 text-violet-700 border border-violet-200'   },
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 90 ? 'bg-emerald-500' : pct >= 70 ? 'bg-amber-400' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-ink-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-ink-600 w-9 text-right">{pct}%</span>
    </div>
  )
}

export default function OcrSummaryCard({ ocr }: { ocr: OCRResponse }) {
  const engine = ENGINE_META[ocr.engine_used] ?? { label: ocr.engine_used, color: 'bg-slate-100 text-slate-600 border border-slate-200' }

  return (
    <div className="bg-ink-800/50 border border-ink-700/40 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-ink-600" />
          <span className="text-xs font-semibold text-ink-600 uppercase tracking-wider">OCR</span>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${engine.color}`}>
          {engine.label}
        </span>
      </div>

      <ConfidenceBar value={ocr.confidence} />

      <div className="grid grid-cols-3 gap-3 pt-1">
        <div className="text-center">
          <p className="font-display text-2xl text-parchment">{ocr.pages_processed}</p>
          <p className="text-xs text-ink-600">páginas</p>
        </div>
        <div className="text-center border-x border-ink-700/40">
          <p className="font-display text-2xl text-parchment">{ocr.word_count.toLocaleString()}</p>
          <p className="text-xs text-ink-600">palabras</p>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1">
            {ocr.is_searchable
              ? <FileCheck className="w-4 h-4 text-emerald-400" />
              : <Eye className="w-4 h-4 text-amber-400" />}
          </div>
          <p className="text-xs text-ink-600">{ocr.is_searchable ? 'Texto nativo' : 'Escaneado'}</p>
        </div>
      </div>
    </div>
  )
}
