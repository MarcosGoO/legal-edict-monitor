"""
Document Processing Endpoints.

Provides endpoints for:
- Uploading and processing PDF documents
- Extracting entities from text
- Viewing processing results
"""

import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict, Field

from app.services.ocr import SmartOCRService
from app.services.parser import ColombianEntityParser

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class EntityResponse(BaseModel):
    """Response model for extracted entity."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "radicado",
                "raw": "2023-00123-45-67-890-12",
                "normalized": "2023-00123-45-67-890",
                "confidence": 0.95,
                "context": "Radicado No. 2023-00123-45-67-890-12",
            }
        }
    )

    type: str
    raw: str
    normalized: str
    confidence: float
    context: str = ""


class OCRResponse(BaseModel):
    """Response model for OCR results."""
    text_length: int
    word_count: int
    engine_used: str
    confidence: float
    pages_processed: int
    is_searchable: bool


class ParseResponse(BaseModel):
    """Response model for entity parsing."""
    entity_count: int
    entities: list[EntityResponse]
    processing_time_ms: float
    summary: dict[str, int]


class DocumentProcessResponse(BaseModel):
    """Response model for document processing."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "ocr": {
                    "text_length": 5000,
                    "word_count": 750,
                    "engine_used": "native",
                    "confidence": 0.95,
                    "pages_processed": 3,
                    "is_searchable": True,
                },
                "parse": {
                    "entity_count": 5,
                    "entities": [
                        {
                            "type": "radicado",
                            "raw": "2023-00123-45-67-890-12",
                            "normalized": "2023-00123-45-67-890",
                            "confidence": 0.95,
                            "context": "Radicado No. 2023-00123-45-67-890-12",
                        }
                    ],
                    "processing_time_ms": 150.5,
                    "summary": {
                        "radicados": 1,
                        "nits": 2,
                        "cedulas": 1,
                        "names": 1,
                    },
                },
                "error": None,
            }
        }
    )

    success: bool
    ocr: OCRResponse | None = None
    parse: ParseResponse | None = None
    error: str | None = None


class TextParseRequest(BaseModel):
    """Request model for parsing text directly."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": (
                    "El radicado 2023-00123-45-67-890-12 corresponde al proceso "
                    "seguido por JOSÉ MARÍA RODRÍGUEZ con CC 12345678."
                )
            }
        }
    )

    text: str = Field(..., min_length=10, description="Text to parse for entities")


class TextParseResponse(BaseModel):
    """Response model for text parsing."""
    success: bool
    result: ParseResponse | None = None
    error: str | None = None


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/process",
    response_model=DocumentProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a PDF document",
    description="Upload a PDF document for OCR processing and entity extraction.",
)
async def process_document(
    file: Annotated[UploadFile, File(description="PDF file to process")],
) -> DocumentProcessResponse:
    """
    Process a PDF document.
    
    This endpoint:
    1. Extracts text from the PDF using Smart OCR
    2. Parses the text for Colombian legal entities
    3. Returns both OCR results and extracted entities
    
    Supported file types: PDF
    Maximum file size: 50MB
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    # Check file size (50MB limit)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 50MB limit",
        )

    try:
        # Initialize services
        ocr_service = SmartOCRService()
        parser = ColombianEntityParser()

        # Process OCR
        logger.info(f"Processing document: {file.filename}")
        ocr_result = await ocr_service.extract_text_from_bytes(content)

        # Parse entities
        parse_result = parser.parse(ocr_result.text)

        logger.info(
            f"Document processed: {ocr_result.word_count} words, "
            f"{parse_result.entity_count} entities"
        )

        return DocumentProcessResponse(
            success=True,
            ocr=OCRResponse(
                text_length=ocr_result.character_count,
                word_count=ocr_result.word_count,
                engine_used=ocr_result.engine_used.value,
                confidence=ocr_result.confidence,
                pages_processed=ocr_result.pages_processed,
                is_searchable=ocr_result.is_searchable,
            ),
            parse=ParseResponse(
                entity_count=parse_result.entity_count,
                entities=[
                    EntityResponse(
                        type=e.entity_type.value,
                        raw=e.raw_value,
                        normalized=e.normalized_value,
                        confidence=e.confidence,
                        context=e.context[:100] if e.context else "",
                    )
                    for e in parse_result.entities
                ],
                processing_time_ms=parse_result.processing_time_ms,
                summary={
                    "radicados": len(parse_result.radicados),
                    "nits": len(parse_result.nits),
                    "cedulas": len(parse_result.cedulas),
                    "names": len(parse_result.names),
                    "court_ids": len(parse_result.court_ids),
                },
            ),
        )

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return DocumentProcessResponse(
            success=False,
            error=str(e),
        )


@router.post(
    "/parse-text",
    response_model=TextParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse text for entities",
    description="Parse text directly for Colombian legal entities without OCR.",
)
async def parse_text(request: TextParseRequest) -> TextParseResponse:
    """
    Parse text for entities.
    
    This endpoint extracts Colombian legal entities from
    provided text without OCR processing.
    
    Useful for testing entity extraction or processing
    text from other sources.
    """
    try:
        parser = ColombianEntityParser()
        result = parser.parse(request.text)

        return TextParseResponse(
            success=True,
            result=ParseResponse(
                entity_count=result.entity_count,
                entities=[
                    EntityResponse(
                        type=e.entity_type.value,
                        raw=e.raw_value,
                        normalized=e.normalized_value,
                        confidence=e.confidence,
                        context=e.context[:100] if e.context else "",
                    )
                    for e in result.entities
                ],
                processing_time_ms=result.processing_time_ms,
                summary={
                    "radicados": len(result.radicados),
                    "nits": len(result.nits),
                    "cedulas": len(result.cedulas),
                    "names": len(result.names),
                    "court_ids": len(result.court_ids),
                },
            ),
        )

    except Exception as e:
        logger.error(f"Error parsing text: {e}")
        return TextParseResponse(
            success=False,
            error=str(e),
        )


@router.get(
    "/entity-types",
    summary="Get supported entity types",
    description="Returns list of supported entity types for extraction.",
)
async def get_entity_types() -> dict:
    """
    Get supported entity types.
    
    Returns a list of entity types that can be extracted
    from Colombian legal documents.
    """
    return {
        "entity_types": [
            {
                "type": "radicado",
                "description": "23-digit case number",
                "example": "2023-00123-45-67-890-12",
            },
            {
                "type": "nit",
                "description": "Colombian Tax ID (9 digits + check digit)",
                "example": "900123456-7",
            },
            {
                "type": "cedula",
                "description": "Colombian ID (6-12 digits)",
                "example": "12345678",
            },
            {
                "type": "nombre",
                "description": "Person name (extracted via NLP)",
                "example": "JOSÉ MARÍA RODRÍGUEZ",
            },
            {
                "type": "court_id",
                "description": "Court identifier",
                "example": "Juzgado Primero Civil del Circuito",
            },
        ]
    }
