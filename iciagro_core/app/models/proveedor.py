from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Proveedor:
    codigo_proveedor: str
    nombre: str
    ubicacion: str = ""
    telefono: str = ""
    correo: str = ""
    producto_abastece: str = ""
    tipo_aditivo: str = ""
    presentacion: str = ""
    uso_producto: str = ""
    condiciones_almacenamiento: str = ""
    vida_util: str = ""
    codigo_mp: str = ""
    producto_presentacion: str = ""

    @staticmethod
    def headers() -> list[str]:
        return [
            "Código Proveedor",
            "Nombre del Proveedor",
            "Ubicación",
            "Teléfono",
            "Correo electrónico",
            "Producto que abastece",
            "Tipo de aditivo",
            "Presentación",
            "Uso en el producto",
            "Condiciones de almacenamiento",
            "Vida útil",
            "Código MP",
            "Producto / presentación",
        ]

    def to_row(self) -> list:
        return [
            self.codigo_proveedor,
            self.nombre,
            self.ubicacion,
            self.telefono,
            self.correo,
            self.producto_abastece,
            self.tipo_aditivo,
            self.presentacion,
            self.uso_producto,
            self.condiciones_almacenamiento,
            self.vida_util,
            self.codigo_mp,
            self.producto_presentacion,
        ]
