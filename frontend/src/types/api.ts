// ============================================================================
// Health / System
// ============================================================================

export interface HealthResponse {
  status: string
  app_name: string
  environment: string
}

export interface ReadyResponse {
  status: string
  checks: {
    database: string
    redis: string
  }
}

// ============================================================================
// Documents
// ============================================================================

export type EntityType = 'radicado' | 'nit' | 'cedula' | 'nombre' | 'court_id'

export interface EntityResponse {
  type: EntityType
  raw: string
  normalized: string
  confidence: number
  context: string
}

export interface OCRResponse {
  text_length: number
  word_count: number
  engine_used: 'native' | 'tesseract' | 'textract' | string
  confidence: number
  pages_processed: number
  is_searchable: boolean
}

export interface ParseSummary {
  radicados: number
  nits: number
  cedulas: number
  names: number
  court_ids: number
}

export interface ParseResponse {
  entity_count: number
  entities: EntityResponse[]
  processing_time_ms: number
  summary: ParseSummary
}

export interface DocumentProcessResponse {
  success: boolean
  ocr: OCRResponse | null
  parse: ParseResponse | null
  error: string | null
}

export interface TextParseRequest {
  text: string
}

export interface TextParseResponse {
  success: boolean
  result: ParseResponse | null
  error: string | null
}

export interface EntityTypeInfo {
  type: EntityType
  description: string
  example: string
}

export interface EntityTypesResponse {
  entity_types: EntityTypeInfo[]
}

// ============================================================================
// Clients
// ============================================================================

export type DocumentType = 'CC' | 'CE' | 'NIT' | 'PP' | 'TI'

export interface ClientCreate {
  full_name: string
  document_type: DocumentType | null
  document_number: string | null
  nit: string | null
  aliases: string[]
  notes: string | null
}

export interface ClientResponse {
  id: string
  full_name: string
  document_type: DocumentType | null
  document_number: string | null
  nit: string | null
  aliases: string[]
  is_active: boolean
}

export interface ClientListResponse {
  clients: ClientResponse[]
  total: number
  page: number
  page_size: number
}

export interface ClientListParams {
  page?: number
  page_size?: number
  is_active?: boolean
  search?: string
}

// ============================================================================
// Watchlist
// ============================================================================

export interface NotificationPreferences {
  channels: ('whatsapp' | 'email')[]
  immediate: boolean
  digest?: boolean
  digest_frequency?: 'daily' | 'weekly'
}

export interface WatchlistCreate {
  client_id: string
  case_numbers: string[]
  court_ids: string[]
  notification_preferences: NotificationPreferences
}

export interface WatchlistResponse {
  id: string
  client_id: string
  case_numbers: string[]
  court_ids: string[]
  is_active: boolean
}

// ============================================================================
// API Errors
// ============================================================================

export interface APIError {
  detail: string | { loc: string[]; msg: string; type: string }[]
}
