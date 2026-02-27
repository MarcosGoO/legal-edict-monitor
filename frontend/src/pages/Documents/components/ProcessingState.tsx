interface ProcessingStateProps {
  mode: 'pdf' | 'text'
}

export default function ProcessingState({ mode }: ProcessingStateProps) {
  return (
    <div className="py-10 flex flex-col items-center gap-4">
      {/* Animated bar */}
      <div className="w-full max-w-xs h-1.5 bg-ink-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gold-500 rounded-full shadow-[0_0_8px_rgba(212,168,67,0.6)] animate-[progress_1.5s_ease-in-out_infinite]"
        />
      </div>
      <p className="text-sm text-parchment/80 font-medium">
        {mode === 'pdf'
          ? 'Extrayendo texto con OCR y detectando entidades…'
          : 'Analizando texto con NLP colombiano…'}
      </p>
      <p className="text-xs text-ink-600">Esto puede tomar unos segundos</p>

      <style>{`
        @keyframes progress {
          0%   { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
      `}</style>
    </div>
  )
}
