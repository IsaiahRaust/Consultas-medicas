from __future__ import annotations
from typing import Callable, Any, DefaultDict
from collections import defaultdict
import json
from sqlalchemy.orm import Session
from .models import EventLog

Subscriber = Callable[[dict, Session], None]

class EventBus:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Subscriber) -> None:
        self._subs[event_type].append(handler)

    def publish(self, event_type: str, payload: dict, db: Session) -> None:
        from datetime import datetime

        # Convertimos los datetime a string antes de guardar
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        # Persistimos el evento (auditoría)
        db.add(EventLog(type=event_type, payload=json.dumps(payload, default=default_serializer)))
        db.commit()

        # Notificamos a suscriptores
        for h in list(self._subs.get(event_type, [])):
            h(payload, db)

bus = EventBus()

# Ejemplo de suscriptor: simula notificación y agrega lógica derivada
def on_appointment_created(payload: dict, db: Session) -> None:
    # Aquí podrías integrar correo/SMS. Dejamos una traza simple:
    print(f"[event] appointment.created -> notifying entities: {payload.get('id')}")

bus.subscribe("appointment.created", on_appointment_created)
