from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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
from services.hongos_service import HongosService


_MODULOS = [
    ("Proveedores",         "proveedores"),
    ("Evaluación Proveedores", "evaluaciones"),
    ("Clientes",            "clientes"),
    ("Recepción MP",        "recepciones"),
    ("Producción Interna",  "producciones"),
    ("Producto Terminado",  "terminados"),
    ("Expedición y Ventas", "expediciones"),
    ("Retiro de Producto",  "retiros"),
]


class ReportePage(QWidget):
    """Vista de reportes con selector de módulo, búsqueda y exportación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._df_full: pd.DataFrame = pd.DataFrame()
        self._df_filtrado: pd.DataFrame = pd.DataFrame()
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self.cargar_registros()

    def showEvent(self, event) -> None:
        """Refresca los datos cada vez que el usuario navega a esta página."""
        super().showEvent(event)
        if self._service:
            self.cargar_registros()

    # ─────────────────── UI ─────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        hdr = QVBoxLayout()
        title = QLabel("Reportes y Exportación")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Selecciona el módulo, filtra los registros y exporta a PDF o Excel.")
        subtitle.setObjectName("pageSubtitle")
        hdr.addWidget(title)
        hdr.addWidget(subtitle)
        layout.addLayout(hdr)

        layout.addWidget(self._build_filtros_card())

        self.tabla = TablaRegistros()
        layout.addWidget(self.tabla)

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

        # Selector de módulo
        lbl_mod = QLabel("Módulo:")
        lbl_mod.setObjectName("fieldLabel")
        controls.addWidget(lbl_mod)
        self.combo_modulo = QComboBox()
        for nombre, _ in _MODULOS:
            self.combo_modulo.addItem(nombre)
        self.combo_modulo.setMinimumWidth(200)
        self.combo_modulo.currentIndexChanged.connect(self.cargar_registros)
        controls.addWidget(self.combo_modulo)

        # Búsqueda libre
        lbl_bus = QLabel("Buscar:")
        lbl_bus.setObjectName("fieldLabel")
        controls.addWidget(lbl_bus)
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Filtrar en todos los campos...")
        self.input_buscar.textChanged.connect(self._filtrar)
        controls.addWidget(self.input_buscar, 1)

        controls.addStretch()

        btn_reload = QPushButton("Actualizar")
        btn_reload.setObjectName("secondaryButton")
        btn_reload.clicked.connect(self.cargar_registros)
        controls.addWidget(btn_reload)

        btn_limpiar = QPushButton("Limpiar filtro")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self._limpiar_filtros)
        controls.addWidget(btn_limpiar)

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

    # ─────────────────── LÓGICA ─────────────────────────────────

    def cargar_registros(self) -> None:
        if not self._service:
            return
        idx = self.combo_modulo.currentIndex()
        _, key = _MODULOS[idx]
        getter = {
            "proveedores":  self._service.get_proveedores_df,
            "evaluaciones": self._service.get_evaluaciones_df,
            "clientes":     self._service.get_clientes_df,
            "recepciones":  self._service.get_recepciones_df,
            "producciones": self._service.get_producciones_df,
            "terminados":   self._service.get_terminados_df,
            "expediciones": self._service.get_expediciones_df,
            "retiros":      self._service.get_retiros_df,
        }.get(key)
        self._df_full = getter() if getter else pd.DataFrame()
        self._df_filtrado = self._df_full.copy()
        self.input_buscar.clear()
        self._render_tabla(self._df_filtrado)

    def _filtrar(self, texto: str) -> None:
        if self._df_full.empty:
            return
        if not texto.strip():
            self._df_filtrado = self._df_full.copy()
        else:
            t = texto.lower()
            mask = self._df_full.apply(
                lambda row: any(t in str(v).lower() for v in row if v is not None),
                axis=1,
            )
            self._df_filtrado = self._df_full[mask]
        self._render_tabla(self._df_filtrado)

    def _limpiar_filtros(self) -> None:
        self.input_buscar.clear()
        self._df_filtrado = self._df_full.copy()
        self._render_tabla(self._df_filtrado)

    def _render_tabla(self, df: pd.DataFrame) -> None:
        self.tabla.cargar_dataframe(df)
        n = len(df)
        self.lbl_total.setText(f"{n} registro{'s' if n != 1 else ''}")

    # ─────────────────── EXPORTAR ───────────────────────────────

    def _exportar_pdf(self) -> None:
        if self._df_filtrado.empty:
            QMessageBox.information(self, "Sin datos", "No hay registros para exportar.")
            return
        modulo = self.combo_modulo.currentText()
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte PDF",
            f"Reporte_{modulo.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            "PDF (*.pdf)",
        )
        if not ruta:
            return
        try:
            self._generar_pdf(self._df_filtrado, modulo, ruta)
            QMessageBox.information(self, "PDF generado", f"Guardado en:\n{ruta}")
        except Exception as ex:
            QMessageBox.critical(self, "Error al generar PDF", str(ex))

    def _exportar_excel(self) -> None:
        if self._df_filtrado.empty:
            QMessageBox.information(self, "Sin datos", "No hay registros para exportar.")
            return
        modulo = self.combo_modulo.currentText()
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Excel",
            f"Reporte_{modulo.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            "Excel (*.xlsx)",
        )
        if not ruta:
            return
        try:
            with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
                self._df_filtrado.to_excel(writer, sheet_name=modulo[:31], index=False)
            QMessageBox.information(self, "Excel exportado", f"Guardado en:\n{ruta}")
        except Exception as ex:
            QMessageBox.critical(self, "Error al exportar Excel", str(ex))

    def _generar_pdf(self, df: pd.DataFrame, modulo: str, ruta: str) -> None:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle,
            Paragraph, Spacer, HRFlowable,
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        doc = SimpleDocTemplate(
            ruta, pagesize=landscape(A4),
            rightMargin=1.5*cm, leftMargin=1.5*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )
        verde  = colors.HexColor("#10B981")
        oscuro = colors.HexColor("#0D1B2E")
        claro  = colors.HexColor("#E2E8F0")
        gris   = colors.HexColor("#64748B")

        t_title = ParagraphStyle("tt", fontName="Helvetica-Bold", fontSize=15,
                                 textColor=claro, alignment=TA_LEFT)
        t_sub   = ParagraphStyle("ts", fontName="Helvetica", fontSize=9,
                                 textColor=gris,  alignment=TA_LEFT)
        t_foot  = ParagraphStyle("tf", fontName="Helvetica", fontSize=8,
                                 textColor=gris,  alignment=TA_CENTER)

        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        story = [
            Paragraph(f"REPORTE — {modulo.upper()}", t_title),
            Paragraph(f"Hongos del Páramo  ·  Generado: {fecha_str}", t_sub),
            HRFlowable(width="100%", thickness=1, color=verde, spaceAfter=0.3*cm),
            Paragraph(f"Total registros: {len(df)}", t_sub),
            Spacer(1, 0.3*cm),
        ]

        # Tabla
        headers = [str(h) for h in df.columns]
        page_w  = landscape(A4)[0] - 3*cm
        col_w   = page_w / len(headers) if headers else page_w

        def _celda(v) -> str:
            if v is None:
                return "Casilla Vacía"
            try:
                if pd.isnull(v):
                    return "Casilla Vacía"
            except (TypeError, ValueError):
                pass
            if isinstance(v, pd.Timestamp):
                if v.hour == 0 and v.minute == 0 and v.second == 0:
                    return v.strftime("%d/%m/%Y")
                return v.strftime("%d/%m/%Y %H:%M")
            s = str(v).strip()
            return "Casilla Vacía" if s.lower() in ("nan", "none", "nat", "") else s

        rows = [headers]
        for _, row in df.iterrows():
            rows.append([_celda(v) for v in row])

        tbl = Table(rows, colWidths=[col_w]*len(headers), repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  oscuro),
            ("TEXTCOLOR",   (0,0), (-1,0),  gris),
            ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 7),
            ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#1A3050")),
            ("LINEBELOW",   (0,0), (-1,0),  1,   verde),
            ("BACKGROUND",  (0,1), (-1,-1), colors.HexColor("#080F1A")),
            ("TEXTCOLOR",   (0,1), (-1,-1), claro),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=oscuro))
        story.append(Paragraph("ICIAGRO CORE · Sistema de Trazabilidad Hongos del Páramo", t_foot))

        doc.build(story)
