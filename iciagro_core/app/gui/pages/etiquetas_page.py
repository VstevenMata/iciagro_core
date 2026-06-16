from __future__ import annotations

import sys
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
    """Generación de etiquetas de trazabilidad (Recepción MP, Producción y Producto Final)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self._poblar_lotes()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._service:
            self._poblar_lotes()

    def cargar(self) -> None:
        self._poblar_lotes()

    # ───────────────────────── UI ───────────────────────────────────

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 24, 32, 24)
        main.setSpacing(20)
        main.addLayout(self._build_header())

        self.tabs = QTabWidget()
        self.tabs.setObjectName("etiquetasTabs")
        self.tabs.addTab(self._build_tab_recepcion(),     "Etiqueta de Recepción MP")
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

    # ─────────────────── TAB 1: RECEPCIÓN MP ────────────────────────

    def _build_tab_recepcion(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("pageContainer")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # Selector
        sel_row = QHBoxLayout()
        lbl = QLabel("Seleccionar código de recepción:")
        lbl.setObjectName("fieldLabel")
        self.combo_recepcion = QComboBox()
        self.combo_recepcion.setMinimumWidth(260)
        self.combo_recepcion.setPlaceholderText("Seleccionar código de recepción...")
        self.combo_recepcion.currentTextChanged.connect(self._on_recepcion_cambiada)
        btn_gen = QPushButton("Generar etiqueta")
        btn_gen.setObjectName("primaryButton")
        btn_gen.clicked.connect(self._generar_pdf_recepcion)
        sel_row.addWidget(lbl)
        sel_row.addWidget(self.combo_recepcion, 1)
        sel_row.addWidget(btn_gen)
        layout.addLayout(sel_row)

        # Vista previa — centrada
        self.preview_recepcion = self._build_label_preview_recepcion()
        center_rec = QHBoxLayout()
        center_rec.addStretch()
        center_rec.addWidget(self.preview_recepcion)
        center_rec.addStretch()
        layout.addLayout(center_rec)
        layout.addStretch()

        return widget

    # ─────────────────── TAB 2: PRODUCCIÓN ──────────────────────────

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

        # Vista previa — centrada
        self.preview_prod = self._build_label_preview_prod()
        center_prod = QHBoxLayout()
        center_prod.addStretch()
        center_prod.addWidget(self.preview_prod)
        center_prod.addStretch()
        layout.addLayout(center_prod)
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

        # Vista previa — centrada
        self.preview_final = self._build_label_preview_final()
        center_final = QHBoxLayout()
        center_final.addStretch()
        center_final.addWidget(self.preview_final)
        center_final.addStretch()
        layout.addLayout(center_final)
        layout.addStretch()

        return widget

    # ─────────────── VISTA PREVIA ETIQUETA RECEPCIÓN MP ─────────────

    def _build_label_preview_recepcion(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("labelPreviewRecepcion")
        frame.setMinimumSize(480, 280)
        frame.setMaximumSize(560, 360)
        frame.setStyleSheet(
            "QFrame#labelPreviewRecepcion{"
            "background:#FFFFFF;border:2px solid #0EA5E9;border-radius:12px;"
            "}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header de la etiqueta
        hdr = QHBoxLayout()
        empresa_lbl = QLabel("HONGOS DEL PÁRAMO")
        empresa_lbl.setStyleSheet("font-size:15px;font-weight:800;color:#064E3B;letter-spacing:0.3px;")
        tipo_lbl = QLabel("ETIQUETA DE RECEPCIÓN MATERIA PRIMA")
        tipo_lbl.setStyleSheet(
            "background:#0EA5E9;color:#FFFFFF;border-radius:4px;"
            "padding:2px 10px;font-size:10px;font-weight:700;letter-spacing:0.5px;"
        )
        hdr.addWidget(empresa_lbl)
        hdr.addStretch()
        hdr.addWidget(tipo_lbl)
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#0EA5E9;")
        layout.addWidget(sep)

        # Campos de la etiqueta
        body = QHBoxLayout()
        body.setSpacing(24)

        col_izq = QVBoxLayout()
        col_izq.setSpacing(6)
        self._fields_recepcion: dict[str, QLabel] = {}
        for campo in ("Código recepción", "Proveedor", "Materia prima",
                      "Fecha recepción", "Día juliano", "Cantidad recibida"):
            row = QHBoxLayout()
            k = QLabel(f"{campo}:")
            k.setStyleSheet("font-size:10px;font-weight:600;color:#334155;min-width:120px;")
            v = QLabel("—")
            v.setStyleSheet("font-size:11px;color:#0F172A;font-weight:500;")
            row.addWidget(k)
            row.addWidget(v)
            row.addStretch()
            col_izq.addLayout(row)
            self._fields_recepcion[campo] = v

        col_der = QVBoxLayout()
        col_der.setSpacing(6)
        col_der.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Logo en columna derecha
        logo_lbl_rec = QLabel()
        logo_lbl_rec.setAlignment(Qt.AlignCenter)
        logo_px = QPixmap(self._logo_path())
        if not logo_px.isNull():
            logo_lbl_rec.setPixmap(
                logo_px.scaled(QSize(90, 90), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        col_der.addWidget(logo_lbl_rec)
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
            self._fields_recepcion[campo] = v
        col_der.addStretch()

        body.addLayout(col_izq, 2)
        body.addLayout(col_der, 1)
        layout.addLayout(body)

        # Observaciones — fila completa con ajuste de línea
        obs_row = QHBoxLayout()
        obs_row.setSpacing(6)
        obs_k = QLabel("Observaciones:")
        obs_k.setStyleSheet("font-size:10px;font-weight:600;color:#334155;")
        obs_v = QLabel("—")
        obs_v.setStyleSheet("font-size:11px;color:#0F172A;font-weight:500;")
        obs_v.setWordWrap(True)
        obs_row.addWidget(obs_k)
        obs_row.addWidget(obs_v, 1)
        layout.addLayout(obs_row)
        self._fields_recepcion["Observaciones"] = obs_v

        return frame

    # ─────────────── VISTA PREVIA ETIQUETA PRODUCCIÓN ───────────────

    def _build_label_preview_prod(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("labelPreview")
        frame.setMinimumSize(480, 260)
        frame.setMaximumSize(560, 320)
        frame.setStyleSheet(
            "QFrame#labelPreview{"
            "background:#FFFFFF;border:2px solid #10B981;border-radius:12px;"
            "}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header de la etiqueta
        hdr = QHBoxLayout()
        empresa_lbl = QLabel("HONGOS DEL PÁRAMO")
        empresa_lbl.setStyleSheet("font-size:15px;font-weight:800;color:#064E3B;letter-spacing:0.3px;")
        self._prod_tipo = QLabel("ETIQUETA INTERNA DE CULTIVO")
        self._prod_tipo.setStyleSheet(
            "background:#059669;color:#FFFFFF;border-radius:4px;"
            "padding:2px 10px;font-size:10px;font-weight:700;letter-spacing:0.5px;"
        )
        hdr.addWidget(empresa_lbl)
        hdr.addStretch()
        hdr.addWidget(self._prod_tipo)
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#10B981;")
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

    def _logo_image(self):
        """Logo reducido (PNG en memoria) para incrustar en el PDF sin inflar su tamaño."""
        logo_path = self._logo_path()
        if not logo_path:
            return None
        try:
            import io
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img.thumbnail((300, 300))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf
        except Exception:
            return None

    # ─────────────────── POBLAR / REFRESH ───────────────────────────

    def _poblar_lotes(self) -> None:
        if not self._service:
            return
        self.combo_recepcion.clear()
        self.combo_recepcion.addItem("")
        for codigo in self._service.get_codigos_recepcion():
            self.combo_recepcion.addItem(codigo)

        self.combo_lote_prod.clear()
        self.combo_lote_prod.addItem("")
        for lote in self._service.get_lotes_internos():
            self.combo_lote_prod.addItem(lote)

        self.combo_lote_final.clear()
        self.combo_lote_final.addItem("")
        for lote in self._service.get_lotes_aceptados_terminado():
            self.combo_lote_final.addItem(lote)

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _on_recepcion_cambiada(self, codigo: str) -> None:
        if not self._service or not codigo:
            for v in self._fields_recepcion.values():
                v.setText("—")
            return
        datos = self._service.get_etiqueta_recepcion(codigo)
        if not datos:
            return
        fecha = datos.get("fecha_recepcion")
        cantidad_txt = self._formatear_cantidad(datos.get("cantidad"), datos.get("unidad"))
        self._fields_recepcion["Código recepción"].setText(str(datos.get("codigo_recepcion") or "—"))
        self._fields_recepcion["Proveedor"].setText(str(datos.get("proveedor") or "—"))
        self._fields_recepcion["Materia prima"].setText(str(datos.get("materia_prima") or "—"))
        self._fields_recepcion["Fecha recepción"].setText(formatear_fecha(fecha) if fecha else "—")
        self._fields_recepcion["Día juliano"].setText(str(datos.get("dia_juliano") or "—"))
        self._fields_recepcion["Cantidad recibida"].setText(cantidad_txt)
        self._fields_recepcion["Empresa"].setText(str(datos.get("empresa") or "—"))
        self._fields_recepcion["Responsable"].setText(str(datos.get("responsable") or "—"))
        self._fields_recepcion["Observaciones"].setText(str(datos.get("observaciones") or "—"))

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

    @staticmethod
    def _formatear_cantidad(cantidad, unidad) -> str:
        if cantidad is None or str(cantidad).strip() == "":
            return "—"
        try:
            valor = float(cantidad)
            texto = f"{valor:g}"
        except (TypeError, ValueError):
            texto = str(cantidad).strip()
        unidad_txt = str(unidad).strip() if unidad else ""
        return f"{texto} {unidad_txt}".strip()

    def _generar_pdf_recepcion(self) -> None:
        if not self._service:
            return
        codigo = self.combo_recepcion.currentText().strip()
        if not codigo:
            QMessageBox.warning(self, "Sin código", "Selecciona un código de recepción primero.")
            return
        datos = self._service.get_etiqueta_recepcion(codigo)
        if not datos:
            QMessageBox.warning(self, "Sin datos", f"No hay datos para la recepción {codigo}.")
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar etiqueta PDF",
            f"Etiqueta_Recepcion_{codigo.replace('-', '_')}.pdf",
            "PDF (*.pdf)",
        )
        if not ruta:
            return
        fecha = datos.get("fecha_recepcion")
        campos_izq = [
            ("Código recepción", datos.get("codigo_recepcion") or "—"),
            ("Proveedor", datos.get("proveedor") or "—"),
            ("Materia prima", datos.get("materia_prima") or "—"),
            ("Fecha recepción", formatear_fecha(fecha) if fecha else "—"),
            ("Día juliano", datos.get("dia_juliano") or "—"),
            ("Cantidad recibida", self._formatear_cantidad(datos.get("cantidad"), datos.get("unidad"))),
        ]
        campos_der = [
            ("Empresa", datos.get("empresa") or "—"),
            ("Responsable", datos.get("responsable") or "—"),
        ]
        observaciones = str(datos.get("observaciones") or "").strip()
        try:
            self._generar_pdf_etiqueta(
                ruta, "ETIQUETA DE RECEPCIÓN MP", "#0EA5E9", campos_izq, campos_der,
                observaciones=observaciones,
            )
            QMessageBox.information(self, "PDF generado", f"Etiqueta guardada en:\n{ruta}")
            idx = self.combo_recepcion.findText(codigo)
            if idx >= 0:
                self.combo_recepcion.removeItem(idx)
        except Exception as ex:
            QMessageBox.critical(self, "Error al generar PDF", str(ex))

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
        fecha = datos.get("fecha_produccion")
        campos_izq = [
            ("Lote interno", datos.get("lote_interno") or "—"),
            ("Código producto", datos.get("codigo_producto") or "—"),
            ("Fecha producción", formatear_fecha(fecha) if fecha else "—"),
            ("Día juliano", datos.get("dia_juliano") or "—"),
            ("Kg sustrato", datos.get("kg_sustrato") if datos.get("kg_sustrato") is not None else "—"),
            ("Gramos micelio", datos.get("g_micelio") if datos.get("g_micelio") is not None else "—"),
        ]
        campos_der = [
            ("Empresa", datos.get("empresa") or "—"),
            ("Responsable", datos.get("responsable") or "—"),
        ]
        try:
            self._generar_pdf_etiqueta(ruta, "ETIQUETA INTERNA DE CULTIVO", "#059669", campos_izq, campos_der)
            QMessageBox.information(self, "PDF generado", f"Etiqueta guardada en:\n{ruta}")
            idx = self.combo_lote_prod.findText(lote)
            if idx >= 0:
                self.combo_lote_prod.removeItem(idx)
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
        fc = datos.get("fecha_cosecha")
        fe = datos.get("fecha_empaque")
        campos_izq = [
            ("Producto", datos.get("producto") or "—"),
            ("Código", datos.get("codigo_producto") or "—"),
            ("Lote", datos.get("lote_interno") or "—"),
            ("Presentación", datos.get("presentacion") or "—"),
            ("Fecha cosecha", formatear_fecha(fc) if fc else "—"),
            ("Fecha empaque", formatear_fecha(fe) if fe else "—"),
        ]
        campos_der = [
            ("Conservación", datos.get("conservacion") or "—"),
            ("Productor", datos.get("productor") or "—"),
        ]
        try:
            self._generar_pdf_etiqueta(ruta, "ETIQUETA PRODUCTO FINAL", "#1E3A5F", campos_izq, campos_der)
            QMessageBox.information(self, "PDF generado", f"Etiqueta guardada en:\n{ruta}")
            idx = self.combo_lote_final.findText(lote)
            if idx >= 0:
                self.combo_lote_final.removeItem(idx)
        except Exception as ex:
            QMessageBox.critical(self, "Error al generar PDF", str(ex))

    # ─────────────────── PDF — generación en texto (reportlab) ──────

    def _generar_pdf_etiqueta(
        self,
        ruta: str,
        badge_texto: str,
        color_hex: str,
        campos_izq: list[tuple[str, object]],
        campos_der: list[tuple[str, object]],
        observaciones: str = "",
    ) -> None:
        """Genera un PDF formal a partir de los datos (sin capturar imágenes)."""
        from xml.sax.saxutils import escape

        from reportlab.lib.colors import HexColor, white
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A6, landscape
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            HRFlowable,
            Image as RLImage,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        page_w, _ = landscape(A6)
        margen = 5 * mm
        ancho_total = page_w - 2 * margen

        style_empresa = ParagraphStyle(
            "empresa", fontName="Helvetica-Bold", fontSize=13,
            textColor=HexColor("#064E3B"),
        )
        style_badge = ParagraphStyle(
            "badge", fontName="Helvetica-Bold", fontSize=8,
            textColor=white, alignment=TA_CENTER,
        )
        style_label = ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=8,
            textColor=HexColor("#334155"),
        )
        style_value = ParagraphStyle(
            "value", fontName="Helvetica", fontSize=9,
            textColor=HexColor("#0F172A"),
        )

        # Encabezado: nombre de empresa + insignia de tipo de etiqueta
        ancho_izq_hdr = ancho_total * 0.58
        ancho_der_hdr = ancho_total * 0.42
        header = Table(
            [[Paragraph("HONGOS DEL PÁRAMO", style_empresa), Paragraph(badge_texto, style_badge)]],
            colWidths=[ancho_izq_hdr, ancho_der_hdr],
        )
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BACKGROUND", (1, 0), (1, 0), HexColor(color_hex)),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (1, 0), (1, 0), 10),
            ("TOPPADDING", (1, 0), (1, 0), 4),
            ("BOTTOMPADDING", (1, 0), (1, 0), 4),
        ]))

        separador = HRFlowable(
            width="100%", thickness=1.2, color=HexColor(color_hex),
            spaceBefore=0, spaceAfter=0,
        )

        # Cuerpo: dos columnas (campos principales | logo + datos de empresa)
        ancho_izq = ancho_total * 0.60
        ancho_der = ancho_total * 0.40

        tabla_izq = self._tabla_campos(campos_izq, ancho_izq, style_label, style_value)

        contenido_der = []
        logo_img = self._logo_image()
        if logo_img is not None:
            logo = RLImage(logo_img, width=22 * mm, height=22 * mm)
            logo.hAlign = "CENTER"
            contenido_der.append(logo)
            contenido_der.append(Spacer(1, 2 * mm))
        contenido_der.append(self._tabla_campos(campos_der, ancho_der, style_label, style_value))

        cuerpo = Table([[tabla_izq, contenido_der]], colWidths=[ancho_izq, ancho_der])
        cuerpo.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        doc = SimpleDocTemplate(
            ruta,
            pagesize=landscape(A6),
            rightMargin=margen,
            leftMargin=margen,
            topMargin=margen,
            bottomMargin=margen,
        )

        elementos = [header, Spacer(1, 3 * mm), separador, Spacer(1, 3 * mm), cuerpo]

        if observaciones:
            tabla_obs = Table(
                [[Paragraph("Observaciones:", style_label), Paragraph(escape(observaciones), style_value)]],
                colWidths=[ancho_total * 0.18, ancho_total * 0.82],
            )
            tabla_obs.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            elementos += [Spacer(1, 2 * mm), tabla_obs]

        doc.build(elementos)

    @staticmethod
    def _tabla_campos(campos, ancho, style_label, style_value):
        from xml.sax.saxutils import escape

        from reportlab.platypus import Paragraph, Table, TableStyle

        data = []
        for clave, valor in campos:
            texto = str(valor) if valor not in (None, "") else "—"
            data.append([
                Paragraph(f"{escape(str(clave))}:", style_label),
                Paragraph(escape(texto), style_value),
            ])
        tabla = Table(data, colWidths=[ancho * 0.42, ancho * 0.58])
        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return tabla
