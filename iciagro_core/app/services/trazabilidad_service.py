from __future__ import annotations

from datetime import date
from typing import Optional

from utils.date_utils import dia_juliano, anno_dos_digitos


class TrazabilidadService:
    """
    Servicio de lógica de trazabilidad pura.
    Todas las funciones son sin estado y pueden usarse sin ExcelService.
    """

    @staticmethod
    def generar_codigo(
        fecha: date,
        codigo_proveedor: str,
        codigo_mp: str,
        secuencia: int,
        prefijo: str = "LDP",
    ) -> str:
        """
        Genera el código de trazabilidad.
        Formato: EMP-CMP-PV-YYJJJ-SEQ
        Ejemplo: LDP-PEC-01-26068-001
        """
        anno = anno_dos_digitos(fecha)
        juliano = str(dia_juliano(fecha)).zfill(3)
        sufijo_prov = codigo_proveedor[-2:] if len(codigo_proveedor) >= 2 else "01"
        seq = str(secuencia).zfill(3)
        return f"{prefijo}-{codigo_mp}-{sufijo_prov}-{anno}{juliano}-{seq}"

    @staticmethod
    def validar_codigo(codigo: str) -> bool:
        """Valida que el código tenga el formato correcto EMP-CMP-PV-YYJJJ-SEQ."""
        partes = codigo.split("-")
        if len(partes) != 5:
            return False
        emp, cmp, pv, yyjjj, seq = partes
        if len(emp) < 2 or len(cmp) < 2 or len(pv) != 2:
            return False
        if len(yyjjj) != 5 or not yyjjj.isdigit():
            return False
        if len(seq) != 3 or not seq.isdigit():
            return False
        return True

    @staticmethod
    def revisar_lote(
        registros: list[dict],
        codigo_proveedor: str,
        lote_proveedor: str,
    ) -> str:
        """
        Detecta duplicados de (codigo_proveedor, lote_proveedor).
        Retorna 'REVISAR' si hay más de una aparición, 'OK' si no.
        """
        if not lote_proveedor:
            return ""
        count = sum(
            1
            for r in registros
            if r.get("codigo_proveedor") == codigo_proveedor
            and r.get("lote_proveedor") == lote_proveedor
        )
        return "REVISAR" if count > 1 else "OK"

    @staticmethod
    def calcular_secuencia(
        registros: list[dict],
        fecha: date,
        codigo_mp: str,
    ) -> int:
        """
        Cuenta los registros del mismo día con el mismo código MP.
        La secuencia se reinicia cada día.
        """
        count = sum(
            1
            for r in registros
            if r.get("fecha_recepcion") == fecha
            and r.get("codigo_mp") == codigo_mp
        )
        return count + 1

    @staticmethod
    def desglosar_codigo(codigo: str) -> Optional[dict]:
        """Desglosa un código en sus partes para visualización."""
        partes = codigo.split("-")
        if len(partes) != 5:
            return None
        emp, cmp, pv, yyjjj, seq = partes
        return {
            "empresa": emp,
            "codigo_mp": cmp,
            "proveedor_sufijo": pv,
            "anno": yyjjj[:2],
            "dia_juliano": yyjjj[2:],
            "secuencia": seq,
        }
