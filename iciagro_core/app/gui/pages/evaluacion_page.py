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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from gui.event_bus import DataEventBus
from services.hongos_service import HongosService


class EvaluacionPage(QWidget):
    """Registro y consulta de evaluaciones de proveedores."""

    CRITERIOS = [
        ("Entrega a tiempo",   "entrega_tiempo",       20),
        ("Calidad",            "calidad",               25),
        ("Cantidad correcta",  "cantidad_correcta",     15),
        ("Condición entrega",  "condicion_entrega",     15),
        ("Comunicación",       "comunicacion",          15),
        ("Identificación/lote","identificacion_lote",   10),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._spins: dict[str, QSpinBox] = {}
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self._poblar_combos()
        self.cargar()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._service:
            self._poblar_combos()
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
        title = QLabel("Evaluación de Proveedores")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Registra la evaluación de desempeño. "
            "El total y clasificación se calculan automáticamente."
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
        title = QLabel("Nueva Evaluación")
        title.setObjectName("cardTitle")
        badge = QLabel("Campos automáticos marcados con icono")
        badge.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(badge)
        layout.addLayout(row_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fecha
        grid.addWidget(self._flbl("Fecha evaluación"), 0, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        grid.addWidget(self.fecha_edit, 0, 1)

        # Código proveedor
        grid.addWidget(self._flbl("Código proveedor *"), 0, 2)
        self.combo_prov = QComboBox()
        self.combo_prov.setPlaceholderText("Seleccionar...")
        self.combo_prov.currentTextChanged.connect(self._on_proveedor_cambiado)
        grid.addWidget(self.combo_prov, 0, 3)

        # Nombre (auto)
        grid.addWidget(self._flbl("Nombre proveedor"), 1, 0)
        self.lbl_nombre = self._auto_lbl()
        grid.addWidget(self.lbl_nombre, 1, 1)

        # Producto (auto)
        grid.addWidget(self._flbl("Producto abastecido"), 1, 2)
        self.lbl_producto = self._auto_lbl()
        grid.addWidget(self.lbl_producto, 1, 3)

        layout.addLayout(grid)

        # Criterios de evaluación
        layout.addWidget(self._build_criterios_section())

        # Resultado auto
        result_row = QHBoxLayout()
        result_row.setSpacing(20)

        col_total = QVBoxLayout()
        col_total.addWidget(self._flbl("Total (0–100)"))
        self.lbl_total = QLabel("0")
        self.lbl_total.setObjectName("autoValue")
        self.lbl_total.setStyleSheet(
            "background:#061A10;border:1px solid #059669;border-radius:8px;"
            "padding:8px 14px;font-size:22px;font-weight:800;color:#10B981;"
        )
        self.lbl_total.setAlignment(Qt.AlignCenter)
        col_total.addWidget(self.lbl_total)
        result_row.addLayout(col_total)

        col_clasif = QVBoxLayout()
        col_clasif.addWidget(self._flbl("Clasificación"))
        self.lbl_clasif = QLabel("—")
        self.lbl_clasif.setObjectName("badgeNeutral")
        self.lbl_clasif.setAlignment(Qt.AlignCenter)
        col_clasif.addWidget(self.lbl_clasif)
        result_row.addLayout(col_clasif)

        col_obs = QVBoxLayout()
        col_obs.addWidget(self._flbl("Observaciones"))
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones opcionales...")
        col_obs.addWidget(self.input_obs)
        result_row.addLayout(col_obs, 2)

        layout.addLayout(result_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_row.addWidget(btn_limpiar)
        btn_guardar = QPushButton("Guardar evaluación")
        btn_guardar.setObjectName("primaryButton")
        btn_guardar.clicked.connect(self._guardar)
        btn_row.addWidget(btn_guardar)
        layout.addLayout(btn_row)

        return card

    def _build_criterios_section(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setStyleSheet(
            "QFrame#card{background:#0A1525;border:1px solid #1A3050;border-radius:8px;}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        lbl = QLabel("Criterios de evaluación")
        lbl.setObjectName("cardTitle")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        for i, (nombre, key, maximo) in enumerate(self.CRITERIOS):
            col = (i % 2) * 2
            row = i // 2
            lbl_c = self._flbl(f"{nombre}  (máx {maximo})")
            lbl_c.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            grid.addWidget(lbl_c, row, col)
            spin = QSpinBox()
            spin.setRange(0, maximo)
            spin.setValue(0)
            spin.valueChanged.connect(self._recalcular)
            self._spins[key] = spin
            grid.addWidget(spin, row, col + 1)

        layout.addLayout(grid)
        return frame

    def _build_tabla_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        row_title = QHBoxLayout()
        title = QLabel("Historial de Evaluaciones")
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

    # ─────────────────── EVENTOS ────────────────────────────────────

    def _on_proveedor_cambiado(self, codigo: str) -> None:
        if not self._service or not codigo:
            self.lbl_nombre.setText("—")
            self.lbl_producto.setText("—")
            return
        datos = self._service.autocompletar_proveedor(codigo)
        self.lbl_nombre.setText(datos.get("nombre", "—") or "—")
        self.lbl_producto.setText(datos.get("producto", "—") or "—")

    def _recalcular(self) -> None:
        total = sum(spin.value() for spin in self._spins.values())
        self.lbl_total.setText(str(total))
        clasif = HongosService.clasificar(total)
        self.lbl_clasif.setText(clasif)
        colores = {
            "Excelente":      ("#052E16", "#16A34A", "#4ADE80"),
            "Aceptable":      ("#1A2E05", "#65A30D", "#A3E635"),
            "Condicionado":   ("#1A1100", "#D97706", "#FCD34D"),
            "No recomendado": ("#1A0505", "#DC2626", "#F87171"),
        }
        bg, brd, fg = colores.get(clasif, ("#0A1525", "#1A3050", "#475569"))
        self.lbl_clasif.setStyleSheet(
            f"background:{bg};border:1px solid {brd};border-radius:7px;"
            f"padding:5px 14px;font-size:13px;font-weight:700;color:{fg};"
        )

    # ─────────────────── GUARDAR ────────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            return
        codigo = self.combo_prov.currentText().strip()
        if not codigo:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un proveedor.")
            return
        qd = self.fecha_edit.date()
        datos = {
            "fecha":               date(qd.year(), qd.month(), qd.day()),
            "codigo_proveedor":    codigo,
            "proveedor":           self.lbl_nombre.text().replace("—", ""),
            "producto_abastecido": self.lbl_producto.text().replace("—", ""),
            "observaciones":       self.input_obs.text().strip(),
        }
        for key, spin in self._spins.items():
            datos[key] = spin.value()
        try:
            self._service.guardar_evaluacion(datos)
            total = int(self.lbl_total.text())
            clasif = HongosService.clasificar(total)
            QMessageBox.information(
                self, "Evaluación guardada",
                f"Proveedor: {codigo}\nTotal: {total}  →  {clasif}"
            )
            self.limpiar()
            self.cargar()
            DataEventBus.instance().datos_actualizados.emit()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def limpiar(self) -> None:
        self.fecha_edit.setDate(QDate.currentDate())
        self.combo_prov.setCurrentIndex(0)
        self.lbl_nombre.setText("—")
        self.lbl_producto.setText("—")
        for spin in self._spins.values():
            spin.setValue(0)
        self.input_obs.clear()
        self.lbl_total.setText("0")
        self.lbl_clasif.setText("—")

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_evaluaciones_df()
        self.tabla.cargar_dataframe(df)
        self.lbl_count.setText(f"{len(df)} registro(s)")
