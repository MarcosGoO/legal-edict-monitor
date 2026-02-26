import type { DocumentType } from '../types/api'

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  CC: 'C.C.',
  CE: 'C.E.',
  NIT: 'NIT',
  PP: 'Pasaporte',
  TI: 'T.I.',
}

export function formatDocumentType(type: DocumentType | null | undefined): string {
  if (!type) return '—'
  return DOCUMENT_TYPE_LABELS[type] ?? type
}

export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(iso))
}

/** Inserts hyphens if not already formatted */
export function formatRadicado(value: string): string {
  const digits = value.replace(/\D/g, '')
  if (digits.length !== 23) return value
  return `${digits.slice(0, 4)}-${digits.slice(4, 9)}-${digits.slice(9, 11)}-${digits.slice(11, 13)}-${digits.slice(13, 16)}-${digits.slice(16, 18)}-${digits.slice(18, 21)}-${digits.slice(21)}`
}

/** Formats NIT as XXXXXXXXX-X */
export function formatNit(value: string): string {
  const clean = value.replace(/\D/g, '')
  if (clean.length === 10) return `${clean.slice(0, 9)}-${clean.slice(9)}`
  return value
}
