# Grupo #4 — API RESTful de Consultas Médicas (Declarativa + Eventos)

Proyecto del curso Paradigmas de Programación. Combina **programación declarativa** (reglas expresadas como datos y SQL declarativo) y **eventos** (bus de eventos asíncrono en memoria).

## Cómo correr
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints clave
- `POST /patients` — crear paciente
- `POST /doctors` — crear doctor
- `POST /appointments` — crear cita (dispara evento `appointment.created`)
- `GET /appointments` — filtrar por `doctor_id`, `patient_id` o rango de fechas

## Paradigmas
- **Declarativo:** 
  - Reglas de negocio expresadas como **datos** (`rules.py`) y evaluadas por un **motor** (sin `if/else` embebidos).
  - SQL **declarativo** (SQLAlchemy Core/ORM) para restricciones como *no solapar citas*.
- **Eventos:**
  - `EventBus` simple con suscriptores para `appointment.created` que registran auditoría y simulan notificaciones.

## Estructura
```
app/
  main.py
  db.py
  models.py
  schemas.py
  events.py
  rules.py
  routers/
    appointments.py
    doctors.py
    patients.py
requirements.txt
README.md
```

## Licencia
Uso académico.