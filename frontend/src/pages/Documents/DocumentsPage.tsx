import { useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'
import { FileText, AlignLeft } from 'lucide-react'
import { Card, CardBody } from '../../components/ui/Card'
import PdfUploadTab from './components/PdfUploadTab'
import TextParseTab from './components/TextParseTab'
import ProcessingState from './components/ProcessingState'
import ResultsPanel from './components/ResultsPanel'
import { useProcessDocument, useParseText } from '../../hooks/useDocumentProcessing'
import type { DocumentProcessResponse, TextParseResponse } from '../../types/api'

const tabTriggerCls =
  'flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ' +
  'border-transparent text-ink-600 hover:text-parchment ' +
  'data-[state=active]:border-gold-500 data-[state=active]:text-gold-500'

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

  // Normalise text result into DocumentProcessResponse shape for ResultsPanel
  const result: DocumentProcessResponse | null =
    activeTab === 'pdf'
      ? pdfResult
      : textResult
      ? { success: textResult.success, parse: textResult.result, ocr: null, error: textResult.error }
      : null

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div>
        <h2 className="font-display text-3xl text-parchment">Procesamiento de Documentos</h2>
        <p className="text-xs text-ink-600 uppercase tracking-[0.12em] mt-1">
          Sube un PDF o pega texto para extraer entidades legales colombianas.
        </p>
      </div>

      <Card>
        <Tabs.Root value={activeTab} onValueChange={(v) => setActiveTab(v as 'pdf' | 'text')}>
          <Tabs.List className="flex border-b border-ink-700/40 px-5 pt-4">
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
          <div className="border-t border-ink-700/40">
            <CardBody>
              <ProcessingState mode={activeTab} />
            </CardBody>
          </div>
        )}
      </Card>

      {result && !isLoading && <ResultsPanel result={result} />}
    </div>
  )
}
