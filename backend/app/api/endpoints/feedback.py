from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...db.session import get_db
from ...db.models import Document, DocumentStatus, Feedback, AnalysisResult
from ...services.document_storage import DocumentStorage
from ...services.vector_storage import VectorStorage
from ...services.ai_service import AIService
from pydantic import BaseModel

router = APIRouter()
document_storage = DocumentStorage()
vector_storage = VectorStorage()
ai_service = AIService()

class FeedbackRequest(BaseModel):
    feedback_text: str

class FeedbackResponse(BaseModel):
    id: int
    document_id: str
    feedback_text: str

@router.post("/{document_id}", response_model=FeedbackResponse)
async def submit_feedback(
    document_id: str,
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback for a document's analysis"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.REDLINE_READY:
        raise HTTPException(status_code=400, detail="Document is not in a state to receive feedback")
    
    # Create feedback record
    feedback_record = Feedback(
        document_id=document_id,
        feedback_text=feedback.feedback_text
    )
    db.add(feedback_record)
    
    # Store feedback embedding
    vector_storage.store_feedback_embedding(
        document_id=document_id,
        feedback_id=str(feedback_record.id),
        text=feedback.feedback_text,
        metadata={"type": "feedback"}
    )
    
    # Update document status
    document.status = DocumentStatus.FEEDBACK_RECEIVED
    db.commit()
    db.refresh(feedback_record)
    
    return feedback_record

@router.post("/{document_id}/regenerate")
async def regenerate_analysis(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Regenerate document analysis based on feedback"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.FEEDBACK_RECEIVED:
        raise HTTPException(status_code=400, detail="Document is not in a state to regenerate analysis")
    
    try:
        # Get document content
        content = document_storage.get_document(document.original_path)
        
        # Get feedback history
        feedback_history = db.query(Feedback).filter(
            Feedback.document_id == document_id
        ).all()
        
        # Get similar feedback from other documents
        similar_feedback = []
        for feedback in feedback_history:
            similar = vector_storage.find_similar_feedback(feedback.feedback_text)
            similar_feedback.extend(similar)
        
        # Regenerate analysis with feedback
        analysis_results = await ai_service.regenerate_analysis(
            content=content,
            feedback_history=feedback_history,
            similar_feedback=similar_feedback
        )
        
        # Clear old analysis results
        db.query(AnalysisResult).filter(
            AnalysisResult.document_id == document_id
        ).delete()
        
        # Store new analysis results
        for result in analysis_results:
            analysis = AnalysisResult(
                document_id=document_id,
                clause_text=result["clause_text"],
                original_text=result["original_text"],
                suggested_text=result["suggested_text"],
                confidence_score=result["confidence_score"]
            )
            db.add(analysis)
        
        # Generate new redline document
        redline_content = await ai_service.create_redline_document(content, analysis_results)
        redline_path = document_storage.save_redline_document(redline_content, "user_1", document_id)
        
        # Update document
        document.redline_path = redline_path
        document.status = DocumentStatus.REDLINE_READY
        db.commit()
        
        return {
            "status": "success",
            "document_id": document_id,
            "redline_path": redline_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 