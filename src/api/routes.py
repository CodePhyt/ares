"""
FastAPI routes for ARES API endpoints.
Clean, well-documented endpoints with Swagger integration.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger
import os
import uuid
from pathlib import Path
from datetime import datetime

from src.api.config import settings
from src.core.rag_engine import HybridRAGEngine
from src.core.agents import ReasoningAgent
from src.core.document_processor import DocumentProcessor
from src.security.pii_masker import GermanPIIMasker
from src.utils.validators import validate_file_extension, parse_size, validate_query_length
from src.api.metrics import metrics_collector
import time

# Initialize global components
rag_engine = HybridRAGEngine(
    chroma_db_path=settings.CHROMA_DB_PATH,
    collection_name=settings.CHROMA_COLLECTION_NAME,
    ollama_base_url=settings.OLLAMA_BASE_URL,
    embedding_model=settings.OLLAMA_EMBEDDING_MODEL,
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
)

pii_masker = GermanPIIMasker(masking_strategy=settings.PII_MASKING_STRATEGY)

reasoning_agent = ReasoningAgent(
    rag_engine=rag_engine,
    pii_masker=pii_masker,
    ollama_base_url=settings.OLLAMA_BASE_URL,
    model=settings.OLLAMA_MODEL,
    temperature=settings.TEMPERATURE,
    max_iterations=settings.MAX_ITERATIONS,
)

router = APIRouter()

# Request/Response models
class QueryRequest(BaseModel):
    """Query request model."""
    query: str = Field(..., description="User query/question")
    mask_pii: bool = Field(True, description="Enable PII masking")
    top_k: Optional[int] = Field(5, description="Number of documents to retrieve")


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str = Field(..., description="Generated answer")
    citations: List[dict] = Field(default_factory=list, description="Source citations")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    context_used: str = Field("", description="Context snippets used")
    iterations: int = Field(0, description="Number of reasoning iterations")
    pii_masked: bool = Field(False, description="Whether PII was masked")
    pii_count: int = Field(0, description="Number of PII entities found")


class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    chunks_created: int = Field(..., description="Number of chunks created")
    pii_detected: int = Field(0, description="Number of PII entities detected")
    status: str = Field("success", description="Upload status")


class PIIDetectionRequest(BaseModel):
    """PII detection request model."""
    text: str = Field(..., description="Text to analyze for PII")


class PIIDetectionResponse(BaseModel):
    """PII detection response model."""
    detections: List[dict] = Field(default_factory=list, description="Detected PII entities")
    total_pii: int = Field(0, description="Total number of PII entities")
    entity_breakdown: dict = Field(default_factory=dict, description="Breakdown by entity type")
    compliance_status: str = Field("compliant", description="Compliance status")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents using the reasoning agent.

    - **query**: User question or query
    - **mask_pii**: Whether to mask PII before processing
    - **top_k**: Number of documents to retrieve

    Returns a comprehensive answer with citations and confidence score.
    """
    start_time = time.time()
    try:
        # Validate query
        is_valid, error_msg = validate_query_length(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info("Processing query: {}", request.query[:50])

        response = await reasoning_agent.query(
            query=request.query,
            mask_pii=request.mask_pii,
        )
        
        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record_query(duration)

        return QueryResponse(**response)

    except Exception as e:
        logger.error("Error processing query: {}", e)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and index a document.

    Supported formats: PDF, DOCX, TXT, MD, XLSX

    The document will be:
    - Processed and chunked
    - Scanned for PII
    - Indexed in the vector database
    """
    try:
        # Validate file type
        allowed_extensions = settings.ALLOWED_EXTENSIONS.split(",")
        if not validate_file_extension(file.filename, allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}",
            )

        # Validate file size
        max_size_bytes = parse_size(settings.MAX_UPLOAD_SIZE)

        # Save uploaded file
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)
        
        document_id = str(uuid.uuid4())
        file_path = upload_dir / f"{document_id}_{file.filename}"
        
        content = await file.read()
        
        # Check file size
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE}",
            )
        
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info("Processing uploaded file: {}", file.filename)
        upload_start = time.time()

        # Process document
        processor = DocumentProcessor()
        result = processor.process_file(str(file_path))

        # Detect PII
        pii_audit = pii_masker.audit_document(result["text"])
        pii_count = pii_audit["total_pii"]

        # Mask PII if enabled
        text_to_index = result["text"]
        if settings.ENABLE_PII_MASKING and pii_count > 0:
            mask_result = pii_masker.mask_text(text_to_index)
            text_to_index = mask_result["masked_text"]
            logger.info("PII masked before indexing: {} entities", pii_count)

        # Index document
        chunks_created = rag_engine.index_document(
            document_id=document_id,
            text=text_to_index,
            metadata={
                "filename": file.filename,
                "file_type": file_extension,
                **result["metadata"],
            },
        )
        
        # Record metrics
        upload_duration = time.time() - upload_start
        metrics_collector.record_upload(upload_duration)

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            chunks_created=chunks_created,
            pii_detected=pii_count,
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading document: {}", e)
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks from the index.
    """
    try:
        success = rag_engine.delete_document(document_id)
        
        if success:
            return {"status": "deleted", "document_id": document_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting document: {}", e)
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.post("/pii/detect", response_model=PIIDetectionResponse)
async def detect_pii(request: PIIDetectionRequest):
    """
    Detect PII in text without masking.

    Useful for compliance auditing and reporting.
    """
    try:
        audit_result = pii_masker.audit_document(request.text)
        
        return PIIDetectionResponse(
            detections=audit_result["detections"],
            total_pii=audit_result["total_pii"],
            entity_breakdown=audit_result["entity_breakdown"],
            compliance_status=audit_result["compliance_status"],
        )

    except Exception as e:
        logger.error("Error detecting PII: {}", e)
        raise HTTPException(status_code=500, detail=f"Error detecting PII: {str(e)}")


@router.post("/pii/mask")
async def mask_pii(request: PIIDetectionRequest):
    """
    Mask PII in text according to configured strategy.

    Returns the masked text and audit information.
    """
    try:
        mask_result = pii_masker.mask_text(request.text)
        
        return {
            "masked_text": mask_result["masked_text"],
            "original_text": mask_result["original_text"],
            "detections": mask_result["detections"],
            "pii_count": mask_result["pii_count"],
            "masked": mask_result["masked"],
            "entities_found": mask_result.get("entities_found", []),
        }

    except Exception as e:
        logger.error("Error masking PII: {}", e)
        raise HTTPException(status_code=500, detail=f"Error masking PII: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    Get system statistics and health information.
    """
    try:
        # Get collection count (approximate)
        collection_info = rag_engine.collection.get()
        document_count = len(set(
            meta.get("document_id", "unknown")
            for meta in collection_info.get("metadatas", [])
        )) if collection_info.get("metadatas") else 0
        
        chunk_count = len(collection_info.get("ids", []))

        # Get API metrics
        api_metrics = metrics_collector.get_stats()

        return {
            "documents_indexed": document_count,
            "chunks_indexed": chunk_count,
            "pii_masking_enabled": settings.ENABLE_PII_MASKING,
            "rag_engine": "hybrid",
            "vector_db": "ChromaDB",
            "keyword_search": "BM25",
            "reranking": "Cross-Encoder",
            "api_metrics": api_metrics,
        }

    except Exception as e:
        logger.error("Error getting stats: {}", e)
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/metrics")
async def get_metrics():
    """
    Get detailed API metrics and performance statistics.
    """
    try:
        return metrics_collector.get_stats()
    except Exception as e:
        logger.error("Error getting metrics: {}", e)
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.post("/metrics/reset")
async def reset_metrics():
    """
    Reset all metrics (admin operation).
    """
    try:
        metrics_collector.reset()
        return {"status": "metrics_reset", "message": "All metrics have been reset"}
    except Exception as e:
        logger.error("Error resetting metrics: {}", e)
        raise HTTPException(status_code=500, detail=f"Error resetting metrics: {str(e)}")


@router.get("/system/health")
async def get_system_health():
    """
    Get detailed system health metrics including memory usage and inference speed.
    """
    try:
        import psutil
        import os
        
        # Get process memory
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Get system memory
        system_memory = psutil.virtual_memory()
        
        # Get metrics
        api_metrics = metrics_collector.get_stats()
        
        # Calculate inference speed (tokens per second approximation)
        inference_speed = 0.0
        if api_metrics.get("query_timing"):
            avg_query_time = api_metrics["query_timing"]["avg_ms"] / 1000  # seconds
            # Approximate: assume 50 tokens per query on average
            if avg_query_time > 0:
                inference_speed = 50 / avg_query_time  # tokens per second
        
        # Get ChromaDB size (approximate)
        chromadb_size = 0
        try:
            db_path = Path(settings.CHROMA_DB_PATH)
            if db_path.exists():
                for file_path in db_path.rglob("*"):
                    if file_path.is_file():
                        chromadb_size += file_path.stat().st_size
                chromadb_size = chromadb_size / 1024 / 1024  # MB
        except Exception:
            pass
        
        return {
            "status": "healthy",
            "memory": {
                "process_mb": round(process_memory, 2),
                "system_total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                "system_available_gb": round(system_memory.available / 1024 / 1024 / 1024, 2),
                "system_used_percent": round(system_memory.percent, 2),
                "chromadb_size_mb": round(chromadb_size, 2),
            },
            "performance": {
                "inference_speed_tokens_per_sec": round(inference_speed, 2),
                "avg_query_time_ms": api_metrics.get("query_timing", {}).get("avg_ms", 0),
                "avg_response_time_ms": api_metrics.get("request_timing", {}).get("avg_ms", 0),
            },
            "api_metrics": api_metrics,
        }
    except ImportError:
        # psutil not available, return basic metrics
        api_metrics = metrics_collector.get_stats()
        return {
            "status": "healthy",
            "memory": {"note": "psutil not installed, install for detailed memory metrics"},
            "performance": {
                "avg_query_time_ms": api_metrics.get("query_timing", {}).get("avg_ms", 0),
                "avg_response_time_ms": api_metrics.get("request_timing", {}).get("avg_ms", 0),
            },
            "api_metrics": api_metrics,
        }
    except Exception as e:
        logger.error("Error getting system health: {}", e)
        raise HTTPException(status_code=500, detail=f"Error getting system health: {str(e)}")


@router.get("/documents/graph")
async def get_document_graph():
    """
    Get document relationship graph data.
    """
    try:
        from src.utils.document_graph import DocumentGraphBuilder
        
        # Get all documents from ChromaDB
        collection_info = rag_engine.collection.get()
        
        if not collection_info.get("metadatas"):
            return {"nodes": [], "edges": [], "stats": {}}
        
        # Group by document_id
        documents = {}
        for i, metadata in enumerate(collection_info["metadatas"]):
            doc_id = metadata.get("document_id", "unknown")
            if doc_id not in documents:
                documents[doc_id] = {
                    "document_id": doc_id,
                    "filename": metadata.get("filename", "Unknown"),
                    "metadata": metadata,
                    "chunks": [],
                }
            documents[doc_id]["chunks"].append(collection_info["documents"][i])
        
        # Build graph
        graph_builder = DocumentGraphBuilder()
        graph_data = graph_builder.build_relationship_graph(list(documents.values()))
        
        return graph_data
        
    except Exception as e:
        logger.error("Error building document graph: {}", e)
        raise HTTPException(status_code=500, detail=f"Error building document graph: {str(e)}")


class AuditExportRequest(BaseModel):
    """Audit export request model."""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    citations: List[dict] = Field(default_factory=list, description="Source citations")
    confidence: float = Field(..., description="Confidence score")
    pii_count: int = Field(0, description="Number of PII entities masked")
    iterations: int = Field(0, description="Number of reasoning iterations")


@router.post("/export/audit-pdf")
async def export_audit_pdf(request: AuditExportRequest):
    """
    Export audit report as PDF with ARES watermark.
    Returns the PDF file for download.
    """
    try:
        from src.utils.pdf_exporter import ARESPDFExporter
        from pathlib import Path
        
        exporter = ARESPDFExporter()
        
        # Create exports directory
        exports_dir = Path("./exports")
        exports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = exports_dir / f"ares_audit_{timestamp}.pdf"
        
        exporter.export_audit_report(
            output_path=str(output_path),
            query=request.query,
            answer=request.answer,
            citations=request.citations,
            confidence=request.confidence,
            pii_count=request.pii_count,
            metadata={"iterations": request.iterations},
        )
        
        # Return file for download
        return FileResponse(
            path=str(output_path),
            filename=f"ARES_Audit_Report_{timestamp}.pdf",
            media_type="application/pdf",
        )
        
    except Exception as e:
        logger.error("Error exporting PDF: {}", e)
        raise HTTPException(status_code=500, detail=f"Error exporting PDF: {str(e)}")
