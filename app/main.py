from fastapi import FastAPI
from .db import Base, engine
from .routers import appointments, doctors, patients

app = FastAPI(title="Consultas Médicas API (Grupo #4)", version="0.1.0")

# Crear tablas
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "consultas-medicas", "version": "0.1.0"}