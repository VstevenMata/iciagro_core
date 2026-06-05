from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.components.drop_zone import DropZoneWidget
from gui.pages.proveedores_page          import ProveedoresPage
from gui.pages.evaluacion_page           import EvaluacionPage
from gui.pages.clientes_page             import ClientesPage
from gui.pages.recepcion_page            import RecepcionPage
from gui.pages.produccion_page           import ProduccionPage
from gui.pages.producto_terminado_page   import ProductoTerminadoPage
from gui.pages.expedicion_page           import ExpedicionPage
from gui.pages.retiro_page               import RetiroPage
from gui.pages.etiquetas_page            import EtiquetasPage
from gui.pages.reporte_page              import ReportePage
from services.hongos_service             import HongosService


# Índices del QStackedWidget
_IDX = {
    "carga":             0,
    "proveedores":       1,
    "evaluacion":        2,
    "clientes":          3,
    "recepcion":         4,
    "produccion":        5,
    "terminado":         6,
    "expedicion":        7,
    "retiro":            8,
    "etiquetas":         9,
    "reporte":          10,
}


class MainWindow(QMainWindow):
    """
    Ventana principal del sistema ICIAGRO CORE — Hongos del Páramo.
    Sidebar de navegación + QStackedWidget con los 9 módulos de trazabilidad.
    """

    _SETTINGS_ORG  = "ICIAGRO"
    _SETTINGS_APP  = "IciagrocCore"
    _KEY_EXCEL     = "ultima_ruta_excel"

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ICIAGRO CORE — Sistema de Trazabilidad Hongos del Páramo")
        self.setMinimumSize(1280, 780)
        self._service: Optional[HongosService] = None
        self._nav_btn: dict[str, QPushButton] = {}
        self._settings = QSettings(self._SETTINGS_ORG, self._SETTINGS_APP)

        self._setup_ui()
        self._auto_cargar_excel()

    # ─────────────────── ESTRUCTURA GENERAL ─────────────────────────

    def _setup_ui(self) -> None:
        central = QWidget()
        central.setObjectName("mainWindow")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")

        # ── Páginas ──────────────────────────────────────────────────
        self.page_carga        = self._build_carga_page()
        self.page_proveedores  = ProveedoresPage()
        self.page_evaluacion   = EvaluacionPage()
        self.page_clientes     = ClientesPage()
        self.page_recepcion    = RecepcionPage()
        self.page_produccion   = ProduccionPage()
        self.page_terminado    = ProductoTerminadoPage()
        self.page_expedicion   = ExpedicionPage()
        self.page_retiro       = RetiroPage()
        self.page_etiquetas    = EtiquetasPage()
        self.page_reporte      = ReportePage()

        for page in (
            self.page_carga,         # 0
            self.page_proveedores,   # 1
            self.page_evaluacion,    # 2
            self.page_clientes,      # 3
            self.page_recepcion,     # 4
            self.page_produccion,    # 5
            self.page_terminado,     # 6
            self.page_expedicion,    # 7
            self.page_retiro,        # 8
            self.page_etiquetas,     # 9
            self.page_reporte,       # 10
        ):
            self.stack.addWidget(page)

        body.addWidget(self.stack, 1)

        body_widget = QWidget()
        body_widget.setLayout(body)
        root.addWidget(body_widget, 1)
        root.addWidget(self._build_footer())

    # ─────────────────── HEADER ─────────────────────────────────────

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("appHeader")
        header.setFixedHeight(54)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        tag = QLabel("ICIAGRO CORE")
        tag.setStyleSheet(
            "background:#3F6B4B;border:1px solid #4F7D5C;"
            "border-radius:6px;padding:3px 10px;font-size:11px;"
            "font-weight:700;color:#FFF;"
        )

        title = QLabel("Sistema de Trazabilidad — Hongos del Páramo")
        title.setObjectName("headerTitle")

        layout.addWidget(tag)
        layout.addWidget(title)
        layout.addStretch()

        self.lbl_archivo = QLabel("Sin archivo cargado")
        self.lbl_archivo.setObjectName("headerSubtitle")
        layout.addWidget(self.lbl_archivo)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep)

        sub = QLabel("Universidad Nacional de Costa Rica · Sede Brunca · 2026")
        sub.setObjectName("headerSubtitle")
        layout.addWidget(sub)

        return header

    # ─────────────────── SIDEBAR ────────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(3)

        brand = QLabel("ICIAGRO")
        brand.setObjectName("sidebarTitle")
        brand.setAlignment(Qt.AlignCenter)
        ver = QLabel("v2.0 · Hongos del Páramo")
        ver.setObjectName("sidebarVersion")
        ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(brand)
        layout.addWidget(ver)
        layout.addSpacing(12)

        sep0 = QFrame()
        sep0.setFrameShape(QFrame.HLine)
        sep0.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep0)
        layout.addSpacing(8)

        # ── INICIO ───────────────────────────────────────────────────
        self._section_label("INICIO", layout)
        self._add_nav(layout, "carga", "Cargar archivo")

        layout.addSpacing(6)
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep1)
        layout.addSpacing(6)

        # ── PROVEEDORES ──────────────────────────────────────────────
        self._section_label("PROVEEDORES", layout)
        self._add_nav(layout, "proveedores", "Gestión Proveedores")
        self._add_nav(layout, "evaluacion",  "Evaluación Proveedores")

        layout.addSpacing(6)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep2)
        layout.addSpacing(6)

        # ── CLIENTES ─────────────────────────────────────────────────
        self._section_label("CLIENTES", layout)
        self._add_nav(layout, "clientes", "Gestión Clientes")

        layout.addSpacing(6)
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep3)
        layout.addSpacing(6)

        # ── TRAZABILIDAD ─────────────────────────────────────────────
        self._section_label("TRAZABILIDAD", layout)
        self._add_nav(layout, "recepcion",  "Recepción MP")
        self._add_nav(layout, "produccion", "Producción Interna")
        self._add_nav(layout, "terminado",  "Producto Terminado")
        self._add_nav(layout, "expedicion", "Expedición y Ventas")
        self._add_nav(layout, "retiro",     "Retiro de Producto")

        layout.addSpacing(6)
        sep4 = QFrame()
        sep4.setFrameShape(QFrame.HLine)
        sep4.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep4)
        layout.addSpacing(6)

        # ── HERRAMIENTAS ─────────────────────────────────────────────
        self._section_label("HERRAMIENTAS", layout)
        self._add_nav(layout, "etiquetas", "Etiquetas")
        self._add_nav(layout, "reporte",   "Reportes / Exportar")

        layout.addStretch()

        sep5 = QFrame()
        sep5.setFrameShape(QFrame.HLine)
        sep5.setStyleSheet("color:#1E293B;")
        layout.addWidget(sep5)
        layout.addSpacing(6)

        integ = QLabel("Integrantes")
        integ.setObjectName("sidebarVersion")
        integ.setAlignment(Qt.AlignCenter)
        layout.addWidget(integ)
        for nombre in ("Anthony Mata Quirós", "Camila Gómez Sequeira"):
            lbl = QLabel(f"· {nombre}")
            lbl.setObjectName("sidebarVersion")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)

        return sidebar

    def _section_label(self, texto: str, layout: QVBoxLayout) -> None:
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "font-size:9px;color:#334155;font-weight:700;"
            "letter-spacing:2px;padding:0 8px;"
        )
        layout.addWidget(lbl)
        layout.addSpacing(2)

    def _add_nav(self, layout: QVBoxLayout, key: str, label: str) -> None:
        btn = QPushButton(f"  {label}")
        btn.setObjectName("navButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(34)
        btn.clicked.connect(lambda checked=False, k=key: self._ir_a(k))
        layout.addWidget(btn)
        self._nav_btn[key] = btn

    # ─────────────────── PÁGINA DE CARGA ────────────────────────────

    def _build_carga_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageContainer")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Cargar archivo de trazabilidad")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Carga el archivo Excel del sistema de trazabilidad de Hongos del Páramo "
            "(.xlsx) para comenzar a trabajar con los módulos."
        )
        sub.setObjectName("pageSubtitle")
        sub.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(sub)

        self.drop_zone = DropZoneWidget()
        self.drop_zone.setMinimumHeight(180)
        self.drop_zone.archivo_cargado.connect(self._cargar_excel)
        layout.addWidget(self.drop_zone)

        info = QFrame()
        info.setObjectName("card")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)

        info_title = QLabel("Archivo esperado")
        info_title.setObjectName("cardTitle")
        info_layout.addWidget(info_title)

        bullets = [
            "Archivo Excel (.xlsx o .xlsm) del sistema de trazabilidad Hongos del Páramo",
            "Debe contener las hojas: Proveedores, Evaluacion_Proveedores, Clientes, Recepcion_MP,",
            "  Produccion_Interna, Producto_Terminado, Expedicion_Ventas, Retiro_Producto, Etiquetas",
            "Nombre sugerido: 'sistema de trazabilidad hongos en páramo 2.0.xlsx'",
        ]
        for b in bullets:
            lbl = QLabel(f"  ·  {b}")
            lbl.setObjectName("pageSubtitle")
            info_layout.addWidget(lbl)

        layout.addWidget(info)
        layout.addStretch()
        return page

    # ─────────────────── FOOTER ─────────────────────────────────────

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(32)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)

        left = QLabel("ICIAGRO CORE · Sistema de Trazabilidad de Hongos del Páramo")
        left.setObjectName("footerText")
        right = QLabel("Universidad Nacional de Costa Rica · Sede Brunca · 2026")
        right.setObjectName("footerText")
        right.setAlignment(Qt.AlignRight)

        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(right)
        return footer

    # ─────────────────── NAVEGACIÓN ─────────────────────────────────

    def _ir_a(self, key: str) -> None:
        for k, btn in self._nav_btn.items():
            btn.setObjectName("navButtonActive" if k == key else "navButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if key != "carga" and self._service is None:
            QMessageBox.information(
                self,
                "Archivo requerido",
                "Debes cargar el archivo Excel primero.\n\nVe a 'Cargar archivo'.",
            )
            self._ir_a("carga")
            return

        idx = _IDX.get(key, 0)
        self.stack.setCurrentIndex(idx)

    # ─────────────────── CARGA DEL EXCEL ────────────────────────────

    def _auto_cargar_excel(self) -> None:
        """Al iniciar, carga el último Excel usado si sigue existiendo."""
        ruta = self._settings.value(self._KEY_EXCEL, "")
        if ruta and os.path.isfile(ruta):
            self._cargar_excel(ruta, silencioso=True)
        else:
            self._ir_a("carga")

    def _cargar_excel(self, ruta: str, silencioso: bool = False) -> None:
        try:
            service = HongosService(ruta)
            self._service = service

            # Persistir la ruta para la próxima sesión
            self._settings.setValue(self._KEY_EXCEL, ruta)

            # Inyectar servicio en todas las páginas
            self.page_proveedores.set_service(service)
            self.page_evaluacion.set_service(service)
            self.page_clientes.set_service(service)
            self.page_recepcion.set_service(service)
            self.page_produccion.set_service(service)
            self.page_terminado.set_service(service)
            self.page_expedicion.set_service(service)
            self.page_retiro.set_service(service)
            self.page_etiquetas.set_service(service)
            self.page_reporte.set_service(service)

            nombre = ruta.replace("\\", "/").split("/")[-1]
            self.lbl_archivo.setText(f"{nombre}  ·  Hongos del Páramo")

            if not silencioso:
                n_prov = len(service.get_proveedores_df())
                n_cli  = len(service.get_clientes_df())
                n_prod = len(service.get_producciones_df())
                QMessageBox.information(
                    self,
                    "Archivo cargado",
                    f"Archivo cargado correctamente.\n\n"
                    f"Proveedores: {n_prov}\n"
                    f"Clientes: {n_cli}\n"
                    f"Lotes de producción: {n_prod}",
                )

            self._ir_a("proveedores")

        except Exception as ex:
            QMessageBox.critical(
                self,
                "Error al cargar",
                f"No se pudo cargar el archivo.\n\nError: {ex}",
            )
            self._service = None
            self._ir_a("carga")
