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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from services.hongos_service import HongosService
from utils.date_utils import dia_juliano


class ProduccionPage(QWidget):
    """Producción interna: creación y consulta de lotes HP."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self._poblar_combos()
        self._recalcular_lote()
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
        title = QLabel("Producción Interna")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Registra lotes de producción. "
            "El lote interno HP se genera automáticamente con consecutivo por producto."
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
        title = QLabel("Nuevo Lote de Producción")
        title.setObjectName("cardTitle")
        badge = QLabel("Formato: HP-YYDDD-COD-CC")
        badge.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(badge)
        layout.addLayout(row_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fila 0: Fecha producción y Día juliano
        grid.addWidget(self._flbl("Fecha producción *"), 0, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.dateChanged.connect(self._on_fecha_cambiada)
        grid.addWidget(self.fecha_edit, 0, 1)

        grid.addWidget(self._flbl("Día juliano"), 0, 2)
        self.lbl_juliano = self._auto_lbl()
        grid.addWidget(self.lbl_juliano, 0, 3)

        # Fila 1: Código producto y Consecutivo
        grid.addWidget(self._flbl("Código producto *"), 1, 0)
        self.combo_prod = QComboBox()
        for p in HongosService.PRODUCTOS:
            self.combo_prod.addItem(f"{p['codigo']} — {p['nombre']}", p["codigo"])
        self.combo_prod.currentIndexChanged.connect(self._on_producto_cambiado)
        grid.addWidget(self.combo_prod, 1, 1)

        grid.addWidget(self._flbl("Consecutivo"), 1, 2)
        self.lbl_consec = self._auto_lbl()
        grid.addWidget(self.lbl_consec, 1, 3)

        # Fila 2: Lote interno (auto)
        grid.addWidget(self._flbl("Lote interno"), 2, 0)
        self.lbl_lote = self._auto_lbl()
        self.lbl_lote.setStyleSheet(
            "background:#061A10;border:1px solid #059669;border-radius:8px;"
            "padding:7px 12px;font-size:14px;font-weight:800;color:#10B981;"
        )
        grid.addWidget(self.lbl_lote, 2, 1, 1, 3)

        # Fila 3: Kg sustrato y g micelio
        grid.addWidget(self._flbl("Kg de sustrato *"), 3, 0)
        self.spin_sustrato = QDoubleSpinBox()
        self.spin_sustrato.setRange(0, 99999)
        self.spin_sustrato.setDecimals(2)
        self.spin_sustrato.setValue(0)
        grid.addWidget(self.spin_sustrato, 3, 1)

        grid.addWidget(self._flbl("Gramos de micelio *"), 3, 2)
        self.spin_micelio = QDoubleSpinBox()
        self.spin_micelio.setRange(0, 99999)
        self.spin_micelio.setDecimals(2)
        self.spin_micelio.setValue(0)
        grid.addWidget(self.spin_micelio, 3, 3)

        # Fila 4: Temp pasteurización y Tiempo pasteurización
        grid.addWidget(self._flbl("Temp. pasteurización (°C)"), 4, 0)
        self.spin_temp = QDoubleSpinBox()
        self.spin_temp.setRange(0, 200)
        self.spin_temp.setDecimals(1)
        self.spin_temp.setValue(85)
        grid.addWidget(self.spin_temp, 4, 1)

        grid.addWidget(self._flbl("Tiempo pasteurización (min)"), 4, 2)
        self.spin_tiempo_past = QDoubleSpinBox()
        self.spin_tiempo_past.setRange(0, 9999)
        self.spin_tiempo_past.setDecimals(0)
        self.spin_tiempo_past.setValue(60)
        grid.addWidget(self.spin_tiempo_past, 4, 3)

        # Fila 5: Tiempo secado y Responsable
        grid.addWidget(self._flbl("Tiempo de secado (Días)"), 5, 0)
        self.spin_secado = QSpinBox()
        self.spin_secado.setRange(0, 120)
        self.spin_secado.setValue(0)
        grid.addWidget(self.spin_secado, 5, 1)

        grid.addWidget(self._flbl("Responsable *"), 5, 2)
        self.combo_resp = QComboBox()
        self.combo_resp.setPlaceholderText("Seleccionar...")
        grid.addWidget(self.combo_resp, 5, 3)

        # Fila 6: Observaciones
        grid.addWidget(self._flbl("Observaciones"), 6, 0)
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones opcionales...")
        grid.addWidget(self.input_obs, 6, 1, 1, 3)

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_row.addWidget(btn_limpiar)
        btn_guardar = QPushButton("Guardar lote")
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
        title = QLabel("Lotes de Producción Registrados")
        title.setObjectName("cardTitle")
        self.lbl_count = QLabel("0 lotes")
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
        self.combo_resp.clear()
        self.combo_resp.addItem("")
        for r in self._service.RESPONSABLES:
            self.combo_resp.addItem(r)

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _on_fecha_cambiada(self) -> None:
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        self.lbl_juliano.setText(str(dia_juliano(d)).zfill(3))
        self._recalcular_lote()

    def _on_producto_cambiado(self) -> None:
        self._recalcular_lote()

    def _recalcular_lote(self) -> None:
        if not self._service:
            return
        codigo = self.combo_prod.currentData() or ""
        if not codigo:
            return
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        lote = self._service.generar_lote_interno(d, codigo)
        consec = self._service.get_consecutivo_producto(codigo)
        self.lbl_lote.setText(lote)
        self.lbl_consec.setText(str(consec).zfill(2))

    # ─────────────────── GUARDAR ────────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            return
        responsable = self.combo_resp.currentText().strip()
        if not responsable:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un responsable.")
            return
        codigo = self.combo_prod.currentData() or ""
        qd = self.fecha_edit.date()
        d = date(qd.year(), qd.month(), qd.day())
        lote = self._service.generar_lote_interno(d, codigo)
        datos = {
            "fecha":               d,
            "codigo_producto":     codigo,
            "lote_interno":        lote,
            "kg_sustrato":         self.spin_sustrato.value(),
            "g_micelio":           self.spin_micelio.value(),
            "responsable":         responsable,
            "temp_pasteurizacion": self.spin_temp.value(),
            "tiempo_pasteurizacion": int(self.spin_tiempo_past.value()),
            "tiempo_secado":       self.spin_secado.value(),
            "observaciones":       self.input_obs.text().strip(),
        }
        try:
            self._service.guardar_produccion(datos)
            QMessageBox.information(
                self, "Lote guardado", f"Lote interno generado: {lote}"
            )
            self.limpiar()
            self.cargar()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def limpiar(self) -> None:
        self.fecha_edit.setDate(QDate.currentDate())
        self.combo_prod.setCurrentIndex(0)
        self.spin_sustrato.setValue(0)
        self.spin_micelio.setValue(0)
        self.spin_temp.setValue(85)
        self.spin_tiempo_past.setValue(60)
        self.spin_secado.setValue(0)
        self.combo_resp.setCurrentIndex(0)
        self.input_obs.clear()
        self._recalcular_lote()

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_producciones_df()
        self.tabla.cargar_dataframe(df)
        self.lbl_count.setText(f"{len(df)} lote(s)")
