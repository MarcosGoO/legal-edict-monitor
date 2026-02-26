import { useMutation } from '@tanstack/react-query'
import { processDocument, parseText } from '../api/documents'

export function useProcessDocument() {
  return useMutation({
    mutationFn: (file: File) => processDocument(file),
  })
}

export function useParseText() {
  return useMutation({
    mutationFn: (text: string) => parseText(text),
  })
}
