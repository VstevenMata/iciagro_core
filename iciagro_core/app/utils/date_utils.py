from __future__ import annotations

from datetime import date, datetime
from typing import Union


def dia_juliano(fecha: Union[date, datetime]) -> int:
    """Día del año (1-366). Equivale a tm_yday."""
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    return fecha.timetuple().tm_yday


def anno_dos_digitos(fecha: Union[date, datetime]) -> str:
    """Año en 2 dígitos: 2026 → '26'."""
    if isinstance(fecha, datetime):
        return fecha.strftime("%y")
    return fecha.strftime("%y")


def formatear_fecha(fecha: Union[date, datetime, None]) -> str:
    """Formato dd/mm/yyyy para mostrar en UI."""
    if fecha is None:
        return ""
    if isinstance(fecha, datetime):
        return fecha.strftime("%d/%m/%Y")
    return fecha.strftime("%d/%m/%Y")


def parse_fecha(valor) -> date | None:
    """Convierte un valor leído de openpyxl (float, datetime, str) a date."""
    if valor is None:
        return None
    if isinstance(valor, (date, datetime)):
        return valor if isinstance(valor, date) else valor.date()
    if isinstance(valor, float):
        # Excel serial date
        from datetime import timedelta
        excel_base = date(1899, 12, 30)
        return excel_base + timedelta(days=int(valor))
    if isinstance(valor, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(valor, fmt).date()
            except ValueError:
                continue
    return None
