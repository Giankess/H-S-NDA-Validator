from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ...db.session import get_db
from ...db.models import Document, DocumentStatus, AnalysisResult
from ...services.document_storage import DocumentStorage
from ...services.vector_storage import VectorStorage
from ...services.ai_service import AIService
from pydantic import BaseModel
import uuid

router = APIRouter()
document_storage = DocumentStorage()
vector_storage = VectorStorage()
ai_service = AIService()

class DocumentResponse(BaseModel):
    id: str
    status: DocumentStatus
    original_path: str
    redline_path: str | None
    clean_path: str | None

class AnalysisResponse(BaseModel):
    document_id: str
    clauses: List[dict]
    status: DocumentStatus

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new NDA document for analysis"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files are allowed")
    
    # Save the document
    document_id, file_path = await document_storage.save_original_document(file, "user_1")  # TODO: Get actual user_id
    
    # Create document record
    document = Document(
        id=document_id,
        user_id=1,  # TODO: Get actual user_id
        original_path=file_path,
        status=DocumentStatus.UPLOADED
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/{document_id}/analyze", response_model=AnalysisResponse)
async def analyze_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Analyze the document and generate suggestions"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update status
    document.status = DocumentStatus.ANALYZING
    db.commit()
    
    try:
        # Get document content
        content = document_storage.get_document(document.original_path)
        
        # Analyze document
        analysis_results = await ai_service.analyze_document(content)
        
        # Store analysis results
        for result in analysis_results:
            analysis = AnalysisResult(
                document_id=document_id,
                clause_text=result["clause_text"],
                original_text=result["original_text"],
                suggested_text=result["suggested_text"],
                confidence_score=result["confidence_score"]
            )
            db.add(analysis)
        
        # Generate redline document
        redline_content = await ai_service.create_redline_document(content, analysis_results)
        redline_path = document_storage.save_redline_document(redline_content, "user_1", document_id)
        
        # Update document
        document.redline_path = redline_path
        document.status = DocumentStatus.REDLINE_READY
        db.commit()
        
        return {
            "document_id": document_id,
            "clauses": analysis_results,
            "status": document.status
        }
        
    except Exception as e:
        document.status = DocumentStatus.UPLOADED
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/clean")
async def create_clean_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Create a clean version of the document with accepted changes"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.redline_path:
        raise HTTPException(status_code=400, detail="No redline version available")
    
    try:
        # Get redline content
        redline_content = document_storage.get_document(document.redline_path)
        
        # Create clean version
        clean_content = await ai_service.create_clean_document(redline_content)
        clean_path = document_storage.save_clean_document(clean_content, "user_1", document_id)
        
        # Update document
        document.clean_path = clean_path
        document.status = DocumentStatus.COMPLETED
        db.commit()
        
        return {"status": "success", "clean_path": clean_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 