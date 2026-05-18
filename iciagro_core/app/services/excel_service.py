from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import openpyxl
import pandas as pd

from models.proveedor import Proveedor
from models.registro_mp import RegistroMP
from utils.date_utils import dia_juliano, anno_dos_digitos, parse_fecha


class ExcelService:
    """
    Servicio principal para lectura/escritura del archivo .xlsm de trazabilidad.
    Replica todas las fórmulas Excel en Python puro.
    """

    REGISTRO_HEADER_ROW = 5
    REGISTRO_DATA_START = 6
    CATALOGO_HEADER_ROW = 2
    CATALOGO_DATA_START = 3

    def __init__(self, ruta: str) -> None:
        self.ruta = ruta
        self._wb = openpyxl.load_workbook(ruta, keep_vba=True, data_only=True)
        self.config = self._cargar_config()
        self.catalogo_df = self._cargar_catalogo_df()
        self.responsables = self._cargar_responsables()
        self._registros_df: Optional[pd.DataFrame] = None

    # ─────────────────────── CARGA INTERNA ───────────────────────

    def _cargar_config(self) -> dict:
        ws = self._wb["Control"]
        config = {
            "prefijo": "LDP",
            "empresa": "Lácteos del Páramo",
            "estados": ["Recibido", "Cuarentena", "Liberado", "Rechazado"],
            "codigos_mp": {},
        }
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:
                continue
            key = str(row[0]).strip()
            val = row[1]
            if key == "Prefijo empresa":
                config["prefijo"] = str(val).strip() if val else "LDP"
            elif key == "Empresa":
                config["empresa"] = str(val).strip() if val else ""
            elif key in ("Recibido", "Cuarentena", "Liberado", "Rechazado"):
                if val and val not in config["estados"]:
                    config["estados"].append(str(val).strip())
            elif key.startswith("Código") and val:
                config["codigos_mp"][key] = str(val).strip()
        return config

    def _cargar_catalogo_df(self) -> pd.DataFrame:
        ws = self._wb["Catalogo_Proveedores"]
        headers = None
        filas = []
        for i, row in enumerate(
            ws.iter_rows(min_row=self.CATALOGO_HEADER_ROW, values_only=True)
        ):
            if i == 0:
                headers = [str(h) if h else f"Col{i}" for i, h in enumerate(row)]
            elif any(v is not None for v in row):
                filas.append(list(row))
        if not headers:
            return pd.DataFrame()
        return pd.DataFrame(filas, columns=headers)

    def _cargar_responsables(self) -> list[str]:
        ws = self._wb["Hoja1"]
        responsables: list[str] = []
        for row in ws.iter_rows(values_only=True):
            val = row[0] if row else None
            if (
                val
                and isinstance(val, str)
                and not val.lower().startswith("código")
                and not val.strip().isdigit()
                and len(val.strip()) > 2
            ):
                nombre = val.strip()
                if nombre not in responsables:
                    responsables.append(nombre)
        if not responsables:
            responsables = ["Anthony Mata", "Camila Gomez"]
        return responsables

    # ─────────────────────── CATÁLOGO ───────────────────────────

    def get_codigos_proveedor(self) -> list[str]:
        col = "Código Proveedor"
        if col in self.catalogo_df.columns:
            return [str(v) for v in self.catalogo_df[col].dropna().tolist()]
        return []

    def get_proveedores(self) -> list[Proveedor]:
        proveedores = []
        for _, row in self.catalogo_df.iterrows():
            proveedores.append(
                Proveedor(
                    codigo_proveedor=str(row.get("Código Proveedor", "") or ""),
                    nombre=str(row.get("Nombre del Proveedor", "") or ""),
                    ubicacion=str(row.get("Ubicación", "") or ""),
                    telefono=str(row.get("Teléfono", "") or ""),
                    correo=str(row.get("Correo electrónico", "") or ""),
                    producto_abastece=str(row.get("Producto que abastece", "") or ""),
                    tipo_aditivo=str(row.get("Tipo de aditivo", "") or ""),
                    presentacion=str(row.get("Presentación", "") or ""),
                    uso_producto=str(row.get("Uso en el producto", "") or ""),
                    condiciones_almacenamiento=str(
                        row.get("Condiciones de almacenamiento", "") or ""
                    ),
                    vida_util=str(row.get("Vida útil", "") or ""),
                    codigo_mp=str(row.get("Código MP", "") or ""),
                    producto_presentacion=str(
                        row.get("Producto / presentación", "") or ""
                    ),
                )
            )
        return proveedores

    # ─────────────────── AUTOCOMPLETADO (VLOOKUP) ───────────────

    def autocompletar_proveedor(self, codigo_proveedor: str) -> dict:
        """Replica los VLOOKUP de columnas C, D, I, J, K, O."""
        cat = self.catalogo_df
        if cat.empty or "Código Proveedor" not in cat.columns:
            return {}
        match = cat[cat["Código Proveedor"].astype(str) == codigo_proveedor]
        if match.empty:
            return {}
        row = match.iloc[0]
        return {
            "nombre_proveedor": str(row.get("Nombre del Proveedor", "") or ""),
            "materia_prima": str(row.get("Producto que abastece", "") or ""),
            "vida_util": str(row.get("Vida útil", "") or ""),
            "almacenamiento": str(row.get("Condiciones de almacenamiento", "") or ""),
            "codigo_mp": str(row.get("Código MP", "") or ""),
            "producto_presentacion": str(
                row.get("Producto / presentación", "") or ""
            ),
        }

    # ──────────────────── REGISTROS ─────────────────────────────

    def cargar_registros(self) -> pd.DataFrame:
        ws = self._wb["Registro_MP"]
        headers_row = list(ws.iter_rows(
            min_row=self.REGISTRO_HEADER_ROW,
            max_row=self.REGISTRO_HEADER_ROW,
            values_only=True,
        ))[0]
        headers = [str(h) if h else f"Col{i}" for i, h in enumerate(headers_row)]
        filas = []
        for row in ws.iter_rows(
            min_row=self.REGISTRO_DATA_START,
            max_row=ws.max_row,
            values_only=True,
        ):
            if any(v is not None for v in row):
                filas.append(list(row))
        df = pd.DataFrame(filas, columns=headers)
        self._registros_df = df
        return df

    def get_registros_df(self) -> pd.DataFrame:
        if self._registros_df is None:
            return self.cargar_registros()
        return self._registros_df

    def get_registros(self) -> list[RegistroMP]:
        df = self.get_registros_df()
        registros = []
        for _, row in df.iterrows():
            fecha = parse_fecha(row.iloc[0] if len(row) > 0 else None)
            if fecha is None:
                continue
            registros.append(
                RegistroMP(
                    fecha_recepcion=fecha,
                    codigo_proveedor=str(row.iloc[1] or "") if len(row) > 1 else "",
                    nombre_proveedor=str(row.iloc[2] or "") if len(row) > 2 else "",
                    materia_prima=str(row.iloc[3] or "") if len(row) > 3 else "",
                    cantidad_sacos=int(row.iloc[4] or 0) if len(row) > 4 else 0,
                    lote_proveedor=str(row.iloc[5] or "") if len(row) > 5 else "",
                    observaciones=str(row.iloc[6] or "") if len(row) > 6 else "",
                    responsable=str(row.iloc[7] or "") if len(row) > 7 else "",
                    vida_util=str(row.iloc[8] or "") if len(row) > 8 else "",
                    almacenamiento=str(row.iloc[9] or "") if len(row) > 9 else "",
                    codigo_mp=str(row.iloc[10] or "") if len(row) > 10 else "",
                    secuencia_dia=int(row.iloc[11] or 0) if len(row) > 11 else 0,
                    codigo_trazabilidad=str(row.iloc[12] or "") if len(row) > 12 else "",
                    revision_lote=str(row.iloc[13] or "") if len(row) > 13 else "",
                    producto_presentacion=str(row.iloc[14] or "") if len(row) > 14 else "",
                )
            )
        return registros

    # ──────────────────── CÁLCULOS (fórmulas Excel) ─────────────

    def calcular_secuencia(self, fecha: date, codigo_mp: str) -> int:
        """Replica COUNTIFS(Fecha, fecha, CódigoMP, codigo_mp) + 1."""
        df = self.get_registros_df()
        if df.empty:
            return 1
        try:
            fechas = df.iloc[:, 0].apply(parse_fecha)
            cods = df.iloc[:, 10].astype(str)
            subset = df[
                (fechas == fecha) & (cods == codigo_mp)
            ]
            return len(subset) + 1
        except Exception:
            return 1

    def revisar_lote(self, codigo_proveedor: str, lote: str) -> str:
        """Replica COUNTIFS para detección de duplicados (columna N)."""
        if not lote:
            return ""
        df = self.get_registros_df()
        if df.empty:
            return "OK"
        try:
            cods = df.iloc[:, 1].astype(str)
            lotes = df.iloc[:, 5].astype(str)
            dups = df[(cods == codigo_proveedor) & (lotes == lote)]
            return "REVISAR" if len(dups) > 1 else "OK"
        except Exception:
            return "OK"

    def generar_codigo_trazabilidad(
        self,
        fecha: date,
        codigo_proveedor: str,
        codigo_mp: str,
        secuencia: int,
    ) -> str:
        """Replica la fórmula de columna M: EMP-CMP-PV-YYJJJ-SEQ."""
        prefijo = self.config.get("prefijo", "LDP")
        anno = anno_dos_digitos(fecha)
        juliano = str(dia_juliano(fecha)).zfill(3)
        sufijo_prov = codigo_proveedor[-2:] if len(codigo_proveedor) >= 2 else "01"
        seq = str(secuencia).zfill(3)
        return f"{prefijo}-{codigo_mp}-{sufijo_prov}-{anno}{juliano}-{seq}"

    # ──────────────────── GUARDAR REGISTRO ──────────────────────

    def guardar_registro(self, registro: RegistroMP) -> None:
        """Escribe un nuevo registro en Registro_MP y guarda el archivo."""
        wb_write = openpyxl.load_workbook(self.ruta, keep_vba=True)
        ws = wb_write["Registro_MP"]

        next_row = self._proxima_fila_vacia(ws)
        valores = registro.to_row()
        for col_idx, valor in enumerate(valores, start=1):
            ws.cell(row=next_row, column=col_idx, value=valor)

        wb_write.save(self.ruta)

        # Invalidar caché
        self._wb = openpyxl.load_workbook(self.ruta, keep_vba=True, data_only=True)
        self._registros_df = None

    def _proxima_fila_vacia(self, ws) -> int:
        for row in range(ws.max_row, self.REGISTRO_DATA_START - 1, -1):
            if any(ws.cell(row=row, column=c).value for c in range(1, 4)):
                return row + 1
        return self.REGISTRO_DATA_START

    # ──────────────────── EXPORTAR ──────────────────────────────

    def exportar_excel(self, df: pd.DataFrame, ruta_destino: str) -> None:
        with pd.ExcelWriter(ruta_destino, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Registro_MP", index=False)

    def actualizar_catalogo(self, ruta_catalogo: str) -> None:
        """Carga un archivo externo de catálogo y actualiza Catalogo_Proveedores."""
        wb_cat = openpyxl.load_workbook(ruta_catalogo)
        ws_src = wb_cat.active

        wb_dest = openpyxl.load_workbook(self.ruta, keep_vba=True)
        ws_dest = wb_dest["Catalogo_Proveedores"]

        # Limpiar filas de datos anteriores
        for row in ws_dest.iter_rows(
            min_row=self.CATALOGO_DATA_START, max_row=ws_dest.max_row
        ):
            for cell in row:
                cell.value = None

        # Copiar nuevos datos
        for r_idx, row in enumerate(
            ws_src.iter_rows(values_only=True), start=self.CATALOGO_DATA_START
        ):
            for c_idx, val in enumerate(row, start=1):
                ws_dest.cell(row=r_idx, column=c_idx, value=val)

        wb_dest.save(self.ruta)

        # Recargar catálogo en memoria
        self._wb = openpyxl.load_workbook(self.ruta, keep_vba=True, data_only=True)
        self.catalogo_df = self._cargar_catalogo_df()
        self.responsables = self._cargar_responsables()
