import { Cpu, FileCheck, Eye } from 'lucide-react'
import type { OCRResponse } from '../../../types/api'

const ENGINE_META: Record<string, { label: string; color: string }> = {
  native:    { label: 'PDF Nativo',    color: 'bg-emerald-100 text-emerald-700' },
  tesseract: { label: 'Tesseract OCR', color: 'bg-blue-100 text-blue-700'      },
  textract:  { label: 'AWS Textract',  color: 'bg-violet-100 text-violet-700'  },
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 90 ? 'bg-emerald-500' : pct >= 70 ? 'bg-amber-400' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-600 w-9 text-right">{pct}%</span>
    </div>
  )
}

export default function OcrSummaryCard({ ocr }: { ocr: OCRResponse }) {
  const engine = ENGINE_META[ocr.engine_used] ?? { label: ocr.engine_used, color: 'bg-slate-100 text-slate-600' }

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">OCR</span>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${engine.color}`}>
          {engine.label}
        </span>
      </div>

      <ConfidenceBar value={ocr.confidence} />

      <div className="grid grid-cols-3 gap-3 pt-1">
        <div className="text-center">
          <p className="text-lg font-bold text-slate-800">{ocr.pages_processed}</p>
          <p className="text-xs text-slate-500">páginas</p>
        </div>
        <div className="text-center border-x border-slate-200">
          <p className="text-lg font-bold text-slate-800">{ocr.word_count.toLocaleString()}</p>
          <p className="text-xs text-slate-500">palabras</p>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1">
            {ocr.is_searchable
              ? <FileCheck className="w-4 h-4 text-emerald-500" />
              : <Eye className="w-4 h-4 text-amber-400" />}
          </div>
          <p className="text-xs text-slate-500">{ocr.is_searchable ? 'Texto nativo' : 'Escaneado'}</p>
        </div>
      </div>
    </div>
  )
}
