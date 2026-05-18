from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.components.tabla_registros import TablaRegistros
from models.proveedor import Proveedor
from services.excel_service import ExcelService


class CatalogoPage(QWidget):
    """Vista del catálogo de proveedores con búsqueda en tiempo real."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pageContainer")
        self._service: Optional[ExcelService] = None
        self._proveedores: list[Proveedor] = []
        self._setup_ui()

    def set_service(self, service: ExcelService) -> None:
        self._service = service
        self.cargar_catalogo()

    # ─────────────────── UI ─────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # Header
        header = QVBoxLayout()
        title = QLabel("Catálogo de Proveedores")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Proveedores cargados desde el archivo Excel de trazabilidad.")
        subtitle.setObjectName("pageSubtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Controles
        controls = QHBoxLayout()
        controls.setSpacing(12)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por código, nombre o producto...")
        self.input_buscar.textChanged.connect(self._filtrar)
        controls.addWidget(self.input_buscar, 1)

        self.lbl_total = QLabel("0 proveedores")
        self.lbl_total.setObjectName("statusBadge")
        controls.addWidget(self.lbl_total)

        self.btn_reload = QPushButton("Actualizar")
        self.btn_reload.setObjectName("secondaryButton")
        self.btn_reload.clicked.connect(self.cargar_catalogo)
        controls.addWidget(self.btn_reload)

        layout.addLayout(controls)

        # Tabla
        self.tabla = TablaRegistros()
        layout.addWidget(self.tabla)

        # Detalle del proveedor seleccionado
        layout.addWidget(self._build_detalle_card())

        self.tabla.fila_seleccionada.connect(self._mostrar_detalle)

    def _build_detalle_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        self._detalle_layout = QVBoxLayout(card)
        self._detalle_layout.setContentsMargins(16, 12, 16, 12)
        self._detalle_layout.setSpacing(8)

        title = QLabel("Detalle del proveedor seleccionado")
        title.setObjectName("cardSubtitle")
        self._detalle_layout.addWidget(title)

        self._detalle_labels: dict[str, QLabel] = {}
        grid = QHBoxLayout()

        campos = [
            ("Código", "codigo_proveedor"),
            ("Nombre", "nombre"),
            ("Código MP", "codigo_mp"),
            ("Vida útil", "vida_util"),
            ("Almacenamiento", "condiciones_almacenamiento"),
        ]
        for titulo, clave in campos:
            col = QVBoxLayout()
            col.setSpacing(2)
            lbl_t = QLabel(titulo)
            lbl_t.setObjectName("fieldLabel")
            lbl_v = QLabel("—")
            lbl_v.setObjectName("autoValue")
            lbl_v.setWordWrap(True)
            col.addWidget(lbl_t)
            col.addWidget(lbl_v)
            grid.addLayout(col)
            self._detalle_labels[clave] = lbl_v

        self._detalle_layout.addLayout(grid)
        card.setFixedHeight(110)
        return card

    # ─────────────────── LÓGICA ─────────────────────────────────

    def cargar_catalogo(self) -> None:
        if not self._service:
            return
        self._proveedores = self._service.get_proveedores()
        self._render_tabla(self._proveedores)

    def _filtrar(self, texto: str) -> None:
        if not texto:
            self._render_tabla(self._proveedores)
            return
        texto = texto.lower()
        filtrados = [
            p for p in self._proveedores
            if (
                texto in p.codigo_proveedor.lower()
                or texto in p.nombre.lower()
                or texto in p.producto_abastece.lower()
                or texto in p.codigo_mp.lower()
            )
        ]
        self._render_tabla(filtrados)

    def _render_tabla(self, proveedores: list[Proveedor]) -> None:
        headers = Proveedor.headers()
        filas = [p.to_row() for p in proveedores]
        self.tabla.cargar_lista(headers, filas)
        n = len(proveedores)
        self.lbl_total.setText(f"{n} proveedor{'es' if n != 1 else ''}")

    def _mostrar_detalle(self, row_idx: int) -> None:
        texto_busq = self.input_buscar.text().lower()
        fuente = [
            p for p in self._proveedores
            if not texto_busq or (
                texto_busq in p.codigo_proveedor.lower()
                or texto_busq in p.nombre.lower()
            )
        ] if texto_busq else self._proveedores

        if row_idx < 0 or row_idx >= len(fuente):
            return
        p = fuente[row_idx]
        self._detalle_labels["codigo_proveedor"].setText(p.codigo_proveedor)
        self._detalle_labels["nombre"].setText(p.nombre)
        self._detalle_labels["codigo_mp"].setText(p.codigo_mp)
        self._detalle_labels["vida_util"].setText(p.vida_util)
        self._detalle_labels["condiciones_almacenamiento"].setText(
            p.condiciones_almacenamiento
        )
