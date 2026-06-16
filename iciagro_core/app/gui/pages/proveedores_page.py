from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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
from gui.event_bus import DataEventBus
from services.hongos_service import HongosService


class ProveedoresPage(QWidget):
    """Gestión de proveedores: visualización y edición de Contacto/Ubicación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[HongosService] = None
        self._proveedor_sel: Optional[str] = None
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
        title = QLabel("Gestión de Proveedores")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Consulta la información de proveedores registrados. "
            "Contacto y Ubicación son editables."
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
        self.input_buscar.setPlaceholderText("Buscar por código, nombre o producto...")
        self.input_buscar.textChanged.connect(self._filtrar)
        hl.addWidget(self.input_buscar, 1)

        self.lbl_total = QLabel("0 proveedores")
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
        title = QLabel("Detalle del proveedor seleccionado")
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
        col_nombre = QVBoxLayout()
        col_nombre.addWidget(self._flbl("Nombre"))
        self.lbl_nombre = self._auto_lbl()
        col_nombre.addWidget(self.lbl_nombre)
        grid.addLayout(col_nombre)

        # Producto (solo lectura)
        col_prod = QVBoxLayout()
        col_prod.addWidget(self._flbl("Producto que abastece"))
        self.lbl_producto = self._auto_lbl()
        self.lbl_producto.setWordWrap(True)
        col_prod.addWidget(self.lbl_producto)
        grid.addLayout(col_prod)

        # Contacto (editable)
        col_contacto = QVBoxLayout()
        col_contacto.addWidget(self._flbl("Contacto *editable"))
        self.input_contacto = QLineEdit()
        self.input_contacto.setPlaceholderText("Teléfono o correo...")
        col_contacto.addWidget(self.input_contacto)
        grid.addLayout(col_contacto)

        # Ubicación (editable)
        col_ubic = QVBoxLayout()
        col_ubic.addWidget(self._flbl("Ubicación *editable"))
        self.input_ubicacion = QLineEdit()
        self.input_ubicacion.setPlaceholderText("Ciudad, Provincia...")
        col_ubic.addWidget(self.input_ubicacion)
        grid.addLayout(col_ubic)

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
        df = self._service.get_proveedores_df()
        self.tabla.cargar_dataframe(df)
        n = len(df)
        self.lbl_total.setText(f"{n} proveedor{'es' if n != 1 else ''}")

    def _filtrar(self, texto: str) -> None:
        if not self._service:
            return
        df = self._service.get_proveedores_df()
        if texto:
            t = texto.lower()
            mask = df.apply(
                lambda row: any(t in str(v).lower() for v in row), axis=1
            )
            df = df[mask]
        self.tabla.cargar_dataframe(df)
        self.lbl_total.setText(f"{len(df)} resultado(s)")

    def _on_fila_seleccionada(self, row_idx: int) -> None:
        if not self._service:
            return
        df = self._service.get_proveedores_df()
        texto = self.input_buscar.text().lower()
        if texto:
            mask = df.apply(lambda r: any(texto in str(v).lower() for v in r), axis=1)
            df = df[mask]
        if row_idx < 0 or row_idx >= len(df):
            return
        row = df.iloc[row_idx]
        codigo = str(row.get("Código proveedor", "") or "")
        self._proveedor_sel = codigo
        self.lbl_sel.setText(codigo)
        self.lbl_nombre.setText(str(row.get("Proveedor", "") or "—"))
        self.lbl_producto.setText(str(row.get("Producto que abastece", "") or "—"))
        self.input_contacto.setText(str(row.get("Contacto", "") or ""))
        self.input_ubicacion.setText(str(row.get("Ubicación", "") or ""))
        self.btn_guardar.setEnabled(True)

    def _guardar_cambios(self) -> None:
        if not self._service or not self._proveedor_sel:
            return
        contacto = self.input_contacto.text().strip()
        ubicacion = self.input_ubicacion.text().strip()
        try:
            self._service.actualizar_proveedor(self._proveedor_sel, "Contacto", contacto)
            self._service.actualizar_proveedor(self._proveedor_sel, "Ubicación", ubicacion)
            QMessageBox.information(
                self, "Guardado", f"Proveedor {self._proveedor_sel} actualizado."
            )
            self.cargar()
            DataEventBus.instance().datos_actualizados.emit()
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))
