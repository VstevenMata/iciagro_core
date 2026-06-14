from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from services.hongos_service import HongosService
from utils.date_utils import dia_juliano


class RecepcionPage(QWidget):
    """Recepción de materia prima e insumos."""

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
        title = QLabel("Recepción de Materia Prima")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Registra el ingreso de materia prima. "
            "El código de recepción se genera automáticamente si el estado es Aceptado."
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
        title = QLabel("Nueva Recepción")
        title.setObjectName("cardTitle")
        badge = QLabel("Automático")
        badge.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(badge)
        layout.addLayout(row_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fila 0: Fecha y Día juliano
        grid.addWidget(self._flbl("Fecha recepción *"), 0, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.dateChanged.connect(self._on_fecha_cambiada)
        grid.addWidget(self.fecha_edit, 0, 1)

        grid.addWidget(self._flbl("Día juliano"), 0, 2)
        self.lbl_juliano = self._auto_lbl()
        grid.addWidget(self.lbl_juliano, 0, 3)

        # Fila 1: Proveedor y Materia prima
        grid.addWidget(self._flbl("Proveedor *"), 1, 0)
        self.combo_prov = QComboBox()
        self.combo_prov.setPlaceholderText("Seleccionar proveedor...")
        self.combo_prov.currentTextChanged.connect(self._on_proveedor_cambiado)
        grid.addWidget(self.combo_prov, 1, 1)

        grid.addWidget(self._flbl("Materia prima"), 1, 2)
        self.combo_mp = QComboBox()
        self.combo_mp.setEnabled(False)
        grid.addWidget(self.combo_mp, 1, 3)

        # Fila 2: Cantidad, Unidad
        grid.addWidget(self._flbl("Cantidad recibida *"), 2, 0)
        self.spin_cantidad = QDoubleSpinBox()
        self.spin_cantidad.setRange(0, 999999)
        self.spin_cantidad.setDecimals(2)
        self.spin_cantidad.setValue(1)
        grid.addWidget(self.spin_cantidad, 2, 1)

        grid.addWidget(self._flbl("Unidad *"), 2, 2)
        self.input_unidad = QLineEdit()
        self.input_unidad.setPlaceholderText("kg, unidades, bolsas...")
        grid.addWidget(self.input_unidad, 2, 3)

        # Fila 3: Estado y Responsable
        grid.addWidget(self._flbl("Estado *"), 3, 0)
        self.combo_estado = QComboBox()
        for e in HongosService.ESTADOS:
            self.combo_estado.addItem(e)
        self.combo_estado.currentTextChanged.connect(self._on_estado_cambiado)
        grid.addWidget(self.combo_estado, 3, 1)

        grid.addWidget(self._flbl("Responsable *"), 3, 2)
        self.combo_resp = QComboBox()
        self.combo_resp.setPlaceholderText("Seleccionar...")
        grid.addWidget(self.combo_resp, 3, 3)

        # Fila 4: Código recepción (auto) y Observaciones
        grid.addWidget(self._flbl("Código recepción"), 4, 0)
        self.lbl_codigo = self._auto_lbl()
        self.lbl_codigo.setStyleSheet(
            "background:#061A10;border:1px solid #059669;border-radius:8px;"
            "padding:7px 12px;font-size:14px;font-weight:800;color:#10B981;"
        )
        grid.addWidget(self.lbl_codigo, 4, 1)

        grid.addWidget(self._flbl("Observaciones"), 4, 2)
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones opcionales...")
        grid.addWidget(self.input_obs, 4, 3)

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_row.addWidget(btn_limpiar)
        btn_guardar = QPushButton("Guardar recepción")
        btn_guardar.setObjectName("primaryButton")
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
        title = QLabel("Historial de Recepciones")
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
        self.combo_prov.clear()
        self.combo_prov.addItem("")
        for cod in self._service.get_codigos_proveedor():
            self.combo_prov.addItem(cod)
        self.combo_resp.clear()
        self.combo_resp.addItem("")
        for r in self._service.RESPONSABLES:
            self.combo_resp.addItem(r)

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _on_fecha_cambiada(self) -> None:
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        self.lbl_juliano.setText(str(dia_juliano(d)).zfill(3))
        self._recalcular_codigo()

    def _on_proveedor_cambiado(self, codigo: str) -> None:
        if not self._service or not codigo:
            self.combo_mp.clear()
            self.combo_mp.setEnabled(False)
            return
        datos = self._service.autocompletar_proveedor(codigo)
        producto = datos.get("producto", "")
        self.combo_mp.clear()
        if codigo == "PROV-001":
            # Abastece múltiples: mostrar selector
            for mp in self._service.MATERIAS_PRIMAS_PROV001:
                self.combo_mp.addItem(mp)
            self.combo_mp.setEnabled(True)
        else:
            self.combo_mp.addItem(producto)
            self.combo_mp.setEnabled(False)
        self._recalcular_codigo()

    def _on_estado_cambiado(self, estado: str) -> None:
        self._recalcular_codigo()

    def _recalcular_codigo(self) -> None:
        if not self._service:
            return
        estado = self.combo_estado.currentText()
        if estado != "Aceptado":
            self.lbl_codigo.setText("Sin código (Rechazado)")
            return
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        codigo = self._service.generar_codigo_recepcion(d)
        self.lbl_codigo.setText(codigo)

    # ─────────────────── GUARDAR ────────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            return
        proveedor = self.combo_prov.currentText().strip()
        if not proveedor:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un proveedor.")
            return
        mp = self.combo_mp.currentText().strip()
        if not mp:
            QMessageBox.warning(self, "Campo requerido", "Selecciona la materia prima.")
            return
        responsable = self.combo_resp.currentText().strip()
        if not responsable:
            QMessageBox.warning(self, "Campo requerido", "Selecciona el responsable.")
            return
        unidad = self.input_unidad.text().strip()
        if not unidad:
            QMessageBox.warning(self, "Campo requerido", "Ingresa la unidad.")
            return
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        estado = self.combo_estado.currentText()
        codigo = self._service.generar_codigo_recepcion(d) if estado == "Aceptado" else ""
        datos = {
            "fecha":            d,
            "proveedor":        proveedor,
            "materia_prima":    mp,
            "cantidad":         self.spin_cantidad.value(),
            "unidad":           unidad,
            "estado":           estado,
            "responsable":      responsable,
            "observaciones":    self.input_obs.text().strip(),
            "codigo_recepcion": codigo,
        }
        try:
            self._service.guardar_recepcion(datos)
            msg = f"Recepción guardada.\nCódigo: {codigo}" if codigo else "Recepción guardada (estado: Rechazado)."
            QMessageBox.information(self, "Guardado", msg)
            self.limpiar()
            self.cargar()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def limpiar(self) -> None:
        self.fecha_edit.setDate(QDate.currentDate())
        self.combo_prov.setCurrentIndex(0)
        self.combo_mp.clear()
        self.combo_mp.setEnabled(False)
        self.spin_cantidad.setValue(1)
        self.input_unidad.clear()
        self.combo_estado.setCurrentIndex(0)
        self.combo_resp.setCurrentIndex(0)
        self.input_obs.clear()
        self._recalcular_codigo()
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        self.lbl_juliano.setText(str(dia_juliano(d)).zfill(3))

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_recepciones_df()
        self.tabla.cargar_dataframe(df)
        self.lbl_count.setText(f"{len(df)} registro(s)")
