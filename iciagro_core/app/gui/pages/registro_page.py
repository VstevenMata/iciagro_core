from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import Qt, QDate, Signal
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
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.registro_mp import RegistroMP
from services.excel_service import ExcelService


class RegistroPage(QWidget):
    """
    Formulario de registro de materia prima.
    Requiere que se le inyecte un ExcelService con set_service().
    """

    registro_guardado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[ExcelService] = None
        self._setup_ui()

    def set_service(self, service: ExcelService) -> None:
        self._service = service
        self._poblar_combos()

    # ─────────────────── UI ─────────────────────────────────────

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)

        # Encabezado
        header = self._build_header()
        main_layout.addLayout(header)

        # Scroll area para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        form_widget = QWidget()
        form_widget.setObjectName("pageContainer")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 8, 0)

        # Card de campos manuales
        form_layout.addWidget(self._build_card_manual())

        # Card de campos automáticos
        form_layout.addWidget(self._build_card_auto())

        # Card de trazabilidad generada
        form_layout.addWidget(self._build_card_trazabilidad())

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)

        # Botones de acción
        main_layout.addLayout(self._build_actions())

    def _build_header(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(4)
        title = QLabel("Registro de Materia Prima")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Complete los campos requeridos. Los campos marcados con * son obligatorios.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return layout

    def _build_card_manual(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Datos de Recepción")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Fecha
        grid.addWidget(self._lbl("Fecha de recepción *"), 0, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.dateChanged.connect(self._on_campos_cambiados)
        grid.addWidget(self.fecha_edit, 0, 1)

        # Código proveedor
        grid.addWidget(self._lbl("Código proveedor *"), 0, 2)
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.setPlaceholderText("Seleccionar proveedor...")
        self.combo_proveedor.currentTextChanged.connect(self._on_proveedor_cambiado)
        grid.addWidget(self.combo_proveedor, 0, 3)

        # Cantidad de sacos
        grid.addWidget(self._lbl("Cantidad de sacos *"), 1, 0)
        self.spin_sacos = QSpinBox()
        self.spin_sacos.setRange(1, 99999)
        self.spin_sacos.setValue(1)
        grid.addWidget(self.spin_sacos, 1, 1)

        # Lote proveedor
        grid.addWidget(self._lbl("Lote proveedor"), 1, 2)
        self.input_lote = QLineEdit()
        self.input_lote.setPlaceholderText("Ej: A202025")
        self.input_lote.textChanged.connect(self._on_campos_cambiados)
        grid.addWidget(self.input_lote, 1, 3)

        # Responsable
        grid.addWidget(self._lbl("Responsable recepción *"), 2, 0)
        self.combo_responsable = QComboBox()
        self.combo_responsable.setPlaceholderText("Seleccionar responsable...")
        grid.addWidget(self.combo_responsable, 2, 1)

        # Observaciones
        grid.addWidget(self._lbl("Observaciones"), 2, 2)
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones de la recepción...")
        grid.addWidget(self.input_obs, 2, 3)

        layout.addLayout(grid)
        return card

    def _build_card_auto(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        title_row = QHBoxLayout()
        title = QLabel("Datos Autocompletados")
        title.setObjectName("cardTitle")
        badge = QLabel("Desde catálogo de proveedores")
        badge.setObjectName("statusBadge")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(badge)
        layout.addLayout(title_row)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        grid.addWidget(self._lbl("Nombre del proveedor"), 0, 0)
        self.lbl_nombre = self._auto_lbl()
        grid.addWidget(self.lbl_nombre, 0, 1)

        grid.addWidget(self._lbl("Materia prima"), 0, 2)
        self.lbl_mp = self._auto_lbl()
        grid.addWidget(self.lbl_mp, 0, 3)

        grid.addWidget(self._lbl("Código MP"), 1, 0)
        self.lbl_codigo_mp = self._auto_lbl()
        grid.addWidget(self.lbl_codigo_mp, 1, 1)

        grid.addWidget(self._lbl("Vida útil"), 1, 2)
        self.lbl_vida_util = self._auto_lbl()
        grid.addWidget(self.lbl_vida_util, 1, 3)

        grid.addWidget(self._lbl("Condiciones de almacenamiento"), 2, 0)
        self.lbl_almacenamiento = self._auto_lbl()
        self.lbl_almacenamiento.setWordWrap(True)
        grid.addWidget(self.lbl_almacenamiento, 2, 1, 1, 3)

        grid.addWidget(self._lbl("Producto / presentación"), 3, 0)
        self.lbl_prod_pres = self._auto_lbl()
        self.lbl_prod_pres.setWordWrap(True)
        grid.addWidget(self.lbl_prod_pres, 3, 1, 1, 3)

        layout.addLayout(grid)
        return card

    def _build_card_trazabilidad(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        title_row = QHBoxLayout()
        title = QLabel("Código de Trazabilidad")
        title.setObjectName("cardTitle")
        badge = QLabel("Generado automáticamente")
        badge.setObjectName("statusBadge")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(badge)
        layout.addLayout(title_row)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        grid.addWidget(self._lbl("Código de trazabilidad"), 0, 0)
        self.lbl_trazabilidad = self._auto_lbl()
        self.lbl_trazabilidad.setStyleSheet(
            "background-color: #061A10; border: 1px solid #059669; border-radius: 8px;"
            " padding: 7px 12px; font-size: 14px; color: #10B981; font-weight: 800;"
        )
        grid.addWidget(self.lbl_trazabilidad, 0, 1)

        grid.addWidget(self._lbl("Secuencia del día"), 0, 2)
        self.lbl_secuencia = self._auto_lbl()
        grid.addWidget(self.lbl_secuencia, 0, 3)

        grid.addWidget(self._lbl("Revisión lote proveedor"), 1, 0)
        self.lbl_revision = self._auto_lbl()
        grid.addWidget(self.lbl_revision, 1, 1)

        layout.addLayout(grid)
        return card

    def _build_actions(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.addStretch()

        self.btn_limpiar = QPushButton("Limpiar formulario")
        self.btn_limpiar.setObjectName("secondaryButton")
        self.btn_limpiar.clicked.connect(self.limpiar)
        layout.addWidget(self.btn_limpiar)

        self.btn_guardar = QPushButton("Guardar registro")
        self.btn_guardar.setObjectName("primaryButton")
        self.btn_guardar.clicked.connect(self._guardar)
        layout.addWidget(self.btn_guardar)

        return layout

    # ─────────────────── HELPERS ────────────────────────────────

    def _lbl(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lbl

    def _auto_lbl(self) -> QLabel:
        lbl = QLabel("—")
        lbl.setObjectName("autoValue")
        return lbl

    # ─────────────────── COMBOS ─────────────────────────────────

    def _poblar_combos(self) -> None:
        if not self._service:
            return
        self.combo_proveedor.clear()
        self.combo_proveedor.addItem("")
        for cod in self._service.get_codigos_proveedor():
            self.combo_proveedor.addItem(cod)
        self.combo_responsable.clear()
        self.combo_responsable.addItem("")
        for resp in self._service.responsables:
            self.combo_responsable.addItem(resp)

    # ─────────────────── EVENTOS ────────────────────────────────

    def _on_proveedor_cambiado(self, codigo: str) -> None:
        if not self._service or not codigo:
            self._limpiar_auto()
            return
        datos = self._service.autocompletar_proveedor(codigo)
        self.lbl_nombre.setText(datos.get("nombre_proveedor", "—") or "—")
        self.lbl_mp.setText(datos.get("materia_prima", "—") or "—")
        self.lbl_codigo_mp.setText(datos.get("codigo_mp", "—") or "—")
        self.lbl_vida_util.setText(datos.get("vida_util", "—") or "—")
        self.lbl_almacenamiento.setText(datos.get("almacenamiento", "—") or "—")
        self.lbl_prod_pres.setText(datos.get("producto_presentacion", "—") or "—")
        self._recalcular_trazabilidad()

    def _on_campos_cambiados(self) -> None:
        self._recalcular_trazabilidad()

    def _recalcular_trazabilidad(self) -> None:
        if not self._service:
            return
        codigo_mp = self.lbl_codigo_mp.text()
        codigo_prov = self.combo_proveedor.currentText()
        if not codigo_mp or codigo_mp == "—" or not codigo_prov:
            self.lbl_trazabilidad.setText("—")
            self.lbl_secuencia.setText("—")
            self.lbl_revision.setText("—")
            return

        qdate = self.fecha_edit.date()
        fecha = date(qdate.year(), qdate.month(), qdate.day())
        secuencia = self._service.calcular_secuencia(fecha, codigo_mp)
        lote = self.input_lote.text().strip()
        revision = self._service.revisar_lote(codigo_prov, lote) if lote else "—"
        codigo = self._service.generar_codigo_trazabilidad(
            fecha, codigo_prov, codigo_mp, secuencia
        )
        self.lbl_trazabilidad.setText(codigo)
        self.lbl_secuencia.setText(str(secuencia))
        self.lbl_revision.setText(revision)

    def _limpiar_auto(self) -> None:
        for lbl in (
            self.lbl_nombre, self.lbl_mp, self.lbl_codigo_mp,
            self.lbl_vida_util, self.lbl_almacenamiento, self.lbl_prod_pres,
            self.lbl_trazabilidad, self.lbl_secuencia, self.lbl_revision,
        ):
            lbl.setText("—")

    # ─────────────────── GUARDAR ────────────────────────────────

    def _guardar(self) -> None:
        if not self._service:
            QMessageBox.warning(self, "Sin datos", "Carga un archivo Excel primero.")
            return

        codigo_prov = self.combo_proveedor.currentText().strip()
        responsable = self.combo_responsable.currentText().strip()

        if not codigo_prov:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un proveedor.")
            return
        if not responsable:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un responsable.")
            return

        codigo_mp = self.lbl_codigo_mp.text()
        if not codigo_mp or codigo_mp == "—":
            QMessageBox.warning(self, "Sin código MP", "El proveedor no tiene Código MP.")
            return

        qdate = self.fecha_edit.date()
        fecha = date(qdate.year(), qdate.month(), qdate.day())
        lote = self.input_lote.text().strip()
        secuencia = self._service.calcular_secuencia(fecha, codigo_mp)
        codigo_trazabilidad = self._service.generar_codigo_trazabilidad(
            fecha, codigo_prov, codigo_mp, secuencia
        )
        revision = self._service.revisar_lote(codigo_prov, lote) if lote else ""

        registro = RegistroMP(
            fecha_recepcion=fecha,
            codigo_proveedor=codigo_prov,
            nombre_proveedor=self.lbl_nombre.text().replace("—", ""),
            materia_prima=self.lbl_mp.text().replace("—", ""),
            cantidad_sacos=self.spin_sacos.value(),
            lote_proveedor=lote,
            observaciones=self.input_obs.text().strip(),
            responsable=responsable,
            vida_util=self.lbl_vida_util.text().replace("—", ""),
            almacenamiento=self.lbl_almacenamiento.text().replace("—", ""),
            codigo_mp=codigo_mp,
            secuencia_dia=secuencia,
            codigo_trazabilidad=codigo_trazabilidad,
            revision_lote=revision,
            producto_presentacion=self.lbl_prod_pres.text().replace("—", ""),
        )

        try:
            self._service.guardar_registro(registro)
            QMessageBox.information(
                self,
                "Registro guardado",
                f"El registro fue guardado exitosamente.\n\nCódigo: {codigo_trazabilidad}",
            )
            self.limpiar()
            self.registro_guardado.emit()
        except Exception as ex:
            QMessageBox.critical(self, "Error al guardar", str(ex))

    def limpiar(self) -> None:
        self.fecha_edit.setDate(QDate.currentDate())
        self.combo_proveedor.setCurrentIndex(0)
        self.spin_sacos.setValue(1)
        self.input_lote.clear()
        self.combo_responsable.setCurrentIndex(0)
        self.input_obs.clear()
        self._limpiar_auto()
