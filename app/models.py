from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=True)

    appointments: Mapped[list['Appointment']] = relationship(back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)

    appointments: Mapped[list['Appointment']] = relationship(back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    reason: Mapped[str | None] = mapped_column(String(250), nullable=True)

    patient: Mapped['Patient'] = relationship(back_populates="appointments")
    doctor: Mapped['Doctor'] = relationship(back_populates="appointments")

    __table_args__ = (
        # Evita duplicados exactos (misma persona/médico/fecha)
        UniqueConstraint("patient_id", "doctor_id", "start_at", name="uq_appt_exact"),
    )

class EventLog(Base):
    __tablename__ = "event_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(120), index=True)
    payload: Mapped[str] = mapped_column(String)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)