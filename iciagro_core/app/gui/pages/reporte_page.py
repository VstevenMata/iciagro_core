from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from services.excel_service import ExcelService
from services.pdf_service import PDFService


class ReportePage(QWidget):
    """
    Vista de reportes con filtros y exportación PDF/Excel.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[ExcelService] = None
        self._df_full: pd.DataFrame = pd.DataFrame()
        self._df_filtrado: pd.DataFrame = pd.DataFrame()
        self._pdf_service = PDFService()
        self._setup_ui()

    def set_service(self, service: ExcelService) -> None:
        self._service = service
        self.cargar_registros()

    # ─────────────────── UI ─────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # Header
        hdr = QVBoxLayout()
        title = QLabel("Reportes y Exportación")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Filtra los registros y exporta a PDF o Excel.")
        subtitle.setObjectName("pageSubtitle")
        hdr.addWidget(title)
        hdr.addWidget(subtitle)
        layout.addLayout(hdr)

        # Filtros
        layout.addWidget(self._build_filtros_card())

        # Tabla
        self.tabla = TablaRegistros()
        layout.addWidget(self.tabla)

        # Acciones de exportación
        layout.addLayout(self._build_export_actions())

    def _build_filtros_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        vlayout = QVBoxLayout(card)
        vlayout.setContentsMargins(20, 16, 20, 16)
        vlayout.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("Filtros")
        title.setObjectName("cardTitle")
        self.lbl_total = QLabel("0 registros")
        self.lbl_total.setObjectName("statusBadge")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self.lbl_total)
        vlayout.addLayout(title_row)

        controls = QHBoxLayout()
        controls.setSpacing(12)

        # Filtro fecha desde
        controls.addWidget(self._flbl("Desde:"))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate(2020, 1, 1))
        self.fecha_desde.setDisplayFormat("dd/MM/yyyy")
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setMaximumWidth(130)
        controls.addWidget(self.fecha_desde)

        controls.addWidget(self._flbl("Hasta:"))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setDisplayFormat("dd/MM/yyyy")
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setMaximumWidth(130)
        controls.addWidget(self.fecha_hasta)

        controls.addWidget(self._flbl("Proveedor:"))
        self.input_prov = QLineEdit()
        self.input_prov.setPlaceholderText("Filtrar por código...")
        self.input_prov.setMaximumWidth(160)
        controls.addWidget(self.input_prov)

        controls.addWidget(self._flbl("Solo REVISAR:"))
        self.btn_solo_revisar = QPushButton("Mostrar todos")
        self.btn_solo_revisar.setObjectName("secondaryButton")
        self.btn_solo_revisar.setCheckable(True)
        self.btn_solo_revisar.toggled.connect(self._toggle_revisar)
        controls.addWidget(self.btn_solo_revisar)

        controls.addStretch()

        self.btn_filtrar = QPushButton("Aplicar filtros")
        self.btn_filtrar.setObjectName("primaryButton")
        self.btn_filtrar.clicked.connect(self._aplicar_filtros)
        controls.addWidget(self.btn_filtrar)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("secondaryButton")
        self.btn_limpiar.clicked.connect(self._limpiar_filtros)
        controls.addWidget(self.btn_limpiar)

        vlayout.addLayout(controls)
        return card

    def _build_export_actions(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.addStretch()

        self.btn_export_excel = QPushButton("Exportar Excel")
        self.btn_export_excel.setObjectName("secondaryButton")
        self.btn_export_excel.clicked.connect(self._exportar_excel)
        layout.addWidget(self.btn_export_excel)

        self.btn_export_pdf = QPushButton("Exportar PDF")
        self.btn_export_pdf.setObjectName("primaryButton")
        self.btn_export_pdf.clicked.connect(self._exportar_pdf)
        layout.addWidget(self.btn_export_pdf)

        return layout

    def _flbl(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lbl

    # ─────────────────── LÓGICA ─────────────────────────────────

    def cargar_registros(self) -> None:
        if not self._service:
            return
        self._df_full = self._service.cargar_registros()
        self._df_filtrado = self._df_full.copy()
        self._render_tabla(self._df_filtrado)

    def _aplicar_filtros(self) -> None:
        if self._df_full.empty:
            return
        df = self._df_full.copy()

        prov = self.input_prov.text().strip().lower()
        if prov and df.shape[1] > 1:
            col_prov = df.columns[1]
            df = df[df[col_prov].astype(str).str.lower().str.contains(prov, na=False)]

        solo_rev = self.btn_solo_revisar.isChecked()
        if solo_rev and df.shape[1] > 13:
            col_rev = df.columns[13]
            df = df[df[col_rev].astype(str).str.strip() == "REVISAR"]

        self._df_filtrado = df
        self._render_tabla(self._df_filtrado)

    def _limpiar_filtros(self) -> None:
        self.fecha_desde.setDate(QDate(2020, 1, 1))
        self.fecha_hasta.setDate(QDate.currentDate())
        self.input_prov.clear()
        self.btn_solo_revisar.setChecked(False)
        self._df_filtrado = self._df_full.copy()
        self._render_tabla(self._df_filtrado)

    def _toggle_revisar(self, checked: bool) -> None:
        self.btn_solo_revisar.setText(
            "Solo REVISAR activo" if checked else "Mostrar todos"
        )
        self._aplicar_filtros()

    def _render_tabla(self, df: pd.DataFrame) -> None:
        self.tabla.cargar_dataframe(df)
        n = len(df)
        self.lbl_total.setText(f"{n} registro{'s' if n != 1 else ''}")

    # ─────────────────── EXPORTAR ───────────────────────────────

    def _exportar_pdf(self) -> None:
        if self._df_filtrado.empty:
            QMessageBox.information(self, "Sin datos", "No hay registros para exportar.")
            return
        if not self._service:
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte PDF",
            f"Reporte_Trazabilidad_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            "PDF (*.pdf)",
        )
        if not ruta:
            return

        try:
            filtros = {}
            if self.input_prov.text().strip():
                filtros["Proveedor"] = self.input_prov.text().strip()
            if self.btn_solo_revisar.isChecked():
                filtros["Estado"] = "Solo REVISAR"

            empresa = self._service.config.get("empresa", "Lácteos del Páramo")
            prefijo = self._service.config.get("prefijo", "LDP")

            self._pdf_service.generar_reporte(
                df=self._df_filtrado,
                ruta_destino=ruta,
                empresa=empresa,
                prefijo=prefijo,
                filtros=filtros,
            )
            QMessageBox.information(
                self, "PDF generado", f"Reporte guardado en:\n{ruta}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Error al generar PDF", str(ex))

    def _exportar_excel(self) -> None:
        if self._df_filtrado.empty:
            QMessageBox.information(self, "Sin datos", "No hay registros para exportar.")
            return
        if not self._service:
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Excel",
            f"Registros_Trazabilidad_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            "Excel (*.xlsx)",
        )
        if not ruta:
            return

        try:
            self._service.exportar_excel(self._df_filtrado, ruta)
            QMessageBox.information(
                self, "Excel exportado", f"Archivo guardado en:\n{ruta}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Error al exportar Excel", str(ex))
