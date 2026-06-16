from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from gui.event_bus import DataEventBus
from services.hongos_service import HongosService


class RetiroPage(QWidget):
    """Gestión de eventos de retiro o inmovilización de producto."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self._poblar_combos()
        self._recalcular_codigo()
        self.cargar()

    def showEvent(self, event) -> None:
        """Refresca lotes cada vez que el usuario navega a esta página."""
        super().showEvent(event)
        if self._service:
            self._poblar_combos()
            self._recalcular_codigo()
            self.cargar()

    # ───────────────────────── UI ───────────────────────────────────

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 24, 32, 24)
        main.setSpacing(20)
        main.addLayout(self._build_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")

        inner = QWidget()
        inner.setObjectName("pageContainer")
        vl = QVBoxLayout(inner)
        vl.setSpacing(16)
        vl.setContentsMargins(0, 0, 8, 0)
        vl.addWidget(self._build_form_card())
        vl.addWidget(self._build_tabla_card())
        vl.addStretch()
        scroll.setWidget(inner)
        main.addWidget(scroll)

    def _build_header(self) -> QVBoxLayout:
        vl = QVBoxLayout()
        vl.setSpacing(4)
        title = QLabel("Retiro de Producto")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Gestiona eventos de retiro o inmovilización. "
            "Solo se muestran lotes de Expedición con condición Aceptada no utilizados en retiros previos."
        )
        sub.setObjectName("pageSubtitle")
        sub.setWordWrap(True)
        vl.addWidget(title)
        vl.addWidget(sub)
        return vl

    def _build_form_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        row_title = QHBoxLayout()
        title = QLabel("Nuevo Evento de Retiro")
        title.setObjectName("cardTitle")
        badge = QLabel("Código automático")
        badge.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(badge)
        layout.addLayout(row_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fila 0: Fecha detección y Código retiro
        grid.addWidget(self._flbl("Fecha detección *"), 0, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.dateChanged.connect(self._recalcular_codigo)
        grid.addWidget(self.fecha_edit, 0, 1)

        grid.addWidget(self._flbl("Código retiro"), 0, 2)
        self.lbl_codigo = self._auto_lbl()
        self.lbl_codigo.setStyleSheet(
            "background:#2D0A0A;border:1px solid #8B3F3F;border-radius:6px;"
            "padding:6px 10px;font-size:14px;font-weight:700;color:#C04040;"
        )
        grid.addWidget(self.lbl_codigo, 0, 3)

        # Fila 1: Lote afectado y Cliente relacionado (auto)
        grid.addWidget(self._flbl("Lote afectado *"), 1, 0)
        self.combo_lote = QComboBox()
        self.combo_lote.setPlaceholderText("Seleccionar lote...")
        self.combo_lote.currentTextChanged.connect(self._on_lote_cambiado)
        grid.addWidget(self.combo_lote, 1, 1)

        grid.addWidget(self._flbl("Cliente relacionado"), 1, 2)
        self.lbl_cliente = self._auto_lbl()
        grid.addWidget(self.lbl_cliente, 1, 3)

        # Fila 2: Cantidad afectada (auto) y Responsable
        grid.addWidget(self._flbl("Cantidad afectada"), 2, 0)
        self.lbl_cantidad = self._auto_lbl()
        grid.addWidget(self.lbl_cantidad, 2, 1)

        grid.addWidget(self._flbl("Responsable *"), 2, 2)
        self.combo_resp = QComboBox()
        self.combo_resp.setPlaceholderText("Seleccionar...")
        grid.addWidget(self.combo_resp, 2, 3)

        # Fila 3: Origen del aviso y Producto inmovilizado
        grid.addWidget(self._flbl("Origen del aviso *"), 3, 0)
        self.input_origen = QLineEdit()
        self.input_origen.setPlaceholderText("Queja cliente, control interno...")
        grid.addWidget(self.input_origen, 3, 1)

        grid.addWidget(self._flbl("Producto inmovilizado *"), 3, 2)
        self.combo_inmovilizado = QComboBox()
        self.combo_inmovilizado.addItem("Sí")
        self.combo_inmovilizado.addItem("No")
        grid.addWidget(self.combo_inmovilizado, 3, 3)

        # Fila 4: Motivo (ancho completo)
        grid.addWidget(self._flbl("Motivo *"), 4, 0)
        self.input_motivo = QLineEdit()
        self.input_motivo.setPlaceholderText("Descripción del motivo del retiro...")
        grid.addWidget(self.input_motivo, 4, 1, 1, 3)

        # Fila 5: Acción inmediata
        grid.addWidget(self._flbl("Acción inmediata *"), 5, 0)
        self.input_accion = QLineEdit()
        self.input_accion.setPlaceholderText("Acciones tomadas de inmediato...")
        grid.addWidget(self.input_accion, 5, 1, 1, 3)

        # Fila 6: Comunicación realizada y Estado del caso
        grid.addWidget(self._flbl("Comunicación realizada"), 6, 0)
        self.input_comunicacion = QLineEdit()
        self.input_comunicacion.setPlaceholderText("A quién y cómo se comunicó...")
        grid.addWidget(self.input_comunicacion, 6, 1)

        grid.addWidget(self._flbl("Estado del caso"), 6, 2)
        self.combo_estado = QComboBox()
        for e in HongosService.ESTADOS_CASO:
            self.combo_estado.addItem(e)
        grid.addWidget(self.combo_estado, 6, 3)

        # Fila 7: Acción correctiva
        grid.addWidget(self._flbl("Acción correctiva"), 7, 0)
        self.input_correctiva = QLineEdit()
        self.input_correctiva.setPlaceholderText("Plan de acción correctiva a largo plazo...")
        grid.addWidget(self.input_correctiva, 7, 1, 1, 3)

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_row.addWidget(btn_limpiar)
        btn_guardar = QPushButton("Registrar retiro")
        btn_guardar.setObjectName("dangerButton")
        btn_guardar.clicked.connect(self._guardar)
        btn_row.addWidget(btn_guardar)
        layout.addLayout(btn_row)

        return card

    def _build_tabla_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        row_title = QHBoxLayout()
        title = QLabel("Historial de Retiros")
        title.setObjectName("cardTitle")
        self.lbl_count = QLabel("0 registros")
        self.lbl_count.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(self.lbl_count)
        layout.addLayout(row_title)

        self.tabla = TablaRegistros()
        self.tabla.setMinimumHeight(200)
        layout.addWidget(self.tabla)

        return card

    # ─────────────────── HELPERS ────────────────────────────────────

    def _flbl(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lbl

    def _auto_lbl(self) -> QLabel:
        lbl = QLabel("—")
        lbl.setObjectName("autoValue")
        return lbl

    def _poblar_combos(self) -> None:
        if not self._service:
            return

        lotes = self._service.get_lotes_disponibles_para_retiro()
        self.combo_lote.clear()
        if lotes:
            self.combo_lote.addItem("")
            self.combo_lote.setEnabled(True)
            for lote in lotes:
                self.combo_lote.addItem(lote)
        else:
            self.combo_lote.addItem("Sin lotes disponibles para retiro")
            self.combo_lote.setEnabled(False)

        self.combo_resp.clear()
        self.combo_resp.addItem("")
        for r in self._service.RESPONSABLES:
            self.combo_resp.addItem(r)

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _recalcular_codigo(self) -> None:
        if not self._service:
            return
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        self.lbl_codigo.setText(self._service.generar_codigo_retiro(d))

    def _on_lote_cambiado(self, lote: str) -> None:
        if not self._service or not lote:
            self.lbl_cliente.setText("—")
            self.lbl_cantidad.setText("—")
            return
        exp = self._service.get_expedicion_by_lote(lote)
        if exp:
            self.lbl_cliente.setText(str(exp.get("Cliente", "") or "—"))
            self.lbl_cantidad.setText(str(exp.get("Cantidad", "") or "—"))
        else:
            self.lbl_cliente.setText("—")
            self.lbl_cantidad.setText("—")

    # ─────────────────── GUARDAR ────────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            return
        lote = self.combo_lote.currentText().strip()
        if not lote or not self.combo_lote.isEnabled():
            QMessageBox.warning(self, "Campo requerido",
                "Selecciona el lote afectado.\n\n"
                "Asegúrate de registrar primero una Expedición con condición 'Aceptada'.")
            return
        origen = self.input_origen.text().strip()
        if not origen:
            QMessageBox.warning(self, "Campo requerido", "Ingresa el origen del aviso.")
            return
        motivo = self.input_motivo.text().strip()
        if not motivo:
            QMessageBox.warning(self, "Campo requerido", "Ingresa el motivo del retiro.")
            return
        responsable = self.combo_resp.currentText().strip()
        if not responsable:
            QMessageBox.warning(self, "Campo requerido", "Selecciona el responsable.")
            return
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        codigo = self._service.generar_codigo_retiro(d)
        cantidad_txt = self.lbl_cantidad.text().replace("—", "")
        try:
            cantidad = float(cantidad_txt) if cantidad_txt else None
        except ValueError:
            cantidad = None
        datos = {
            "fecha_deteccion":        d,
            "codigo_retiro":          codigo,
            "lote_afectado":          lote,
            "origen_aviso":           origen,
            "cliente_relacionado":    self.lbl_cliente.text().replace("—", ""),
            "cantidad_afectada":      cantidad,
            "motivo":                 motivo,
            "accion_inmediata":       self.input_accion.text().strip(),
            "producto_inmovilizado":  self.combo_inmovilizado.currentText(),
            "comunicacion_realizada": self.input_comunicacion.text().strip(),
            "responsable":            responsable,
            "estado_caso":            self.combo_estado.currentText(),
            "accion_correctiva":      self.input_correctiva.text().strip(),
        }
        try:
            self._service.guardar_retiro(datos)
            QMessageBox.information(
                self, "Retiro registrado",
                f"Código: {codigo}\nLote afectado: {lote}"
            )
            self.limpiar()
            self.cargar()
            DataEventBus.instance().datos_actualizados.emit()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def limpiar(self) -> None:
        self._poblar_combos()
        self.fecha_edit.setDate(QDate.currentDate())
        self.combo_lote.setCurrentIndex(0)
        self.lbl_cliente.setText("—")
        self.lbl_cantidad.setText("—")
        self.combo_resp.setCurrentIndex(0)
        self.input_origen.clear()
        self.combo_inmovilizado.setCurrentIndex(0)
        self.input_motivo.clear()
        self.input_accion.clear()
        self.input_comunicacion.clear()
        self.combo_estado.setCurrentIndex(0)
        self.input_correctiva.clear()
        self._recalcular_codigo()

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_retiros_df()
        self.tabla.cargar_dataframe(df)
        self.lbl_count.setText(f"{len(df)} registro(s)")
