from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..events import bus
from .. import rules

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=schemas.AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(data: schemas.AppointmentIn, db: Session = Depends(get_db)):
    # Validación de traslapes (mismo doctor)
    start = data.start_at
    end = start + timedelta(minutes=data.duration_min)
    existing = db.execute(
        select(models.Appointment).where(models.Appointment.doctor_id == data.doctor_id)
    ).scalars().all()

    for ap in existing:
        ap_start = ap.start_at
        ap_end = ap.start_at + timedelta(minutes=ap.duration_min)
        if ap_start < end and start < ap_end:
            raise HTTPException(
                status_code=409,
                detail=f"El doctor {data.doctor_id} ya tiene una cita en ese horario."
            )

    # Validación declarativa por reglas
    payload = data.model_dump()
    try:
        rules.evaluate("appointment.validate", payload, db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    appt = models.Appointment(**payload)
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # Evento de dominio
    bus.publish("appointment.created", {"id": appt.id, **payload}, db)
    return appt

@router.get("", response_model=list[schemas.AppointmentOut])
def list_appointments(
    doctor_id: Optional[int] = Query(default=None),
    patient_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    stmt = select(models.Appointment)
    if doctor_id is not None:
        stmt = stmt.where(models.Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        stmt = stmt.where(models.Appointment.patient_id == patient_id)

    rows = db.execute(stmt).scalars().all()
    return rows
