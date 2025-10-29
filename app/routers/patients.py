from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import re

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=schemas.PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(data: schemas.PatientIn, db: Session = Depends(get_db)):
    # Normaliza: quita espacios dobles y bordes
    name = re.sub(r"\s+", " ", data.name or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="El nombre no puede estar vacío o solo contener espacios.")

    p = models.Patient(name=name, email=data.email)
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El correo ya existe.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear paciente: {e}")
    db.refresh(p)
    return p
