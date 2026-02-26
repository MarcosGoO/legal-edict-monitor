import * as Tabs from '@radix-ui/react-tabs'
import { FileText, AlignLeft } from 'lucide-react'
import { Card, CardBody } from '../../components/ui/Card'
import PdfUploadTab from './components/PdfUploadTab'
import TextParseTab from './components/TextParseTab'
import ProcessingState from './components/ProcessingState'
import { useProcessDocument, useParseText } from '../../hooks/useDocumentProcessing'
import type { DocumentProcessResponse, TextParseResponse } from '../../types/api'
import { useState } from 'react'

const tabTriggerCls =
  'flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ' +
  'border-transparent text-slate-500 hover:text-slate-700 ' +
  'data-[state=active]:border-brand-500 data-[state=active]:text-brand-600'

export default function DocumentsPage() {
  const [activeTab, setActiveTab] = useState<'pdf' | 'text'>('pdf')
  const [pdfResult, setPdfResult] = useState<DocumentProcessResponse | null>(null)
  const [textResult, setTextResult] = useState<TextParseResponse | null>(null)

  const pdfMutation = useProcessDocument()
  const textMutation = useParseText()

  const handlePdf = async (file: File) => {
    setPdfResult(null)
    const res = await pdfMutation.mutateAsync(file)
    setPdfResult(res)
  }

  const handleText = async (text: string) => {
    setTextResult(null)
    const res = await textMutation.mutateAsync(text)
    setTextResult(res)
  }

  const isLoading =
    (activeTab === 'pdf' && pdfMutation.isPending) ||
    (activeTab === 'text' && textMutation.isPending)

  const result = activeTab === 'pdf' ? pdfResult : textResult?.result
    ? { success: textResult.success, parse: textResult.result, ocr: null, error: textResult.error }
    : null

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Procesamiento de Documentos</h2>
        <p className="text-sm text-slate-500 mt-0.5">
          Sube un PDF o pega texto para extraer entidades legales colombianas.
        </p>
      </div>

      <Card>
        <Tabs.Root
          value={activeTab}
          onValueChange={(v) => setActiveTab(v as 'pdf' | 'text')}
        >
          <Tabs.List className="flex border-b border-slate-200 px-5 pt-4">
            <Tabs.Trigger value="pdf" className={`focus:outline-none ${tabTriggerCls}`}>
              <FileText className="w-4 h-4" />
              Subir PDF
            </Tabs.Trigger>
            <Tabs.Trigger value="text" className={`focus:outline-none ${tabTriggerCls}`}>
              <AlignLeft className="w-4 h-4" />
              Pegar texto
            </Tabs.Trigger>
          </Tabs.List>

          <CardBody>
            <Tabs.Content value="pdf" className="focus:outline-none">
              <PdfUploadTab onProcess={handlePdf} isLoading={pdfMutation.isPending} />
            </Tabs.Content>
            <Tabs.Content value="text" className="focus:outline-none">
              <TextParseTab onProcess={handleText} isLoading={textMutation.isPending} />
            </Tabs.Content>
          </CardBody>
        </Tabs.Root>

        {isLoading && (
          <div className="border-t border-slate-100">
            <CardBody>
              <ProcessingState mode={activeTab} />
            </CardBody>
          </div>
        )}
      </Card>

      {/* Results area — populated in Task 9 */}
      {result && !isLoading && (
        <ResultsPlaceholder result={result} />
      )}
    </div>
  )
}

// Temporary placeholder — replaced with full ResultsPanel in Task 9
function ResultsPlaceholder({ result }: { result: DocumentProcessResponse }) {
  if (!result.success || !result.parse) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center gap-2 text-red-600 text-sm">
            <span className="font-medium">Error:</span>
            <span>{result.error ?? 'No se pudo procesar el documento.'}</span>
          </div>
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardBody>
        <p className="text-sm font-semibold text-slate-700 mb-2">
          {result.parse.entity_count} entidad{result.parse.entity_count !== 1 ? 'es' : ''} encontrada{result.parse.entity_count !== 1 ? 's' : ''}
        </p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(result.parse.summary).map(([type, count]) =>
            count > 0 ? (
              <span key={type} className="px-2.5 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-700">
                {count} {type}
              </span>
            ) : null,
          )}
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Los resultados detallados aparecerán aquí en la próxima tarea de desarrollo.
        </p>
      </CardBody>
    </Card>
  )
}
