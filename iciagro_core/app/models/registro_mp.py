from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class RegistroMP:
    fecha_recepcion: date
    codigo_proveedor: str
    nombre_proveedor: str = ""
    materia_prima: str = ""
    cantidad_sacos: int = 0
    lote_proveedor: str = ""
    observaciones: str = ""
    responsable: str = ""
    vida_util: str = ""
    almacenamiento: str = ""
    codigo_mp: str = ""
    secuencia_dia: int = 0
    codigo_trazabilidad: str = ""
    revision_lote: str = ""
    producto_presentacion: str = ""

    def to_row(self) -> list:
        return [
            self.fecha_recepcion,
            self.codigo_proveedor,
            self.nombre_proveedor,
            self.materia_prima,
            self.cantidad_sacos,
            self.lote_proveedor,
            self.observaciones,
            self.responsable,
            self.vida_util,
            self.almacenamiento,
            self.codigo_mp,
            self.secuencia_dia,
            self.codigo_trazabilidad,
            self.revision_lote,
            self.producto_presentacion,
        ]

    @staticmethod
    def headers() -> list[str]:
        return [
            "Fecha recepción",
            "Código proveedor",
            "Nombre del proveedor",
            "Materia prima",
            "Cantidad de sacos",
            "Lote proveedor",
            "Observaciones",
            "Responsable recepción",
            "Vida útil",
            "Almacenamiento",
            "Código MP",
            "Secuencia día",
            "Código lote trazabilidad",
            "Revisión lote proveedor",
            "Producto / presentación",
        ]
