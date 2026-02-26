"""
Smart OCR Service.

Intelligent OCR wrapper that:
1. Analyzes PDFs to detect text vs scanned content
2. Selects the best extraction method
3. Falls back through multiple OCR engines
4. Caches results to avoid re-processing
"""

import logging
import tempfile
from pathlib import Path
from typing import BinaryIO

from app.config import settings
from app.services.ocr.base import (
    OCREngine,
    OCREngineBase,
    OCRResult,
    PDFAnalysis,
)

logger = logging.getLogger(__name__)


class SmartOCRService:
    """
    Intelligent OCR wrapper that selects the best extraction method.
    
    Usage:
        service = SmartOCRService()
        result = await service.process_pdf("document.pdf")
        print(result.text)
    """

    def __init__(
        self,
        confidence_threshold: float | None = None,
        enable_textract_fallback: bool | None = None,
        language: str | None = None,
    ):
        """
        Initialize Smart OCR Service.
        
        Args:
            confidence_threshold: Minimum confidence for quality check
            enable_textract_fallback: Enable AWS Textract as fallback
            language: OCR language (default: Spanish)
        """
        self.confidence_threshold = confidence_threshold or settings.ocr_confidence_threshold
        self.enable_textract_fallback = (
            enable_textract_fallback
            if enable_textract_fallback is not None
            else settings.enable_textract_fallback
        )
        self.language = language or settings.tesseract_lang

        # Lazy load engines
        self._native_engine: OCREngineBase | None = None
        self._tesseract_engine: OCREngineBase | None = None
        self._textract_engine: OCREngineBase | None = None

    @property
    def native_engine(self) -> OCREngineBase:
        """Get native PDF engine (lazy load)."""
        if self._native_engine is None:
            from app.services.ocr.engines.native import NativePDFEngine
            self._native_engine = NativePDFEngine()
        return self._native_engine

    @property
    def tesseract_engine(self) -> OCREngineBase:
        """Get Tesseract engine (lazy load)."""
        if self._tesseract_engine is None:
            from app.services.ocr.engines.tesseract import TesseractEngine
            self._tesseract_engine = TesseractEngine(language=self.language)
        return self._tesseract_engine

    @property
    def textract_engine(self) -> OCREngineBase | None:
        """Get AWS Textract engine (lazy load)."""
        if not self.enable_textract_fallback:
            return None
        if self._textract_engine is None:
            from app.services.ocr.engines.textract import TextractEngine
            self._textract_engine = TextractEngine()
        return self._textract_engine

    async def analyze_pdf(self, pdf_path: Path) -> PDFAnalysis:
        """
        Analyze PDF to determine best extraction strategy.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            PDFAnalysis with recommendations
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.warning("PyMuPDF not available, defaulting to OCR")
            return PDFAnalysis(
                has_text_layer=False,
                page_count=1,
                is_scanned=True,
                estimated_quality=0.0,
                recommended_engine=OCREngine.TESSERACT,
            )

        doc = fitz.open(pdf_path)
        page_count = len(doc)

        # Sample first 3 pages for text
        total_text = ""
        sample_pages = min(3, page_count)

        for i in range(sample_pages):
            page = doc[i]
            total_text += page.get_text()

        doc.close()

        # Analyze text content
        text_length = len(total_text.strip())
        has_text = text_length > 100
        is_scanned = not has_text

        # Estimate quality based on text density
        if page_count > 0:
            text_per_page = text_length / page_count
            estimated_quality = min(text_per_page / 1000, 1.0)
        else:
            estimated_quality = 0.0

        # Recommend engine
        if has_text:
            recommended = OCREngine.NATIVE
        else:
            recommended = OCREngine.TESSERACT

        return PDFAnalysis(
            has_text_layer=has_text,
            page_count=page_count,
            is_scanned=is_scanned,
            estimated_quality=estimated_quality,
            recommended_engine=recommended,
            text_sample=total_text[:500] if total_text else "",
        )

    async def process_pdf(
        self,
        pdf_source: Path | BinaryIO,
        force_ocr: bool = False,
    ) -> OCRResult:
        """
        Process PDF and extract text using the best available method.
        
        Args:
            pdf_source: Path to PDF file or file-like object
            force_ocr: Skip native extraction and force OCR
            
        Returns:
            OCRResult with extracted text and metadata
        """
        # Handle file-like objects
        temp_path: Path | None = None
        if isinstance(pdf_source, BinaryIO):
            temp_path = await self._save_temp_pdf(pdf_source)
            pdf_path = temp_path
        else:
            pdf_path = pdf_source

        try:
            # Analyze document
            analysis = await self.analyze_pdf(pdf_path)
            logger.info(
                f"PDF analysis: {analysis.page_count} pages, "
                f"text_layer={analysis.has_text_layer}, "
                f"scanned={analysis.is_scanned}"
            )

            # Try native extraction first
            if analysis.has_text_layer and not force_ocr:
                result = await self.native_engine.extract_text(pdf_path)
                if result.is_quality_acceptable:
                    logger.info(
                        f"Native extraction successful: "
                        f"{result.word_count} words, "
                        f"confidence={result.confidence:.2f}"
                    )
                    return result
                logger.warning(
                    f"Native extraction quality low (confidence={result.confidence:.2f}), "
                    "falling back to OCR"
                )

            # Try Tesseract OCR
            if await self.tesseract_engine.is_available():
                result = await self.tesseract_engine.extract_text(pdf_path)
                if result.is_quality_acceptable:
                    logger.info(
                        f"Tesseract OCR successful: "
                        f"{result.word_count} words, "
                        f"confidence={result.confidence:.2f}"
                    )
                    return result
                logger.warning(
                    f"Tesseract quality low (confidence={result.confidence:.2f})"
                )

            # Fallback to AWS Textract if enabled
            if self.enable_textract_fallback and self.textract_engine:
                if await self.textract_engine.is_available():
                    logger.info("Falling back to AWS Textract")
                    result = await self.textract_engine.extract_text(pdf_path)
                    logger.info(
                        f"Textract extraction: "
                        f"{result.word_count} words, "
                        f"confidence={result.confidence:.2f}"
                    )
                    return result

            # Return best effort result
            logger.warning("All OCR engines failed or unavailable")
            return OCRResult(
                text="",
                engine_used=OCREngine.TESSERACT,
                confidence=0.0,
                pages_processed=analysis.page_count,
                is_searchable=False,
                metadata={"error": "All OCR engines failed"},
            )

        finally:
            # Clean up temp file if created
            if temp_path and temp_path.exists():
                temp_path.unlink()

    async def _save_temp_pdf(self, file_obj: BinaryIO) -> Path:
        """Save file-like object to temporary path."""
        import os

        temp_dir = tempfile.gettempdir()
        temp_path = Path(temp_dir) / f"ocr_{os.getpid()}_{id(file_obj)}.pdf"

        file_obj.seek(0)
        with open(temp_path, "wb") as f:
            f.write(file_obj.read())

        return temp_path

    async def extract_text_from_bytes(
        self,
        pdf_bytes: bytes,
        use_cache: bool = True,
    ) -> OCRResult:
        """
        Extract text from PDF bytes.
        
        Convenience method for processing PDFs in memory.
        Uses caching to avoid re-processing the same documents.
        
        Args:
            pdf_bytes: PDF file as bytes
            use_cache: Whether to use caching (default: True)
            
        Returns:
            OCRResult with extracted text
        """
        import os

        from app.services.cache import CacheService, get_cache_service

        # Compute document hash for caching
        doc_hash = CacheService.compute_document_hash(pdf_bytes)

        # Check cache if enabled
        if use_cache:
            cache = get_cache_service()
            cached_result = await cache.get_ocr_result(doc_hash)

            if cached_result:
                logger.info(f"Using cached OCR result for {doc_hash[:16]}...")
                return OCRResult.from_dict(cached_result)

        temp_dir = tempfile.gettempdir()
        temp_path = Path(temp_dir) / f"ocr_{os.getpid()}_{id(pdf_bytes)}.pdf"

        try:
            with open(temp_path, "wb") as f:
                f.write(pdf_bytes)

            result = await self.process_pdf(temp_path)

            # Cache the result if caching is enabled
            if use_cache and result.text:
                await cache.set_ocr_result(doc_hash, result.to_dict())

            return result
        finally:
            if temp_path.exists():
                temp_path.unlink()
