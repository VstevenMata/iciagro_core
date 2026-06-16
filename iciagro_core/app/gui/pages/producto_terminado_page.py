from __future__ import annotations

import re
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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from services.hongos_service import HongosService
from utils.date_utils import formatear_fecha


class ProductoTerminadoPage(QWidget):
    """Registro de empaque y cierre de producción (Producto Terminado)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self._poblar_lotes()
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
        title = QLabel("Producto Terminado")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Registra el empaque de producción. "
            "Selecciona un lote HP para autocompletar los datos de producción."
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
        title = QLabel("Nuevo Registro de Empaque")
        title.setObjectName("cardTitle")
        badge = QLabel("Autocompletado desde Producción Interna")
        badge.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(badge)
        layout.addLayout(row_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fila 0: Lote interno (selector)
        grid.addWidget(self._flbl("Lote interno (HP) *"), 0, 0)
        self.combo_lote = QComboBox()
        self.combo_lote.setPlaceholderText("Seleccionar lote disponible...")
        self.combo_lote.currentTextChanged.connect(self._on_lote_cambiado)
        grid.addWidget(self.combo_lote, 0, 1)

        grid.addWidget(self._flbl("Código producto"), 0, 2)
        self.lbl_cod_prod = self._auto_lbl()
        grid.addWidget(self.lbl_cod_prod, 0, 3)

        # Fila 1: Producto y Fecha producción (auto)
        grid.addWidget(self._flbl("Producto"), 1, 0)
        self.lbl_producto = self._auto_lbl()
        grid.addWidget(self.lbl_producto, 1, 1)

        grid.addWidget(self._flbl("Fecha producción"), 1, 2)
        self.lbl_fecha_prod = self._auto_lbl()
        grid.addWidget(self.lbl_fecha_prod, 1, 3)

        # Fila 2: Responsable producción y Kg sustrato (auto)
        grid.addWidget(self._flbl("Resp. producción"), 2, 0)
        self.lbl_resp_prod = self._auto_lbl()
        grid.addWidget(self.lbl_resp_prod, 2, 1)

        grid.addWidget(self._flbl("Sustrato / Micelio"), 2, 2)
        self.lbl_sustrato = self._auto_lbl()
        grid.addWidget(self.lbl_sustrato, 2, 3)

        # Fila 3: Fecha cosecha y Fecha empaque
        grid.addWidget(self._flbl("Fecha cosecha *"), 3, 0)
        self.fecha_cosecha = QDateEdit()
        self.fecha_cosecha.setDate(QDate.currentDate())
        self.fecha_cosecha.setCalendarPopup(True)
        self.fecha_cosecha.setDisplayFormat("dd/MM/yyyy")
        grid.addWidget(self.fecha_cosecha, 3, 1)

        grid.addWidget(self._flbl("Fecha empaque *"), 3, 2)
        self.fecha_empaque = QDateEdit()
        self.fecha_empaque.setDate(QDate.currentDate())
        self.fecha_empaque.setCalendarPopup(True)
        self.fecha_empaque.setDisplayFormat("dd/MM/yyyy")
        grid.addWidget(self.fecha_empaque, 3, 3)

        # Fila 4: Presentación y Cantidad empacada
        grid.addWidget(self._flbl("Presentación (G) *"), 4, 0)
        self.spin_presentacion = QSpinBox()
        self.spin_presentacion.setRange(0, 20000)
        self.spin_presentacion.setValue(0)
        grid.addWidget(self.spin_presentacion, 4, 1)

        grid.addWidget(self._flbl("Cantidad Empacada (Bandejas) *"), 4, 2)
        self.spin_cantidad = QDoubleSpinBox()
        self.spin_cantidad.setRange(0, 999999)
        self.spin_cantidad.setDecimals(2)
        self.spin_cantidad.setValue(1)
        grid.addWidget(self.spin_cantidad, 4, 3)

        # Fila 5: Unidad y Temperatura
        grid.addWidget(self._flbl("Unidad"), 5, 0)
        self.input_unidad = QLineEdit("Bandejas")
        self.input_unidad.setEnabled(False)
        grid.addWidget(self.input_unidad, 5, 1)

        grid.addWidget(self._flbl("Temperatura refrigeración (°C)"), 5, 2)
        self.spin_temp = QDoubleSpinBox()
        self.spin_temp.setRange(-10, 30)
        self.spin_temp.setDecimals(1)
        self.spin_temp.setValue(4)
        grid.addWidget(self.spin_temp, 5, 3)

        # Fila 6: Responsable y Estado
        grid.addWidget(self._flbl("Responsable *"), 6, 0)
        self.combo_resp = QComboBox()
        self.combo_resp.setPlaceholderText("Seleccionar...")
        grid.addWidget(self.combo_resp, 6, 1)

        grid.addWidget(self._flbl("Estado *"), 6, 2)
        self.combo_estado = QComboBox()
        for e in HongosService.ESTADOS:
            self.combo_estado.addItem(e)
        grid.addWidget(self.combo_estado, 6, 3)

        # Fila 7: Observaciones
        grid.addWidget(self._flbl("Observaciones"), 7, 0)
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones opcionales...")
        grid.addWidget(self.input_obs, 7, 1, 1, 3)

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_row.addWidget(btn_limpiar)
        btn_guardar = QPushButton("Guardar producto terminado")
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
        title = QLabel("Historial de Producto Terminado")
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

    def _poblar_lotes(self) -> None:
        if not self._service:
            return
        self.combo_lote.clear()
        self.combo_lote.addItem("")
        for lote in self._service.get_lotes_disponibles_para_terminado():
            self.combo_lote.addItem(lote)
        self.combo_resp.clear()
        self.combo_resp.addItem("")
        for r in self._service.RESPONSABLES:
            self.combo_resp.addItem(r)

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _on_lote_cambiado(self, lote: str) -> None:
        if not self._service or not lote:
            self._limpiar_auto()
            return
        prod = self._service.get_produccion_by_lote(lote)
        if not prod:
            self._limpiar_auto()
            return
        codigo = str(prod.get("Código producto", "") or "")
        self.lbl_cod_prod.setText(codigo)
        self.lbl_producto.setText(self._service.get_nombre_producto(codigo))
        fecha = prod.get("Fecha producción")
        self.lbl_fecha_prod.setText(formatear_fecha(fecha) if fecha else "—")
        self.lbl_resp_prod.setText(str(prod.get("Responsable", "") or "—"))
        kg = prod.get("Kilogramos sustrato", "")
        gm = prod.get("gramos micelio", "")
        self.lbl_sustrato.setText(f"{kg} kg / {gm} g")
        # Auto-fill presentación (g) from product catalogue
        for p in self._service.PRODUCTOS:
            if p["codigo"] == codigo:
                match = re.search(r"\d+", p["presentacion"])
                self.spin_presentacion.setValue(int(match.group()) if match else 0)
                break

    def _limpiar_auto(self) -> None:
        for lbl in (self.lbl_cod_prod, self.lbl_producto, self.lbl_fecha_prod,
                    self.lbl_resp_prod, self.lbl_sustrato):
            lbl.setText("—")

    # ─────────────────── GUARDAR ────────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            return
        lote = self.combo_lote.currentText().strip()
        if not lote:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un lote interno.")
            return
        responsable = self.combo_resp.currentText().strip()
        if not responsable:
            QMessageBox.warning(self, "Campo requerido", "Selecciona el responsable.")
            return
        qd_cos = self.fecha_cosecha.date()
        qd_emp = self.fecha_empaque.date()
        codigo = self.lbl_cod_prod.text().replace("—", "")
        datos = {
            "fecha_cosecha":     date(qd_cos.year(), qd_cos.month(), qd_cos.day()),
            "fecha_empaque":     date(qd_emp.year(), qd_emp.month(), qd_emp.day()),
            "lote_interno":      lote,
            "codigo_producto":   codigo,
            "producto":          self.lbl_producto.text().replace("—", ""),
            "presentacion":      self.spin_presentacion.value(),
            "cantidad_empacada": self.spin_cantidad.value(),
            "unidad":            self.input_unidad.text().strip(),
            "responsable":       responsable,
            "temp_refrigeracion":self.spin_temp.value(),
            "estado":            self.combo_estado.currentText(),
            "observaciones":     self.input_obs.text().strip(),
        }
        try:
            self._service.guardar_terminado(datos)
            QMessageBox.information(
                self, "Guardado",
                f"Producto terminado registrado.\nLote: {lote}\nEstado: {datos['estado']}"
            )
            self.limpiar()
            self.cargar()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def limpiar(self) -> None:
        self._poblar_lotes()
        self.combo_lote.setCurrentIndex(0)
        self.fecha_cosecha.setDate(QDate.currentDate())
        self.fecha_empaque.setDate(QDate.currentDate())
        self.spin_presentacion.setValue(0)
        self.spin_cantidad.setValue(1)
        self.spin_temp.setValue(4)
        self.combo_resp.setCurrentIndex(0)
        self.combo_estado.setCurrentIndex(0)
        self.input_obs.clear()
        self._limpiar_auto()

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_terminados_df()
        self.tabla.cargar_dataframe(df)
        self.lbl_count.setText(f"{len(df)} registro(s)")
