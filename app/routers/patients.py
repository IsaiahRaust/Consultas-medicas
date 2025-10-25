from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=schemas.PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(data: schemas.PatientIn, db: Session = Depends(get_db)):
    p = models.Patient(name=data.name, email=data.email)
    db.add(p)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # Posible email duplicado u otro error
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(p)
    return p