from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.session import get_db
from ...services.training_service import TrainingService
from pydantic import BaseModel

router = APIRouter()
training_service = TrainingService()

class TrainingData(BaseModel):
    original: str
    redline: str
    clean: str

class TrainingRequest(BaseModel):
    training_data: List[TrainingData]

@router.post("/train")
async def train_models(
    request: TrainingRequest,
    db: Session = Depends(get_db)
):
    """Train models using provided training data"""
    try:
        # Convert training data to the format expected by the training service
        training_data = [
            {
                "original": item.original,
                "redline": item.redline,
                "clean": item.clean
            }
            for item in request.training_data
        ]
        
        # Train models
        result = await training_service.train_models(training_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-from-files")
async def train_from_files(
    original_files: Optional[List[UploadFile]] = File(None),
    redline_files: Optional[List[UploadFile]] = File(None),
    clean_files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Train models using uploaded training files
    
    You can provide either:
    1. Original and clean files (for training with final versions)
    2. Redline files (for training with tracked changes)
    """
    if not redline_files and (not original_files or not clean_files):
        raise HTTPException(
            status_code=400,
            detail="Either provide redline files OR both original and clean files"
        )
    
    if redline_files and (original_files or clean_files):
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both redline files and original/clean files"
        )
    
    if original_files and clean_files and len(original_files) != len(clean_files):
        raise HTTPException(
            status_code=400,
            detail="Number of original and clean files must match"
        )
    
    try:
        training_data = []
        
        if redline_files:
            # Process redline files
            for redline_file in redline_files:
                if not redline_file.filename.endswith('.docx'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {redline_file.filename} is not a DOCX file"
                    )
                content = await redline_file.read()
                training_data.append({"redline": content})
        else:
            # Process original and clean files
            for orig_file, clean_file in zip(original_files, clean_files):
                if not orig_file.filename.endswith('.docx') or not clean_file.filename.endswith('.docx'):
                    raise HTTPException(
                        status_code=400,
                        detail="All files must be DOCX files"
                    )
                orig_content = await orig_file.read()
                clean_content = await clean_file.read()
                training_data.append({
                    "original": orig_content,
                    "clean": clean_content
                })
        
        # Train models
        result = await training_service.train_models(training_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 