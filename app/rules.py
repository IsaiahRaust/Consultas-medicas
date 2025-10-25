from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from .models import Appointment

@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    when: str  # event type, e.g., "appointment.validate"
    check: Callable[[dict, Session], None]  # raises ValueError on violation

def _ensure_no_overlap(payload: dict, db: Session) -> None:
    doctor_id = payload["doctor_id"]
    start_at = payload["start_at"]
    duration = payload["duration_min"]
    end_at = start_at + timedelta(minutes=duration)

    # SQL declarativo: detecta solapes del mismo doctor
    q = select(func.count()).select_from(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.start_at < end_at,
            (Appointment.start_at + func.printf('%d minutes', Appointment.duration_min)) > start_at
        )
    )
    # Nota: Para SQLite puro podríamos usar cálculo en Python. En motores avanzados usaría DATETIME + INTERVAL.
    # Alternativa segura y portable: comparar rangos en Python tras consultar citas del rango.
    count = db.execute(q).scalar_one()
    if count and count > 0:
        raise ValueError("El médico ya tiene una cita que se solapa en ese horario.")

RULES: list[Rule] = [
    Rule(
        name="doctor_no_overlap",
        description="Un mismo doctor no puede tener dos citas solapadas",
        when="appointment.validate",
        check=_ensure_no_overlap,
    )
]

def evaluate(event_type: str, payload: dict, db: Session) -> None:
    for r in RULES:
        if r.when == event_type:
            r.check(payload, db)