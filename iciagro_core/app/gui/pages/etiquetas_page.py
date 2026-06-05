from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from services.hongos_service import HongosService
from utils.date_utils import formatear_fecha


class EtiquetasPage(QWidget):
    """Generación de etiquetas de trazabilidad (Producción y Producto Final)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self._poblar_lotes()

    # ───────────────────────── UI ───────────────────────────────────

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 24, 32, 24)
        main.setSpacing(20)
        main.addLayout(self._build_header())

        self.tabs = QTabWidget()
        self.tabs.setObjectName("etiquetasTabs")
        self.tabs.addTab(self._build_tab_produccion(),    "Etiqueta de Producción (HP)")
        self.tabs.addTab(self._build_tab_producto_final(),"Etiqueta de Producto Final")
        main.addWidget(self.tabs)

    def _build_header(self) -> QVBoxLayout:
        vl = QVBoxLayout()
        vl.setSpacing(4)
        title = QLabel("Generación de Etiquetas")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Selecciona un lote para generar y visualizar la etiqueta. "
            "Exporta en PDF para impresión."
        )
        sub.setObjectName("pageSubtitle")
        sub.setWordWrap(True)
        vl.addWidget(title)
        vl.addWidget(sub)
        return vl

    # ─────────────────── TAB 1: PRODUCCIÓN ──────────────────────────

    def _build_tab_produccion(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("pageContainer")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # Selector
        sel_row = QHBoxLayout()
        lbl = QLabel("Seleccionar lote interno (HP):")
        lbl.setObjectName("fieldLabel")
        self.combo_lote_prod = QComboBox()
        self.combo_lote_prod.setMinimumWidth(260)
        self.combo_lote_prod.setPlaceholderText("Seleccionar lote HP...")
        self.combo_lote_prod.currentTextChanged.connect(self._on_lote_prod_cambiado)
        btn_gen = QPushButton("Generar etiqueta")
        btn_gen.setObjectName("primaryButton")
        btn_gen.clicked.connect(self._generar_pdf_produccion)
        sel_row.addWidget(lbl)
        sel_row.addWidget(self.combo_lote_prod, 1)
        sel_row.addWidget(btn_gen)
        layout.addLayout(sel_row)

        # Vista previa
        self.preview_prod = self._build_label_preview_prod()
        layout.addWidget(self.preview_prod)
        layout.addStretch()

        return widget

    def _build_tab_producto_final(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("pageContainer")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # Selector
        sel_row = QHBoxLayout()
        lbl = QLabel("Seleccionar lote terminado:")
        lbl.setObjectName("fieldLabel")
        self.combo_lote_final = QComboBox()
        self.combo_lote_final.setMinimumWidth(260)
        self.combo_lote_final.setPlaceholderText("Seleccionar lote terminado...")
        self.combo_lote_final.currentTextChanged.connect(self._on_lote_final_cambiado)
        btn_gen = QPushButton("Generar etiqueta")
        btn_gen.setObjectName("primaryButton")
        btn_gen.clicked.connect(self._generar_pdf_final)
        sel_row.addWidget(lbl)
        sel_row.addWidget(self.combo_lote_final, 1)
        sel_row.addWidget(btn_gen)
        layout.addLayout(sel_row)

        # Vista previa
        self.preview_final = self._build_label_preview_final()
        layout.addWidget(self.preview_final)
        layout.addStretch()

        return widget

    # ─────────────── VISTA PREVIA ETIQUETA PRODUCCIÓN ───────────────

    def _build_label_preview_prod(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("labelPreview")
        frame.setMinimumSize(480, 260)
        frame.setMaximumSize(560, 320)
        frame.setStyleSheet(
            "QFrame#labelPreview{"
            "background:#FFFFFF;border:2px solid #3F6B4B;border-radius:12px;"
            "}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header de la etiqueta
        hdr = QHBoxLayout()
        empresa_lbl = QLabel("HONGOS DEL PÁRAMO")
        empresa_lbl.setStyleSheet("font-size:15px;font-weight:700;color:#1A3A23;")
        self._prod_tipo = QLabel("ETIQUETA INTERNA DE CULTIVO")
        self._prod_tipo.setStyleSheet(
            "background:#3F6B4B;color:#FFF;border-radius:4px;"
            "padding:2px 8px;font-size:10px;font-weight:600;"
        )
        hdr.addWidget(empresa_lbl)
        hdr.addStretch()
        hdr.addWidget(self._prod_tipo)
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#3F6B4B;")
        layout.addWidget(sep)

        # Campos de la etiqueta
        body = QHBoxLayout()
        body.setSpacing(24)

        col_izq = QVBoxLayout()
        col_izq.setSpacing(6)
        self._fields_prod: dict[str, QLabel] = {}
        for campo in ("Lote interno", "Código producto", "Fecha producción",
                      "Día juliano", "Kg sustrato", "Gramos micelio"):
            row = QHBoxLayout()
            k = QLabel(f"{campo}:")
            k.setStyleSheet("font-size:10px;font-weight:600;color:#334155;min-width:120px;")
            v = QLabel("—")
            v.setStyleSheet("font-size:11px;color:#0F172A;font-weight:500;")
            row.addWidget(k)
            row.addWidget(v)
            row.addStretch()
            col_izq.addLayout(row)
            self._fields_prod[campo] = v

        col_der = QVBoxLayout()
        col_der.setSpacing(6)
        col_der.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Logo en columna derecha
        logo_lbl_prod = QLabel()
        logo_lbl_prod.setAlignment(Qt.AlignCenter)
        logo_px = QPixmap(self._logo_path())
        if not logo_px.isNull():
            logo_lbl_prod.setPixmap(
                logo_px.scaled(QSize(90, 90), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        col_der.addWidget(logo_lbl_prod)
        col_der.addSpacing(6)

        for campo in ("Empresa", "Responsable"):
            row = QHBoxLayout()
            k = QLabel(f"{campo}:")
            k.setStyleSheet("font-size:10px;font-weight:600;color:#334155;min-width:80px;")
            v = QLabel("—")
            v.setStyleSheet("font-size:11px;color:#0F172A;font-weight:500;")
            row.addWidget(k)
            row.addWidget(v)
            row.addStretch()
            col_der.addLayout(row)
            self._fields_prod[campo] = v
        col_der.addStretch()

        body.addLayout(col_izq, 2)
        body.addLayout(col_der, 1)
        layout.addLayout(body)

        return frame

    # ─────────────── VISTA PREVIA ETIQUETA PRODUCTO FINAL ───────────

    def _build_label_preview_final(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("labelPreviewFinal")
        frame.setMinimumSize(480, 260)
        frame.setMaximumSize(560, 320)
        frame.setStyleSheet(
            "QFrame#labelPreviewFinal{"
            "background:#FFFFFF;border:2px solid #1E3A5F;border-radius:12px;"
            "}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        hdr = QHBoxLayout()
        empresa_lbl = QLabel("HONGOS DEL PÁRAMO")
        empresa_lbl.setStyleSheet("font-size:15px;font-weight:700;color:#1E3A5F;")
        tipo_lbl = QLabel("ETIQUETA PRODUCTO FINAL")
        tipo_lbl.setStyleSheet(
            "background:#1E3A5F;color:#FFF;border-radius:4px;"
            "padding:2px 8px;font-size:10px;font-weight:600;"
        )
        hdr.addWidget(empresa_lbl)
        hdr.addStretch()
        hdr.addWidget(tipo_lbl)
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1E3A5F;")
        layout.addWidget(sep)

        body = QHBoxLayout()
        body.setSpacing(24)

        col_izq = QVBoxLayout()
        col_izq.setSpacing(6)
        self._fields_final: dict[str, QLabel] = {}
        for campo in ("Producto", "Código", "Lote", "Presentación",
                      "Fecha cosecha", "Fecha empaque"):
            row = QHBoxLayout()
            k = QLabel(f"{campo}:")
            k.setStyleSheet("font-size:10px;font-weight:600;color:#334155;min-width:100px;")
            v = QLabel("—")
            v.setStyleSheet("font-size:11px;color:#0F172A;font-weight:500;")
            row.addWidget(k)
            row.addWidget(v)
            row.addStretch()
            col_izq.addLayout(row)
            self._fields_final[campo] = v

        col_der = QVBoxLayout()
        col_der.setSpacing(6)
        col_der.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Logo en columna derecha
        logo_lbl_final = QLabel()
        logo_lbl_final.setAlignment(Qt.AlignCenter)
        logo_px2 = QPixmap(self._logo_path())
        if not logo_px2.isNull():
            logo_lbl_final.setPixmap(
                logo_px2.scaled(QSize(90, 90), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        col_der.addWidget(logo_lbl_final)
        col_der.addSpacing(6)

        for campo in ("Conservación", "Productor"):
            row = QHBoxLayout()
            k = QLabel(f"{campo}:")
            k.setStyleSheet("font-size:10px;font-weight:600;color:#334155;min-width:90px;")
            v = QLabel("—")
            v.setStyleSheet("font-size:11px;color:#0F172A;font-weight:500;word-wrap:true;")
            v.setWordWrap(True)
            row.addWidget(k)
            row.addWidget(v)
            col_der.addLayout(row)
            self._fields_final[campo] = v
        col_der.addStretch()

        body.addLayout(col_izq, 2)
        body.addLayout(col_der, 1)
        layout.addLayout(body)

        return frame

    # ─────────────────── HELPERS ────────────────────────────────────

    def _logo_path(self) -> str:
        if getattr(sys, "frozen", False):
            assets_dir = Path(sys._MEIPASS) / "assets"
        else:
            assets_dir = Path(__file__).resolve().parents[2] / "assets"
        candidate = assets_dir / "logo_hongos.png"
        return str(candidate) if candidate.is_file() else ""

    # ─────────────────── POBLAR / REFRESH ───────────────────────────

    def _poblar_lotes(self) -> None:
        if not self._service:
            return
        self.combo_lote_prod.clear()
        self.combo_lote_prod.addItem("")
        for lote in self._service.get_lotes_internos():
            self.combo_lote_prod.addItem(lote)

        self.combo_lote_final.clear()
        self.combo_lote_final.addItem("")
        for lote in self._service.get_lotes_aceptados_terminado():
            self.combo_lote_final.addItem(lote)

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _on_lote_prod_cambiado(self, lote: str) -> None:
        if not self._service or not lote:
            for v in self._fields_prod.values():
                v.setText("—")
            return
        datos = self._service.get_etiqueta_produccion(lote)
        if not datos:
            return
        fecha = datos.get("fecha_produccion")
        self._fields_prod["Lote interno"].setText(str(datos.get("lote_interno", "—")))
        self._fields_prod["Código producto"].setText(str(datos.get("codigo_producto", "—")))
        self._fields_prod["Fecha producción"].setText(
            formatear_fecha(fecha) if fecha else "—"
        )
        self._fields_prod["Día juliano"].setText(str(datos.get("dia_juliano", "—")))
        self._fields_prod["Kg sustrato"].setText(str(datos.get("kg_sustrato", "—")))
        self._fields_prod["Gramos micelio"].setText(str(datos.get("g_micelio", "—")))
        self._fields_prod["Empresa"].setText(str(datos.get("empresa", "—")))
        self._fields_prod["Responsable"].setText(str(datos.get("responsable", "—")))

    def _on_lote_final_cambiado(self, lote: str) -> None:
        if not self._service or not lote:
            for v in self._fields_final.values():
                v.setText("—")
            return
        datos = self._service.get_etiqueta_producto_final(lote)
        if not datos:
            return
        fc = datos.get("fecha_cosecha")
        fe = datos.get("fecha_empaque")
        self._fields_final["Producto"].setText(str(datos.get("producto", "—")))
        self._fields_final["Código"].setText(str(datos.get("codigo_producto", "—")))
        self._fields_final["Lote"].setText(str(datos.get("lote_interno", "—")))
        self._fields_final["Presentación"].setText(str(datos.get("presentacion", "—")))
        self._fields_final["Fecha cosecha"].setText(formatear_fecha(fc) if fc else "—")
        self._fields_final["Fecha empaque"].setText(formatear_fecha(fe) if fe else "—")
        self._fields_final["Conservación"].setText(str(datos.get("conservacion", "—")))
        self._fields_final["Productor"].setText(str(datos.get("productor", "—")))

    # ─────────────────── GENERAR PDF ────────────────────────────────

    def _generar_pdf_produccion(self) -> None:
        if not self._service:
            return
        lote = self.combo_lote_prod.currentText().strip()
        if not lote:
            QMessageBox.warning(self, "Sin lote", "Selecciona un lote primero.")
            return
        datos = self._service.get_etiqueta_produccion(lote)
        if not datos:
            QMessageBox.warning(self, "Sin datos", f"No hay datos para el lote {lote}.")
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar etiqueta PDF",
            f"Etiqueta_Produccion_{lote.replace('-', '_')}.pdf",
            "PDF (*.pdf)",
        )
        if not ruta:
            return
        try:
            self._generar_pdf_etiqueta_produccion(datos, ruta)
            QMessageBox.information(self, "PDF generado", f"Etiqueta guardada en:\n{ruta}")
        except Exception as ex:
            QMessageBox.critical(self, "Error al generar PDF", str(ex))

    def _generar_pdf_final(self) -> None:
        if not self._service:
            return
        lote = self.combo_lote_final.currentText().strip()
        if not lote:
            QMessageBox.warning(self, "Sin lote", "Selecciona un lote primero.")
            return
        datos = self._service.get_etiqueta_producto_final(lote)
        if not datos:
            QMessageBox.warning(self, "Sin datos", f"No hay datos para el lote {lote}.")
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar etiqueta PDF",
            f"Etiqueta_Final_{lote.replace('-', '_')}.pdf",
            "PDF (*.pdf)",
        )
        if not ruta:
            return
        try:
            self._generar_pdf_etiqueta_final(datos, ruta)
            QMessageBox.information(self, "PDF generado", f"Etiqueta guardada en:\n{ruta}")
        except Exception as ex:
            QMessageBox.critical(self, "Error al generar PDF", str(ex))

    # ─────────────────── PDF (reportlab) ────────────────────────────

    def _generar_pdf_etiqueta_produccion(self, datos: dict, ruta: str) -> None:
        from reportlab.lib.pagesizes import A6, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        doc = SimpleDocTemplate(
            ruta, pagesize=landscape(A6),
            rightMargin=1*cm, leftMargin=1*cm,
            topMargin=1*cm, bottomMargin=1*cm,
        )
        verde = colors.HexColor("#3F6B4B")
        oscuro = colors.HexColor("#0F172A")
        claro  = colors.HexColor("#E5E7EB")

        titulo_style = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=13,
                                      textColor=verde, alignment=TA_LEFT)
        sub_style    = ParagraphStyle("s", fontName="Helvetica", fontSize=8,
                                      textColor=claro, alignment=TA_LEFT)
        campo_style  = ParagraphStyle("c", fontName="Helvetica-Bold", fontSize=8,
                                      textColor=colors.HexColor("#94A3B8"), alignment=TA_LEFT)
        valor_style  = ParagraphStyle("v", fontName="Helvetica", fontSize=9,
                                      textColor=claro, alignment=TA_LEFT)

        fecha_str = formatear_fecha(datos.get("fecha_produccion")) or "—"
        story = [
            Paragraph("HONGOS DEL PÁRAMO", titulo_style),
            Paragraph("ETIQUETA INTERNA DE CULTIVO", sub_style),
            HRFlowable(width="100%", thickness=1, color=verde),
            Spacer(1, 0.2*cm),
        ]

        filas = [
            ["Lote interno",    datos.get("lote_interno", "—"),
             "Empresa",         datos.get("empresa", "—")],
            ["Código producto", datos.get("codigo_producto", "—"),
             "Responsable",     datos.get("responsable", "—")],
            ["Fecha producción",fecha_str,
             "Ubicación",       datos.get("ubicacion", "—")],
            ["Día juliano",     datos.get("dia_juliano", "—"), "", ""],
            ["Kg sustrato",     str(datos.get("kg_sustrato", "—")),
             "Gramos micelio",  str(datos.get("g_micelio", "—"))],
        ]

        t = Table(filas, colWidths=[3*cm, 4.5*cm, 3*cm, 4.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), oscuro),
            ("TEXTCOLOR", (0,0), (-1,-1), claro),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#94A3B8")),
            ("TEXTCOLOR", (2,0), (2,-1), colors.HexColor("#94A3B8")),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#334155")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        doc.build(story)

    def _generar_pdf_etiqueta_final(self, datos: dict, ruta: str) -> None:
        from reportlab.lib.pagesizes import A6, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.enums import TA_LEFT

        doc = SimpleDocTemplate(
            ruta, pagesize=landscape(A6),
            rightMargin=1*cm, leftMargin=1*cm,
            topMargin=1*cm, bottomMargin=1*cm,
        )
        azul  = colors.HexColor("#1E3A5F")
        oscuro= colors.HexColor("#0F172A")
        claro = colors.HexColor("#E5E7EB")

        titulo_style = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=13,
                                      textColor=azul, alignment=TA_LEFT)
        sub_style    = ParagraphStyle("s", fontName="Helvetica", fontSize=8,
                                      textColor=claro, alignment=TA_LEFT)

        fc = formatear_fecha(datos.get("fecha_cosecha")) or "—"
        fe = formatear_fecha(datos.get("fecha_empaque")) or "—"

        story = [
            Paragraph("HONGOS DEL PÁRAMO", titulo_style),
            Paragraph("ETIQUETA PRODUCTO FINAL", sub_style),
            HRFlowable(width="100%", thickness=1, color=azul),
            Spacer(1, 0.2*cm),
        ]

        filas = [
            ["Producto",       datos.get("producto", "—"),
             "Conservación",   datos.get("conservacion", "—")],
            ["Código",         datos.get("codigo_producto", "—"),
             "Productor",      datos.get("productor", "—")],
            ["Lote",           datos.get("lote_interno", "—"), "", ""],
            ["Presentación",   datos.get("presentacion", "—"), "", ""],
            ["Fecha cosecha",  fc, "Fecha empaque", fe],
        ]

        t = Table(filas, colWidths=[3*cm, 4.5*cm, 3*cm, 4.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), oscuro),
            ("TEXTCOLOR", (0,0), (-1,-1), claro),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#94A3B8")),
            ("TEXTCOLOR", (2,0), (2,-1), colors.HexColor("#94A3B8")),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#334155")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        doc.build(story)
