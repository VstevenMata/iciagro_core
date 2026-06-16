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


class ExpedicionPage(QWidget):
    """Expedición y ventas de producto terminado."""

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
        """Refresca lotes y clientes cada vez que el usuario navega a esta página."""
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
        title = QLabel("Expedición y Ventas")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Registra despachos de producto terminado. "
            "Solo se muestran lotes con estado Aceptado."
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
        title = QLabel("Nueva Expedición")
        title.setObjectName("cardTitle")
        badge = QLabel("Solo lotes Aceptados disponibles")
        badge.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(badge)
        layout.addLayout(row_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fila 0: Fecha salida y Código expedición
        grid.addWidget(self._flbl("Fecha salida *"), 0, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.dateChanged.connect(self._recalcular_codigo)
        grid.addWidget(self.fecha_edit, 0, 1)

        grid.addWidget(self._flbl("Código expedición"), 0, 2)
        self.lbl_codigo = self._auto_lbl()
        self.lbl_codigo.setStyleSheet(
            "background:#061A10;border:1px solid #059669;border-radius:8px;"
            "padding:7px 12px;font-size:14px;font-weight:800;color:#10B981;"
        )
        grid.addWidget(self.lbl_codigo, 0, 3)

        # Fila 1: Cliente y Tipo cliente
        grid.addWidget(self._flbl("Cliente *"), 1, 0)
        self.combo_cliente = QComboBox()
        self.combo_cliente.setPlaceholderText("Seleccionar cliente...")
        self.combo_cliente.currentTextChanged.connect(self._on_cliente_cambiado)
        grid.addWidget(self.combo_cliente, 1, 1)

        grid.addWidget(self._flbl("Tipo de cliente"), 1, 2)
        self.lbl_tipo = self._auto_lbl()
        grid.addWidget(self.lbl_tipo, 1, 3)

        # Fila 2: Producto y Lote vendido
        grid.addWidget(self._flbl("Producto *"), 2, 0)
        self.combo_prod = QComboBox()
        for p in HongosService.PRODUCTOS:
            self.combo_prod.addItem(f"{p['codigo']} — {p['nombre']}", p["codigo"])
        grid.addWidget(self.combo_prod, 2, 1)

        grid.addWidget(self._flbl("Lote vendido *"), 2, 2)
        self.combo_lote = QComboBox()
        self.combo_lote.setPlaceholderText("Seleccionar lote Aceptado...")
        grid.addWidget(self.combo_lote, 2, 3)

        # Fila 3: Cantidad, Unidad
        grid.addWidget(self._flbl("Cantidad *"), 3, 0)
        self.spin_cantidad = QDoubleSpinBox()
        self.spin_cantidad.setRange(0, 999999)
        self.spin_cantidad.setDecimals(2)
        self.spin_cantidad.setValue(1)
        grid.addWidget(self.spin_cantidad, 3, 1)

        grid.addWidget(self._flbl("Unidad *"), 3, 2)
        self.combo_unidad = QComboBox()
        self.combo_unidad.setPlaceholderText("Seleccionar...")
        self.combo_unidad.addItem("")
        self.combo_unidad.addItem("Bandejas")
        self.combo_unidad.addItem("KG")
        grid.addWidget(self.combo_unidad, 3, 3)

        # Fila 4: Destino y Responsable
        grid.addWidget(self._flbl("Destino *"), 4, 0)
        self.input_destino = QLineEdit()
        self.input_destino.setPlaceholderText("Lugar de entrega...")
        self.input_destino.setMaxLength(25)
        grid.addWidget(self.input_destino, 4, 1)

        grid.addWidget(self._flbl("Responsable *"), 4, 2)
        self.combo_resp = QComboBox()
        self.combo_resp.setPlaceholderText("Seleccionar...")
        grid.addWidget(self.combo_resp, 4, 3)

        # Fila 5: Condición entrega y Observaciones
        grid.addWidget(self._flbl("Condición entrega *"), 5, 0)
        self.combo_condicion = QComboBox()
        for e in HongosService.ESTADOS:
            self.combo_condicion.addItem(e)
        grid.addWidget(self.combo_condicion, 5, 1)

        grid.addWidget(self._flbl("Observaciones"), 5, 2)
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones opcionales...")
        grid.addWidget(self.input_obs, 5, 3)

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_row.addWidget(btn_limpiar)
        btn_guardar = QPushButton("Registrar expedición")
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
        title = QLabel("Historial de Expediciones")
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

        # Clientes: mostrar "Nombre  (código)" para que el usuario sepa qué seleccionar
        self.combo_cliente.clear()
        self.combo_cliente.addItem("", "")
        for cod in self._service.get_codigos_cliente():
            datos = self._service.autocompletar_cliente(cod)
            nombre = datos.get("nombre", "")
            display = f"{nombre}  ({cod})" if nombre else cod
            self.combo_cliente.addItem(display, cod)

        # Lotes: solo lotes de Producto Terminado con Estado=Aceptado
        lotes = self._service.get_lotes_aceptados_terminado()
        self.combo_lote.clear()
        if lotes:
            self.combo_lote.addItem("", "")
            self.combo_lote.setEnabled(True)
            for lote in lotes:
                self.combo_lote.addItem(lote)
        else:
            self.combo_lote.addItem("Sin lotes aceptados disponibles")
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
        self.lbl_codigo.setText(self._service.generar_codigo_expedicion(d))

    def _on_cliente_cambiado(self, _: str) -> None:
        codigo = self.combo_cliente.currentData() or ""
        if not self._service or not codigo:
            self.lbl_tipo.setText("—")
            return
        datos = self._service.autocompletar_cliente(codigo)
        self.lbl_tipo.setText(datos.get("tipo", "—") or "—")

    # ─────────────────── GUARDAR ────────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            return
        cliente = self.combo_cliente.currentData() or ""
        if not cliente:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un cliente.")
            return
        lote = self.combo_lote.currentText().strip()
        if not lote or not self.combo_lote.isEnabled():
            QMessageBox.warning(self, "Campo requerido",
                "Selecciona un lote vendido.\n\n"
                "Asegúrate de registrar primero un Producto Terminado con estado 'Aceptado'.")
            return
        responsable = self.combo_resp.currentText().strip()
        if not responsable:
            QMessageBox.warning(self, "Campo requerido", "Selecciona el responsable.")
            return
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        codigo = self._service.generar_codigo_expedicion(d)
        datos = {
            "fecha_salida":       d,
            "codigo_expedicion":  codigo,
            "cliente":            cliente,  # ya es el código limpio desde currentData()
            "tipo_cliente":       self.lbl_tipo.text().replace("—", ""),
            "producto":           self.combo_prod.currentData() or "",
            "lote_vendido":       lote,
            "cantidad":           self.spin_cantidad.value(),
            "unidad":             self.combo_unidad.currentText().strip(),
            "destino":            self.input_destino.text().strip(),
            "responsable":        responsable,
            "condicion_entrega":  self.combo_condicion.currentText(),
            "observaciones":      self.input_obs.text().strip(),
        }
        try:
            self._service.guardar_expedicion(datos)
            QMessageBox.information(
                self, "Expedición registrada",
                f"Código: {codigo}\nCliente: {cliente}\nLote: {lote}"
            )
            self.limpiar()
            self.cargar()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def limpiar(self) -> None:
        self._poblar_combos()
        self.fecha_edit.setDate(QDate.currentDate())
        self.combo_cliente.setCurrentIndex(0)
        self.lbl_tipo.setText("—")
        self.combo_prod.setCurrentIndex(0)
        self.combo_lote.setCurrentIndex(0)
        self.spin_cantidad.setValue(1)
        self.combo_unidad.setCurrentIndex(0)
        self.input_destino.clear()
        self.combo_resp.setCurrentIndex(0)
        self.combo_condicion.setCurrentIndex(0)
        self.input_obs.clear()
        self._recalcular_codigo()

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_expediciones_df()
        self.tabla.cargar_dataframe(df)
        self.lbl_count.setText(f"{len(df)} registro(s)")
