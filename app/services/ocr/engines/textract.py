"""
AWS Textract OCR Engine.

Cloud-based OCR using AWS Textract for high-accuracy extraction.
Used as fallback when Tesseract confidence is low.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from app.config import settings
from app.services.ocr.base import (
    OCREngine,
    OCREngineBase,
    OCRResult,
)

logger = logging.getLogger(__name__)


class TextractEngine(OCREngineBase):
    """
    AWS Textract engine for high-accuracy OCR.
    
    Used as fallback when Tesseract confidence is low.
    Supports async processing for large documents.
    """
    
    def __init__(
        self,
        region: str | None = None,
        profile_name: str | None = None,
    ):
        """
        Initialize Textract engine.
        
        Args:
            region: AWS region
            profile_name: AWS profile name (optional)
        """
        self.region = region or settings.aws_region
        self.profile_name = profile_name
        self._client: Any = None
    
    @property
    def client(self) -> Any:
        """Get or create Textract client (lazy load)."""
        if self._client is None:
            import boto3
            
            session = boto3.Session(
                profile_name=self.profile_name,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
            self._client = session.client("textract", region_name=self.region)
        return self._client
    
    async def is_available(self) -> bool:
        """Check if AWS credentials are configured."""
        try:
            # Try a simple API call
            self.client.get_document_text_detection(JobId="test")
        except self.client.exceptions.InvalidJobIdException:
            return True
        except Exception as e:
            logger.warning(f"Textract not available: {e}")
            return False
        return True
    
    async def extract_text(self, pdf_path: Path) -> OCRResult:
        """
        Extract text using AWS Textract.
        
        Uses async document analysis for better handling
        of complex legal documents.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            OCRResult with extracted text
        """
        # Read PDF bytes
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Check file size (Textract has limits)
        file_size_mb = len(pdf_bytes) / (1024 * 1024)
        if file_size_mb > 500:  # 500 MB limit
            logger.error(f"File too large for Textract: {file_size_mb:.1f} MB")
            return OCRResult(
                text="",
                engine_used=OCREngine.TEXTRACT,
                confidence=0.0,
                pages_processed=0,
                is_searchable=False,
                metadata={"error": "File too large for Textract"},
            )
        
        # Start async job
        try:
            response = self.client.start_document_text_detection(
                Document={"Bytes": pdf_bytes}
            )
            job_id = response["JobId"]
            logger.info(f"Started Textract job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to start Textract job: {e}")
            return OCRResult(
                text="",
                engine_used=OCREngine.TEXTRACT,
                confidence=0.0,
                pages_processed=0,
                is_searchable=False,
                metadata={"error": str(e)},
            )
        
        # Poll for completion
        result = await self._poll_job(job_id)
        
        # Extract text blocks
        blocks = result.get("Blocks", [])
        text_blocks = [b for b in blocks if b["BlockType"] == "LINE"]
        
        # Calculate confidence
        confidences = [b.get("Confidence", 100) for b in text_blocks]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Build text
        text_lines = [b["Text"] for b in text_blocks]
        full_text = "\n".join(text_lines)
        
        # Count pages
        pages = set()
        for block in blocks:
            if "Page" in block:
                pages.add(block["Page"])
        page_count = len(pages) if pages else 1
        
        return OCRResult(
            text=full_text,
            engine_used=OCREngine.TEXTRACT,
            confidence=avg_confidence / 100,
            pages_processed=page_count,
            is_searchable=False,
            metadata={
                "job_id": job_id,
                "blocks_count": len(blocks),
                "lines_count": len(text_blocks),
                "region": self.region,
            },
        )
    
    async def _poll_job(
        self,
        job_id: str,
        timeout: int = 300,
        poll_interval: int = 2,
    ) -> dict[str, Any]:
        """
        Poll Textract job until completion.
        
        Args:
            job_id: Textract job ID
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between polls
            
        Returns:
            Job result dictionary
        """
        import time
        
        start_time = time.time()
        
        while True:
            response = self.client.get_document_text_detection(JobId=job_id)
            status = response["JobStatus"]
            
            if status == "SUCCEEDED":
                logger.info(f"Textract job completed: {job_id}")
                return response
            elif status == "FAILED":
                error_msg = response.get("StatusMessage", "Unknown error")
                raise Exception(f"Textract job failed: {error_msg}")
            elif status == "PARTIAL_SUCCESS":
                logger.warning(f"Textract job partial success: {job_id}")
                return response
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Textract job timed out after {timeout}s: {job_id}"
                )
            
            logger.debug(
                f"Textract job {job_id} status: {status} "
                f"(elapsed: {elapsed:.0f}s)"
            )
            await asyncio.sleep(poll_interval)
