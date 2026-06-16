from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.event_bus import DataEventBus

from gui.components.tabla_registros import TablaRegistros
from services.hongos_service import HongosService


class ClientesPage(QWidget):
    """Gestión de clientes: visualización y edición de campos operativos."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._cliente_sel: Optional[str] = None
        self._setup_ui()

    def set_service(self, service: HongosService) -> None:
        self._service = service
        self.cargar()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._service:
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

        inner = QWidget()
        inner.setObjectName("pageContainer")
        vl = QVBoxLayout(inner)
        vl.setSpacing(16)
        vl.setContentsMargins(0, 0, 8, 0)
        vl.addLayout(self._build_busqueda())
        vl.addWidget(self.tabla, 1)
        vl.addWidget(self._build_detalle_card())
        vl.addStretch()

        scroll.setWidget(inner)
        main.addWidget(scroll, 1)

    def _build_header(self) -> QVBoxLayout:
        vl = QVBoxLayout()
        vl.setSpacing(4)
        title = QLabel("Gestión de Clientes")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Información operativa de clientes. "
            "Selecciona un cliente para editar sus datos."
        )
        sub.setObjectName("pageSubtitle")
        sub.setWordWrap(True)
        vl.addWidget(title)
        vl.addWidget(sub)
        return vl

    def _build_busqueda(self) -> QHBoxLayout:
        hl = QHBoxLayout()
        hl.setSpacing(12)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por código, nombre o tipo...")
        self.input_buscar.textChanged.connect(self._filtrar)
        hl.addWidget(self.input_buscar, 1)

        self.lbl_total = QLabel("0 clientes")
        self.lbl_total.setObjectName("statusBadge")
        hl.addWidget(self.lbl_total)

        btn_reload = QPushButton("Actualizar")
        btn_reload.setObjectName("secondaryButton")
        btn_reload.clicked.connect(self.cargar)
        hl.addWidget(btn_reload)

        self.tabla = TablaRegistros()
        self.tabla.setMinimumHeight(200)
        self.tabla.fila_seleccionada.connect(self._on_fila_seleccionada)

        return hl

    def _build_detalle_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(14)

        row_title = QHBoxLayout()
        title = QLabel("Detalle del cliente seleccionado")
        title.setObjectName("cardTitle")
        hint = QLabel("Haz clic en una fila de la tabla para editar")
        hint.setObjectName("pageSubtitle")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(hint)
        layout.addLayout(row_title)

        # Fila de lectura: Código y Nombre
        id_row = QHBoxLayout()
        id_row.setSpacing(24)

        col_cod = QVBoxLayout()
        col_cod.addWidget(self._flbl("Código cliente"))
        self.lbl_sel = QLabel("—")
        self.lbl_sel.setStyleSheet(
            "background:#061A10;border:1px solid #059669;border-radius:7px;"
            "padding:6px 14px;font-size:13px;font-weight:700;color:#10B981;"
        )
        col_cod.addWidget(self.lbl_sel)
        id_row.addLayout(col_cod)

        col_nom = QVBoxLayout()
        col_nom.addWidget(self._flbl("Nombre cliente"))
        self.lbl_nombre = self._auto_lbl()
        col_nom.addWidget(self.lbl_nombre)
        id_row.addLayout(col_nom, 1)
        layout.addLayout(id_row)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1A3050;")
        layout.addWidget(sep)

        # Campos editables en grid 2x2
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Tipo (selector)
        col_tipo = QVBoxLayout()
        col_tipo.setSpacing(4)
        col_tipo.addWidget(self._flbl("Tipo de cliente"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("")
        for t in HongosService.TIPOS_CLIENTE:
            self.combo_tipo.addItem(t)
        col_tipo.addWidget(self.combo_tipo)
        grid.addLayout(col_tipo, 0, 0)

        # Contacto
        col_con = QVBoxLayout()
        col_con.setSpacing(4)
        col_con.addWidget(self._flbl("Contacto  (editable)"))
        self.input_contacto = QLineEdit()
        self.input_contacto.setPlaceholderText("Teléfono o correo...")
        col_con.addWidget(self.input_contacto)
        grid.addLayout(col_con, 0, 1)

        # Punto de entrega
        col_pe = QVBoxLayout()
        col_pe.setSpacing(4)
        col_pe.addWidget(self._flbl("Punto de entrega  (editable)"))
        self.input_punto = QLineEdit()
        self.input_punto.setPlaceholderText("Lugar de entrega...")
        col_pe.addWidget(self.input_punto)
        grid.addLayout(col_pe, 1, 0)

        # Observaciones
        col_obs = QVBoxLayout()
        col_obs.setSpacing(4)
        col_obs.addWidget(self._flbl("Observaciones  (editable)"))
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones...")
        col_obs.addWidget(self.input_obs)
        grid.addLayout(col_obs, 1, 1)

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_guardar = QPushButton("Guardar cambios")
        self.btn_guardar.setObjectName("primaryButton")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self._guardar_cambios)
        btn_row.addWidget(self.btn_guardar)
        layout.addLayout(btn_row)

        return card

    # ─────────────────── HELPERS ────────────────────────────────────

    def _flbl(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _auto_lbl(self) -> QLabel:
        lbl = QLabel("—")
        lbl.setObjectName("autoValue")
        return lbl

    # ─────────────────── LÓGICA ─────────────────────────────────────

    def cargar(self) -> None:
        if not self._service:
            return
        df = self._service.get_clientes_df()
        self.tabla.cargar_dataframe(df)
        n = len(df)
        self.lbl_total.setText(f"{n} cliente{'s' if n != 1 else ''}")
        # Populate combo if service was injected after init
        if self.combo_tipo.count() <= 1:
            for t in self._service.TIPOS_CLIENTE:
                self.combo_tipo.addItem(t)

    def _filtrar(self, texto: str) -> None:
        if not self._service:
            return
        df = self._service.get_clientes_df()
        if texto:
            t = texto.lower()
            mask = df.apply(lambda row: any(t in str(v).lower() for v in row), axis=1)
            df = df[mask]
        self.tabla.cargar_dataframe(df)
        self.lbl_total.setText(f"{len(df)} resultado(s)")

    def _on_fila_seleccionada(self, row_idx: int) -> None:
        if not self._service:
            return
        df = self._service.get_clientes_df()
        texto = self.input_buscar.text().lower()
        if texto:
            mask = df.apply(lambda r: any(texto in str(v).lower() for v in r), axis=1)
            df = df[mask]
        if row_idx < 0 or row_idx >= len(df):
            return
        row = df.iloc[row_idx]
        # _val sanitiza NaN -> "" para evitar que se guarde el string "nan"
        codigo = self._service._val(row.get("Código cliente"))
        self._cliente_sel = codigo
        self.lbl_sel.setText(codigo if codigo else "—")
        self.lbl_nombre.setText(self._service._val(row.get("Nombre cliente")) or "—")
        tipo = self._service._val(row.get("Tipo de cliente"))
        idx = self.combo_tipo.findText(tipo)
        self.combo_tipo.setCurrentIndex(idx if idx >= 0 else 0)
        self.input_contacto.setText(self._service._val(row.get("Contacto")))
        self.input_punto.setText(self._service._val(row.get("Punto de entrega")))
        self.input_obs.setText(self._service._val(row.get("Observaciones")))
        self.btn_guardar.setEnabled(bool(codigo))

    def _guardar_cambios(self) -> None:
        if not self._service or not self._cliente_sel:
            QMessageBox.warning(
                self, "Sin selección",
                "Selecciona un cliente de la tabla antes de guardar."
            )
            return
        try:
            self._service.actualizar_cliente(
                self._cliente_sel, "Tipo de cliente", self.combo_tipo.currentText()
            )
            self._service.actualizar_cliente(
                self._cliente_sel, "Contacto", self.input_contacto.text().strip()
            )
            self._service.actualizar_cliente(
                self._cliente_sel, "Punto de entrega", self.input_punto.text().strip()
            )
            self._service.actualizar_cliente(
                self._cliente_sel, "Observaciones", self.input_obs.text().strip()
            )
            QMessageBox.information(
                self, "Guardado", f"Cliente {self._cliente_sel} actualizado."
            )
            self.cargar()
            DataEventBus.instance().datos_actualizados.emit()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))
