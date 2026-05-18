from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
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
from gui.pages.registro_page import RegistroPage
from gui.pages.catalogo_page import CatalogoPage
from gui.pages.reporte_page import ReportePage
from services.excel_service import ExcelService


class MainWindow(QMainWindow):
    """
    Ventana principal del sistema ICIAGRO CORE.
    Contiene sidebar de navegación + área de contenido con páginas.
    El archivo Excel se carga mediante drag & drop o selector de archivo.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ICIAGRO CORE — Sistema de Gestión y Automatización")
        self.setMinimumSize(1200, 720)
        self._service: Optional[ExcelService] = None

        self._setup_ui()
        self._nav_buttons: dict[str, QPushButton] = {}
        self._setup_nav()
        self._ir_a("carga")

    # ─────────────────── ESTRUCTURA ─────────────────────────────

    def _setup_ui(self) -> None:
        central = QWidget()
        central.setObjectName("mainWindow")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        root.addWidget(self._build_header())

        # Body: sidebar + content
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = self._build_sidebar()
        body.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")

        # Páginas
        self.page_carga = self._build_carga_page()
        self.page_registro = RegistroPage()
        self.page_catalogo = CatalogoPage()
        self.page_reporte = ReportePage()

        # Conectar señal de guardado para refrescar reportes
        self.page_registro.registro_guardado.connect(self._on_registro_guardado)

        self.stack.addWidget(self.page_carga)      # 0
        self.stack.addWidget(self.page_registro)   # 1
        self.stack.addWidget(self.page_catalogo)   # 2
        self.stack.addWidget(self.page_reporte)    # 3

        body.addWidget(self.stack, 1)
        body_widget = QWidget()
        body_widget.setLayout(body)
        root.addWidget(body_widget, 1)

        # Footer
        root.addWidget(self._build_footer())

    # ─────────────────── HEADER ─────────────────────────────────

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("appHeader")
        header.setFixedHeight(54)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Logo / título
        tag = QLabel("ICIAGRO CORE")
        tag.setObjectName("statusBadge")
        tag.setStyleSheet(
            "background-color: #3F6B4B; border: 1px solid #4F7D5C;"
            " border-radius: 6px; padding: 3px 10px; font-size: 11px;"
            " font-weight: 700; color: #FFFFFF;"
        )

        title = QLabel("Sistema de Gestión y Automatización Empresarial")
        title.setObjectName("headerTitle")

        layout.addWidget(tag)
        layout.addWidget(title)
        layout.addStretch()

        self.lbl_archivo = QLabel("Sin archivo cargado")
        self.lbl_archivo.setObjectName("headerSubtitle")
        layout.addWidget(self.lbl_archivo)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #1E293B;")
        layout.addWidget(sep)

        subtitle = QLabel("Ingeniería en Ciencias Agroindustriales · 2026")
        subtitle.setObjectName("headerSubtitle")
        layout.addWidget(subtitle)

        return header

    # ─────────────────── SIDEBAR ────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        # Marca
        brand = QLabel("ICIAGRO")
        brand.setObjectName("sidebarTitle")
        brand.setAlignment(Qt.AlignCenter)
        version = QLabel("v1.0 — Trazabilidad MP")
        version.setObjectName("sidebarVersion")
        version.setAlignment(Qt.AlignCenter)

        layout.addWidget(brand)
        layout.addWidget(version)
        layout.addSpacing(16)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1E293B;")
        layout.addWidget(sep)
        layout.addSpacing(12)

        # Sección: Inicio
        self._section_label("INICIO", layout)

        self._nav_btn = {}
        self._add_nav(layout, "carga", "📂  Cargar archivo")

        layout.addSpacing(8)
        self._section_label("MÓDULOS", layout)

        self._add_nav(layout, "registro", "📝  Registro MP")
        self._add_nav(layout, "catalogo", "📋  Catálogo Proveedores")
        self._add_nav(layout, "reporte", "📊  Reportes / Exportar")

        layout.addStretch()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #1E293B;")
        layout.addWidget(sep2)
        layout.addSpacing(8)

        integrantes = QLabel("Integrantes")
        integrantes.setObjectName("sidebarVersion")
        integrantes.setAlignment(Qt.AlignCenter)
        layout.addWidget(integrantes)

        for nombre in ("Steven Mata", "Anthony Mata"):
            lbl = QLabel(f"· {nombre}")
            lbl.setObjectName("sidebarVersion")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)

        return sidebar

    def _section_label(self, texto: str, layout: QVBoxLayout) -> None:
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "font-size: 9px; color: #334155; font-weight: 700;"
            " letter-spacing: 2px; padding: 0 8px;"
        )
        layout.addWidget(lbl)
        layout.addSpacing(2)

    def _add_nav(self, layout: QVBoxLayout, key: str, label: str) -> None:
        btn = QPushButton(label)
        btn.setObjectName("navButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked=False, k=key: self._ir_a(k))
        layout.addWidget(btn)
        self._nav_btn[key] = btn

    def _setup_nav(self) -> None:
        pass

    # ─────────────────── PÁGINAS ────────────────────────────────

    def _build_carga_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageContainer")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        # Header de la página
        title = QLabel("Cargar archivo de trazabilidad")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Carga el archivo .xlsm de trazabilidad de Lácteos del Páramo "
            "para comenzar a registrar materia prima."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Drop zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.setMinimumHeight(160)
        self.drop_zone.archivo_cargado.connect(self._cargar_excel)
        layout.addWidget(self.drop_zone)

        # Info card
        info = QFrame()
        info.setObjectName("card")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)

        info_title = QLabel("¿Qué archivo debo cargar?")
        info_title.setObjectName("cardTitle")
        info_layout.addWidget(info_title)

        bullets = [
            "Archivo Excel con macros habilitadas (.xlsm)",
            "Debe contener las hojas: Registro_MP, Catalogo_Proveedores, Control, Hoja1",
            "Formato: trazabilidad_hongos_el_paramo_listo.xlsm o similar",
        ]
        for b in bullets:
            lbl = QLabel(f"  ·  {b}")
            lbl.setObjectName("pageSubtitle")
            info_layout.addWidget(lbl)

        layout.addWidget(info)
        layout.addStretch()

        return page

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(32)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)

        left = QLabel("ICIAGRO CORE · Sistema de Trazabilidad de Materia Prima")
        left.setObjectName("footerText")
        right = QLabel("Universidad Nacional de Costa Rica · Sede Brunca · 2026")
        right.setObjectName("footerText")
        right.setAlignment(Qt.AlignRight)

        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(right)

        return footer

    # ─────────────────── NAVEGACIÓN ─────────────────────────────

    def _ir_a(self, key: str) -> None:
        # Actualizar estado visual de los botones
        for k, btn in self._nav_btn.items():
            btn.setObjectName("navButtonActive" if k == key else "navButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        idx_map = {"carga": 0, "registro": 1, "catalogo": 2, "reporte": 3}
        idx = idx_map.get(key, 0)

        if key != "carga" and self._service is None:
            QMessageBox.information(
                self,
                "Archivo requerido",
                "Debes cargar el archivo Excel primero.\n\nVe a 'Cargar archivo'.",
            )
            self._ir_a("carga")
            return

        self.stack.setCurrentIndex(idx)

    # ─────────────────── EXCEL ──────────────────────────────────

    def _cargar_excel(self, ruta: str) -> None:
        try:
            self._service = ExcelService(ruta)
            self.page_registro.set_service(self._service)
            self.page_catalogo.set_service(self._service)
            self.page_reporte.set_service(self._service)

            nombre = ruta.replace("\\", "/").split("/")[-1]
            empresa = self._service.config.get("empresa", "")
            self.lbl_archivo.setText(
                f"{nombre}  ·  {empresa}" if empresa else nombre
            )

            QMessageBox.information(
                self,
                "Archivo cargado",
                f"Archivo cargado correctamente.\n\n"
                f"Empresa: {self._service.config.get('empresa', '—')}\n"
                f"Prefijo: {self._service.config.get('prefijo', '—')}\n"
                f"Proveedores: {len(self._service.get_codigos_proveedor())}",
            )
            self._ir_a("registro")

        except Exception as ex:
            QMessageBox.critical(
                self,
                "Error al cargar",
                f"No se pudo cargar el archivo.\n\nError: {ex}",
            )
            self._service = None

    def _on_registro_guardado(self) -> None:
        if self._service:
            self.page_reporte.cargar_registros()
