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
    QVBoxLayout,
    QWidget,
)

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

    # ───────────────────────── UI ───────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)
        layout.addLayout(self._build_header())
        layout.addLayout(self._build_busqueda())
        layout.addWidget(self.tabla)
        layout.addWidget(self._build_detalle_card())

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
        self.tabla.fila_seleccionada.connect(self._on_fila_seleccionada)

        return hl

    def _build_detalle_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        row_title = QHBoxLayout()
        title = QLabel("Detalle del cliente seleccionado")
        title.setObjectName("cardTitle")
        self.lbl_sel = QLabel("Ninguno seleccionado")
        self.lbl_sel.setObjectName("statusBadge")
        row_title.addWidget(title)
        row_title.addStretch()
        row_title.addWidget(self.lbl_sel)
        layout.addLayout(row_title)

        grid = QHBoxLayout()
        grid.setSpacing(20)

        # Nombre (solo lectura)
        col_nom = QVBoxLayout()
        col_nom.addWidget(self._flbl("Nombre"))
        self.lbl_nombre = self._auto_lbl()
        col_nom.addWidget(self.lbl_nombre)
        grid.addLayout(col_nom)

        # Tipo (selector)
        col_tipo = QVBoxLayout()
        col_tipo.addWidget(self._flbl("Tipo de cliente"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("")
        if self._service:
            for t in HongosService.TIPOS_CLIENTE:
                self.combo_tipo.addItem(t)
        else:
            for t in ["Restaurante", "Feria", "Cliente directo"]:
                self.combo_tipo.addItem(t)
        col_tipo.addWidget(self.combo_tipo)
        grid.addLayout(col_tipo)

        # Contacto (editable)
        col_con = QVBoxLayout()
        col_con.addWidget(self._flbl("Contacto *editable"))
        self.input_contacto = QLineEdit()
        self.input_contacto.setPlaceholderText("Teléfono o correo...")
        col_con.addWidget(self.input_contacto)
        grid.addLayout(col_con)

        # Punto de entrega (editable)
        col_pe = QVBoxLayout()
        col_pe.addWidget(self._flbl("Punto de entrega *editable"))
        self.input_punto = QLineEdit()
        self.input_punto.setPlaceholderText("Lugar de entrega...")
        col_pe.addWidget(self.input_punto)
        grid.addLayout(col_pe)

        # Observaciones (editable)
        col_obs = QVBoxLayout()
        col_obs.addWidget(self._flbl("Observaciones *editable"))
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Observaciones...")
        col_obs.addWidget(self.input_obs)
        grid.addLayout(col_obs)

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
        codigo = str(row.get("Código cliente", "") or "")
        self._cliente_sel = codigo
        self.lbl_sel.setText(codigo)
        self.lbl_nombre.setText(str(row.get("Nombre cliente", "") or "—"))
        tipo = str(row.get("Tipo de cliente", "") or "")
        idx = self.combo_tipo.findText(tipo)
        self.combo_tipo.setCurrentIndex(idx if idx >= 0 else 0)
        self.input_contacto.setText(str(row.get("Contacto", "") or ""))
        self.input_punto.setText(str(row.get("Punto de entrega", "") or ""))
        self.input_obs.setText(str(row.get("Observaciones", "") or ""))
        self.btn_guardar.setEnabled(True)

    def _guardar_cambios(self) -> None:
        if not self._service or not self._cliente_sel:
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
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))
