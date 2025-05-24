from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...db.session import get_db
from ...db.models import Document, DocumentStatus, AnalysisResult
from ...services.document_storage import DocumentStorage
from ...services.vector_storage import VectorStorage
from ...services.ai_service import AIService
from pydantic import BaseModel

router = APIRouter()
document_storage = DocumentStorage()
vector_storage = VectorStorage()
ai_service = AIService()

class ValidationRequest(BaseModel):
    document_id: str
    clause_ids: List[int]

class ValidationResponse(BaseModel):
    document_id: str
    validated_clauses: List[dict]
    status: DocumentStatus

@router.post("/validate", response_model=ValidationResponse)
async def validate_analysis(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate specific clauses in a document's analysis"""
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.REDLINE_READY:
        raise HTTPException(status_code=400, detail="Document is not in a state to be validated")
    
    try:
        # Get clauses to validate
        clauses = db.query(AnalysisResult).filter(
            AnalysisResult.document_id == request.document_id,
            AnalysisResult.id.in_(request.clause_ids)
        ).all()
        
        if not clauses:
            raise HTTPException(status_code=404, detail="No clauses found for validation")
        
        # Validate clauses
        validated_clauses = []
        for clause in clauses:
            # Get similar clauses for context
            similar_clauses = vector_storage.find_similar_clauses(clause.clause_text)
            
            # Validate clause
            validation_result = await ai_service.validate_clause(
                clause_text=clause.clause_text,
                suggested_text=clause.suggested_text,
                similar_clauses=similar_clauses
            )
            
            # Update clause with validation score
            clause.validation_score = validation_result["validation_score"]
            validated_clauses.append({
                "id": clause.id,
                "clause_text": clause.clause_text,
                "suggested_text": clause.suggested_text,
                "validation_score": validation_result["validation_score"],
                "validation_notes": validation_result["validation_notes"]
            })
        
        db.commit()
        
        return {
            "document_id": request.document_id,
            "validated_clauses": validated_clauses,
            "status": document.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/validate-all")
async def validate_all_clauses(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Validate all clauses in a document's analysis"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.REDLINE_READY:
        raise HTTPException(status_code=400, detail="Document is not in a state to be validated")
    
    try:
        # Get all clauses
        clauses = db.query(AnalysisResult).filter(
            AnalysisResult.document_id == document_id
        ).all()
        
        if not clauses:
            raise HTTPException(status_code=404, detail="No clauses found for validation")
        
        # Validate all clauses
        for clause in clauses:
            # Get similar clauses for context
            similar_clauses = vector_storage.find_similar_clauses(clause.clause_text)
            
            # Validate clause
            validation_result = await ai_service.validate_clause(
                clause_text=clause.clause_text,
                suggested_text=clause.suggested_text,
                similar_clauses=similar_clauses
            )
            
            # Update clause with validation score
            clause.validation_score = validation_result["validation_score"]
        
        db.commit()
        
        return {
            "status": "success",
            "document_id": document_id,
            "validated_clauses_count": len(clauses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 