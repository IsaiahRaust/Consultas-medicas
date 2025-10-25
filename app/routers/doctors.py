from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("", response_model=schemas.DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor(data: schemas.DoctorIn, db: Session = Depends(get_db)):
    d = models.Doctor(name=data.name, specialty=data.specialty)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d