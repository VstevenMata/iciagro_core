from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class DataEventBus(QObject):
    """Singleton bus: any page that saves data emits `datos_actualizados`
    so all other pages can refresh in real time."""

    datos_actualizados = Signal()

    _instance: DataEventBus | None = None

    @classmethod
    def instance(cls) -> DataEventBus:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
