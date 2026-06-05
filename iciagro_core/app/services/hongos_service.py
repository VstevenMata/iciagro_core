from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

import openpyxl
import pandas as pd

from utils.date_utils import dia_juliano, anno_dos_digitos, parse_fecha


class HongosService:
    """
    Servicio principal para el sistema de trazabilidad Hongos del Páramo.
    Lee y escribe sobre el archivo Excel con las hojas del sistema.
    """

    HEADER_ROW = 4
    DATA_START = 5

    PRODUCTOS = [
        {"nombre": "Hongo Ostra Blanco", "codigo": "HOB", "presentacion": "250 g"},
        {"nombre": "Hongo Ostra Gris",   "codigo": "HOG", "presentacion": "250 g"},
        {"nombre": "Hongo Ostra Rosado", "codigo": "HOR", "presentacion": "250 g"},
    ]
    MATERIAS_PRIMAS_PROV001 = ["Bolsas de cultivo", "Empaque 250 g"]
    ESTADOS = ["Aceptado", "Rechazado"]
    ESTADOS_CASO = ["Abierto", "Cerrado"]
    RESPONSABLES = ["Doña María", "Don Olman", "Hijas de la familia"]
    TIPOS_CLIENTE = ["Restaurante", "Feria", "Cliente directo"]
    EMPRESA = "Hongos del Páramo"
    UBICACION_EMPRESA = "Pérez Zeledón, Costa Rica"
    CONSERVACION = "Mantener en refrigeración"

    def __init__(self, ruta: str) -> None:
        self.ruta = ruta
        self._reload_data()

    # ─────────────────────────── CARGA ──────────────────────────────

    def _reload_data(self) -> None:
        self._wb = openpyxl.load_workbook(self.ruta, data_only=True)
        self._proveedores_df    = self._load_sheet("Proveedores")
        self._evaluaciones_df   = self._load_sheet("Evaluacion_Proveedores")
        self._clientes_df       = self._load_sheet("Clientes")
        self._recepciones_df    = self._load_sheet("Recepcion_MP")
        self._producciones_df   = self._load_sheet("Produccion_Interna")
        self._terminados_df     = self._load_sheet("Producto_Terminado")
        self._expediciones_df   = self._load_sheet("Expedicion_Ventas")
        self._retiros_df        = self._load_sheet("Retiro_Producto")

    def _load_sheet(self, sheet_name: str) -> pd.DataFrame:
        if sheet_name not in self._wb.sheetnames:
            return pd.DataFrame()
        ws = self._wb[sheet_name]
        header_cells = list(ws.iter_rows(
            min_row=self.HEADER_ROW,
            max_row=self.HEADER_ROW,
            values_only=True,
        ))[0]
        headers = [
            str(h).strip() if h else f"Col{i}"
            for i, h in enumerate(header_cells)
        ]
        filas = []
        for row in ws.iter_rows(
            min_row=self.DATA_START,
            max_row=ws.max_row,
            values_only=True,
        ):
            if any(v is not None for v in row):
                filas.append(list(row))
        if not filas:
            return pd.DataFrame(columns=headers)
        df = pd.DataFrame(filas, columns=headers)
        # Eliminar columnas donde el header es auto-generado y todos los valores son NaN
        cols_validas = [
            col for i, col in enumerate(df.columns)
            if not (col == f"Col{i}" and df[col].isna().all())
        ]
        return df[cols_validas]

    def get_nombre_archivo(self) -> str:
        return Path(self.ruta).name

    # ─────────────────────── PROVEEDORES ────────────────────────────

    def get_proveedores_df(self) -> pd.DataFrame:
        return self._proveedores_df

    def get_codigos_proveedor(self) -> list[str]:
        df = self._proveedores_df
        col = "Código proveedor"
        if df.empty or col not in df.columns:
            return []
        return [str(v) for v in df[col].dropna().tolist()]

    def get_proveedor(self, codigo: str) -> Optional[dict]:
        df = self._proveedores_df
        col = "Código proveedor"
        if df.empty or col not in df.columns:
            return None
        match = df[df[col].astype(str) == codigo]
        return match.iloc[0].to_dict() if not match.empty else None

    @staticmethod
    def _val(v) -> str:
        """Convierte valor de celda (incluyendo NaN de pandas) a str limpio."""
        import math
        if v is None:
            return ""
        try:
            if math.isnan(float(v)):
                return ""
        except (TypeError, ValueError):
            pass
        return str(v).strip()

    def autocompletar_proveedor(self, codigo: str) -> dict:
        prov = self.get_proveedor(codigo)
        if not prov:
            return {}
        return {
            "nombre":           self._val(prov.get("Proveedor")),
            "producto":         self._val(prov.get("Producto que abastece")),
            "contacto":         self._val(prov.get("Contacto")),
            "ubicacion":        self._val(prov.get("Ubicación")),
            "frecuencia":       self._val(prov.get("Frecuencia")),
            "observaciones":    self._val(prov.get("Observaciones")),
        }

    def actualizar_proveedor(self, codigo: str, campo: str, valor: str) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Proveedores"]
        hmap = self._header_map(ws)
        col_codigo = hmap.get("Código proveedor")
        col_campo  = hmap.get(campo)
        if not col_codigo or not col_campo:
            wb.close()
            return
        for row in range(self.DATA_START, ws.max_row + 1):
            if str(ws.cell(row=row, column=col_codigo).value or "").strip() == codigo:
                ws.cell(row=row, column=col_campo, value=valor)
                break
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    # ────────────────── EVALUACIÓN PROVEEDORES ──────────────────────

    def get_evaluaciones_df(self) -> pd.DataFrame:
        return self._evaluaciones_df

    @staticmethod
    def clasificar(total: float) -> str:
        if total >= 90:
            return "Excelente"
        elif total >= 75:
            return "Aceptable"
        elif total >= 60:
            return "Condicionado"
        return "No recomendado"

    def guardar_evaluacion(self, datos: dict) -> None:
        total = sum([
            datos.get("entrega_tiempo", 0),
            datos.get("calidad", 0),
            datos.get("cantidad_correcta", 0),
            datos.get("condicion_entrega", 0),
            datos.get("comunicacion", 0),
            datos.get("identificacion_lote", 0),
        ])
        clasificacion = self.clasificar(total)
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Evaluacion_Proveedores"]
        r = self._next_empty_row(ws)
        ws.cell(r, 1, datos.get("fecha"))
        ws.cell(r, 2, datos.get("codigo_proveedor"))
        ws.cell(r, 3, datos.get("proveedor"))
        ws.cell(r, 4, datos.get("producto_abastecido"))
        ws.cell(r, 5, datos.get("entrega_tiempo", 0))
        ws.cell(r, 6, datos.get("calidad", 0))
        ws.cell(r, 7, datos.get("cantidad_correcta", 0))
        ws.cell(r, 8, datos.get("condicion_entrega", 0))
        ws.cell(r, 9, datos.get("comunicacion", 0))
        ws.cell(r, 10, datos.get("identificacion_lote", 0))
        ws.cell(r, 11, total)
        ws.cell(r, 12, clasificacion)
        ws.cell(r, 13, datos.get("observaciones", ""))
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    # ─────────────────────── CLIENTES ───────────────────────────────

    def get_clientes_df(self) -> pd.DataFrame:
        return self._clientes_df

    def get_codigos_cliente(self) -> list[str]:
        df = self._clientes_df
        col = "Código cliente"
        if df.empty or col not in df.columns:
            return []
        return [str(v) for v in df[col].dropna().tolist()]

    def get_cliente(self, codigo: str) -> Optional[dict]:
        df = self._clientes_df
        col = "Código cliente"
        if df.empty or col not in df.columns:
            return None
        match = df[df[col].astype(str) == codigo]
        return match.iloc[0].to_dict() if not match.empty else None

    def autocompletar_cliente(self, codigo: str) -> dict:
        cl = self.get_cliente(codigo)
        if not cl:
            return {}
        return {
            "nombre":         self._val(cl.get("Nombre cliente")),
            "tipo":           self._val(cl.get("Tipo de cliente")),
            "contacto":       self._val(cl.get("Contacto")),
            "frecuencia":     self._val(cl.get("Frecuencia")),
            "punto_entrega":  self._val(cl.get("Punto de entrega")),
            "observaciones":  self._val(cl.get("Observaciones")),
        }

    def actualizar_cliente(self, codigo: str, campo: str, valor: str) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Clientes"]
        hmap = self._header_map(ws)
        col_codigo = hmap.get("Código cliente")
        col_campo  = hmap.get(campo)
        if not col_codigo or not col_campo:
            wb.close()
            return
        for row in range(self.DATA_START, ws.max_row + 1):
            if str(ws.cell(row=row, column=col_codigo).value or "").strip() == codigo:
                ws.cell(row=row, column=col_campo, value=valor)
                break
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    # ─────────────────────── RECEPCIÓN MP ───────────────────────────

    def get_recepciones_df(self) -> pd.DataFrame:
        return self._recepciones_df

    def generar_codigo_recepcion(self, fecha: date) -> str:
        anno    = anno_dos_digitos(fecha)
        juliano = str(dia_juliano(fecha)).zfill(3)
        prefix  = f"REC-{anno}{juliano}-"
        df = self._recepciones_df
        if df.empty or "Código recepción" not in df.columns:
            return f"{prefix}001"
        n = sum(1 for c in df["Código recepción"].dropna().astype(str) if c.startswith(prefix))
        return f"{prefix}{str(n + 1).zfill(3)}"

    def guardar_recepcion(self, datos: dict) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Recepcion_MP"]
        r = self._next_empty_row(ws)
        fecha = datos.get("fecha")
        ws.cell(r, 1, fecha)
        ws.cell(r, 2, str(dia_juliano(fecha)).zfill(3) if fecha else "")
        ws.cell(r, 3, datos.get("codigo_recepcion", ""))
        ws.cell(r, 4, datos.get("proveedor", ""))
        ws.cell(r, 5, datos.get("materia_prima", ""))
        ws.cell(r, 6, datos.get("cantidad"))
        ws.cell(r, 7, datos.get("unidad", ""))
        ws.cell(r, 8, datos.get("estado", ""))
        ws.cell(r, 9, datos.get("responsable", ""))
        ws.cell(r, 10, datos.get("observaciones", ""))
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    # ─────────────────── PRODUCCIÓN INTERNA ─────────────────────────

    def get_producciones_df(self) -> pd.DataFrame:
        return self._producciones_df

    def get_consecutivo_producto(self, codigo_producto: str) -> int:
        df = self._producciones_df
        if df.empty or "Lote interno automático" not in df.columns:
            return 1
        patron = f"-{codigo_producto}-"
        count = sum(1 for c in df["Lote interno automático"].dropna().astype(str) if patron in c)
        return count + 1

    def generar_lote_interno(self, fecha: date, codigo_producto: str) -> str:
        anno    = anno_dos_digitos(fecha)
        juliano = str(dia_juliano(fecha)).zfill(3)
        consec  = self.get_consecutivo_producto(codigo_producto)
        return f"HP-{anno}{juliano}-{codigo_producto}-{str(consec).zfill(2)}"

    def guardar_produccion(self, datos: dict) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Produccion_Interna"]
        r = self._next_empty_row(ws)
        fecha = datos.get("fecha")
        consec = self.get_consecutivo_producto(datos.get("codigo_producto", ""))
        ws.cell(r, 1, fecha)
        ws.cell(r, 2, str(dia_juliano(fecha)).zfill(3) if fecha else "")
        ws.cell(r, 3, datos.get("codigo_producto", ""))
        ws.cell(r, 4, consec)
        ws.cell(r, 5, datos.get("lote_interno", ""))
        ws.cell(r, 6, datos.get("kg_sustrato"))
        ws.cell(r, 7, datos.get("g_micelio"))
        ws.cell(r, 8, datos.get("responsable", ""))
        ws.cell(r, 9, datos.get("temp_pasteurizacion"))
        ws.cell(r, 10, datos.get("tiempo_pasteurizacion"))
        ws.cell(r, 11, datos.get("tiempo_secado", ""))
        ws.cell(r, 12, datos.get("observaciones", ""))
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    def get_lotes_internos(self) -> list[str]:
        df = self._producciones_df
        if df.empty or "Lote interno automático" not in df.columns:
            return []
        return [str(v) for v in df["Lote interno automático"].dropna().tolist()]

    def get_produccion_by_lote(self, lote: str) -> Optional[dict]:
        df = self._producciones_df
        col = "Lote interno automático"
        if df.empty or col not in df.columns:
            return None
        match = df[df[col].astype(str) == lote]
        return match.iloc[0].to_dict() if not match.empty else None

    def get_nombre_producto(self, codigo: str) -> str:
        for p in self.PRODUCTOS:
            if p["codigo"] == codigo:
                return p["nombre"]
        return codigo

    # ─────────────────── PRODUCTO TERMINADO ─────────────────────────

    def get_terminados_df(self) -> pd.DataFrame:
        return self._terminados_df

    def get_lotes_usados_terminado(self) -> list[str]:
        df = self._terminados_df
        if df.empty or "Lote interno" not in df.columns:
            return []
        return [str(v) for v in df["Lote interno"].dropna().tolist()]

    def get_lotes_disponibles_para_terminado(self) -> list[str]:
        todos  = set(self.get_lotes_internos())
        usados = set(self.get_lotes_usados_terminado())
        return sorted(todos - usados)

    def guardar_terminado(self, datos: dict) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Producto_Terminado"]
        r = self._next_empty_row(ws)
        ws.cell(r, 1,  datos.get("fecha_cosecha"))
        ws.cell(r, 2,  datos.get("fecha_empaque"))
        ws.cell(r, 3,  datos.get("lote_interno", ""))
        ws.cell(r, 4,  datos.get("codigo_producto", ""))
        ws.cell(r, 5,  datos.get("producto", ""))
        ws.cell(r, 6,  datos.get("presentacion", ""))
        ws.cell(r, 7,  datos.get("cantidad_empacada"))
        ws.cell(r, 8,  datos.get("unidad", ""))
        ws.cell(r, 9,  datos.get("responsable", ""))
        ws.cell(r, 10, datos.get("temp_refrigeracion"))
        ws.cell(r, 11, datos.get("estado", ""))
        ws.cell(r, 12, datos.get("observaciones", ""))
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    def get_lotes_aceptados_terminado(self) -> list[str]:
        df = self._terminados_df
        if df.empty:
            return []
        col_lote   = "Lote interno"
        col_estado = "Estado"
        if col_lote not in df.columns or col_estado not in df.columns:
            return []
        return [
            str(v) for v in df.loc[
                df[col_estado].astype(str) == "Aceptado", col_lote
            ].dropna().tolist()
        ]

    def get_terminado_by_lote(self, lote: str) -> Optional[dict]:
        df = self._terminados_df
        col = "Lote interno"
        if df.empty or col not in df.columns:
            return None
        match = df[df[col].astype(str) == lote]
        return match.iloc[0].to_dict() if not match.empty else None

    # ─────────────────── EXPEDICIÓN Y VENTAS ────────────────────────

    def get_expediciones_df(self) -> pd.DataFrame:
        return self._expediciones_df

    def generar_codigo_expedicion(self, fecha: date) -> str:
        anno    = anno_dos_digitos(fecha)
        juliano = str(dia_juliano(fecha)).zfill(3)
        prefix  = f"EXP-{anno}{juliano}-"
        df = self._expediciones_df
        if df.empty or "Código expedición" not in df.columns:
            return f"{prefix}001"
        n = sum(1 for c in df["Código expedición"].dropna().astype(str) if c.startswith(prefix))
        return f"{prefix}{str(n + 1).zfill(3)}"

    def guardar_expedicion(self, datos: dict) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Expedicion_Ventas"]
        r = self._next_empty_row(ws)
        ws.cell(r, 1,  datos.get("fecha_salida"))
        ws.cell(r, 2,  datos.get("codigo_expedicion", ""))
        ws.cell(r, 3,  datos.get("cliente", ""))
        ws.cell(r, 4,  datos.get("tipo_cliente", ""))
        ws.cell(r, 5,  datos.get("producto", ""))
        ws.cell(r, 6,  datos.get("lote_vendido", ""))
        ws.cell(r, 7,  datos.get("cantidad"))
        ws.cell(r, 8,  datos.get("unidad", ""))
        ws.cell(r, 9,  datos.get("destino", ""))
        ws.cell(r, 10, datos.get("responsable", ""))
        ws.cell(r, 11, datos.get("condicion_entrega", ""))
        ws.cell(r, 12, datos.get("observaciones", ""))
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    def get_lotes_vendidos_aceptados(self) -> list[str]:
        df = self._expediciones_df
        if df.empty:
            return []
        col_lote = "Lote vendido"
        col_cond = "Condición entrega"
        if col_lote not in df.columns or col_cond not in df.columns:
            return []
        return [
            str(v) for v in df.loc[
                df[col_cond].astype(str) == "Aceptado", col_lote
            ].dropna().tolist()
        ]

    def get_expedicion_by_lote(self, lote: str) -> Optional[dict]:
        df = self._expediciones_df
        col = "Lote vendido"
        if df.empty or col not in df.columns:
            return None
        match = df[df[col].astype(str) == lote]
        return match.iloc[0].to_dict() if not match.empty else None

    # ─────────────────── RETIRO DE PRODUCTO ─────────────────────────

    def get_retiros_df(self) -> pd.DataFrame:
        return self._retiros_df

    def generar_codigo_retiro(self, fecha: date) -> str:
        anno    = anno_dos_digitos(fecha)
        juliano = str(dia_juliano(fecha)).zfill(3)
        prefix  = f"RET-{anno}{juliano}-"
        df = self._retiros_df
        if df.empty or "Código retiro" not in df.columns:
            return f"{prefix}001"
        n = sum(1 for c in df["Código retiro"].dropna().astype(str) if c.startswith(prefix))
        return f"{prefix}{str(n + 1).zfill(3)}"

    def get_lotes_usados_retiro(self) -> list[str]:
        df = self._retiros_df
        if df.empty or "Lote afectado" not in df.columns:
            return []
        return [str(v) for v in df["Lote afectado"].dropna().tolist()]

    def get_lotes_disponibles_para_retiro(self) -> list[str]:
        vendidos = set(self.get_lotes_vendidos_aceptados())
        usados   = set(self.get_lotes_usados_retiro())
        return sorted(vendidos - usados)

    def guardar_retiro(self, datos: dict) -> None:
        wb = openpyxl.load_workbook(self.ruta)
        ws = wb["Retiro_Producto"]
        r = self._next_empty_row(ws)
        ws.cell(r, 1,  datos.get("fecha_deteccion"))
        ws.cell(r, 2,  datos.get("codigo_retiro", ""))
        ws.cell(r, 3,  datos.get("lote_afectado", ""))
        ws.cell(r, 4,  datos.get("origen_aviso", ""))
        ws.cell(r, 5,  datos.get("cliente_relacionado", ""))
        ws.cell(r, 6,  datos.get("cantidad_afectada"))
        ws.cell(r, 7,  datos.get("motivo", ""))
        ws.cell(r, 8,  datos.get("accion_inmediata", ""))
        ws.cell(r, 9,  datos.get("producto_inmovilizado", ""))
        ws.cell(r, 10, datos.get("comunicacion_realizada", ""))
        ws.cell(r, 11, datos.get("responsable", ""))
        ws.cell(r, 12, datos.get("estado_caso", "Abierto"))
        ws.cell(r, 13, datos.get("accion_correctiva", ""))
        wb.save(self.ruta)
        wb.close()
        self._reload_data()

    # ─────────────────────── ETIQUETAS ──────────────────────────────

    def get_etiqueta_produccion(self, lote_interno: str) -> dict:
        prod = self.get_produccion_by_lote(lote_interno)
        if not prod:
            return {}
        codigo = self._val(prod.get("Código producto"))
        return {
            "empresa":          self.EMPRESA,
            "ubicacion":        self.UBICACION_EMPRESA,
            "lote_interno":     lote_interno,
            "codigo_producto":  codigo,
            "producto":         self.get_nombre_producto(codigo),
            "fecha_produccion": prod.get("Fecha producción"),
            "dia_juliano":      self._val(prod.get("Día juliano")),
            "kg_sustrato":      prod.get("Kilogramos sustrato"),
            "g_micelio":        prod.get("gramos micelio"),
            "responsable":      self._val(prod.get("Responsable")),
        }

    def get_etiqueta_producto_final(self, lote_interno: str) -> dict:
        term = self.get_terminado_by_lote(lote_interno)
        if not term:
            return {}
        codigo = self._val(term.get("Código producto"))
        return {
            "empresa":         self.EMPRESA,
            "producto":        self.get_nombre_producto(codigo),
            "lote_interno":    lote_interno,
            "codigo_producto": codigo,
            "presentacion":    self._val(term.get("Presentación")),
            "fecha_cosecha":   term.get("Fecha cosecha"),
            "fecha_empaque":   term.get("Fecha empaque"),
            "conservacion":    self.CONSERVACION,
            "productor":       f"{self.EMPRESA}, {self.UBICACION_EMPRESA}",
        }

    # ─────────────────────── UTILITARIOS ────────────────────────────

    def _next_empty_row(self, ws) -> int:
        for row in range(ws.max_row, self.DATA_START - 1, -1):
            if any(ws.cell(row=row, column=c).value for c in range(1, 5)):
                return row + 1
        return self.DATA_START

    def _header_map(self, ws) -> dict[str, int]:
        result = {}
        for cell in ws[self.HEADER_ROW]:
            if cell.value:
                result[str(cell.value).strip()] = cell.column
        return result
