from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.icons import make_icon
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

_ICON_COLOR_NORMAL = "#475569"
_ICON_COLOR_ACTIVE = "#10B981"
_ICON_SIZE         = 16


class MainWindow(QMainWindow):
    """Ventana principal ICIAGRO CORE — sidebar colapsable + módulos de trazabilidad."""

    _SETTINGS_ORG     = "ICIAGRO"
    _SETTINGS_APP     = "IciagrocCore"
    _KEY_EXCEL        = "ultima_ruta_excel"
    _SIDEBAR_EXPANDED = 220
    _SIDEBAR_COLLAPSED = 54

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ICIAGRO CORE — Sistema de Trazabilidad Hongos del Páramo")
        self.setMinimumSize(1280, 780)

        self._service: Optional[HongosService] = None
        self._settings = QSettings(self._SETTINGS_ORG, self._SETTINGS_APP)

        # Sidebar state
        self._sidebar_expanded: bool = True
        self._active_key: str = ""
        self._nav_btn: dict[str, QPushButton] = {}
        self._nav_labels: dict[str, str] = {}
        self._nav_icons_n: dict[str, QIcon] = {}
        self._nav_icons_a: dict[str, QIcon] = {}
        self._section_labels: list[QWidget] = []
        self._sidebar_extra: list[QWidget] = []
        self._sidebar_widget: Optional[QWidget] = None
        self._btn_toggle: Optional[QPushButton] = None

        # Pre-build icons for all nav keys
        for key in _IDX:
            self._nav_icons_n[key] = make_icon(key, _ICON_COLOR_NORMAL, _ICON_SIZE)
            self._nav_icons_a[key] = make_icon(key, _ICON_COLOR_ACTIVE, _ICON_SIZE)

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
            self.page_carga,
            self.page_proveedores,
            self.page_evaluacion,
            self.page_clientes,
            self.page_recepcion,
            self.page_produccion,
            self.page_terminado,
            self.page_expedicion,
            self.page_retiro,
            self.page_etiquetas,
            self.page_reporte,
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
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #059669,stop:1 #047857);"
            "border:1px solid #10B981;"
            "border-radius:6px;padding:3px 12px;font-size:11px;"
            "font-weight:800;color:#FFFFFF;letter-spacing:1px;"
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
        sep.setStyleSheet("color:#1A3050;")
        layout.addWidget(sep)

        sub = QLabel("Universidad Nacional · Sede Brunca · 2026")
        sub.setObjectName("headerSubtitle")
        layout.addWidget(sub)

        return header

    # ─────────────────── SIDEBAR ────────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        self._sidebar_widget = QWidget()
        self._sidebar_widget.setObjectName("sidebar")
        self._sidebar_widget.setFixedWidth(self._SIDEBAR_EXPANDED)

        layout = QVBoxLayout(self._sidebar_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Brand + toggle ────────────────────────────────────────────
        brand_row = QWidget()
        brand_layout = QHBoxLayout(brand_row)
        brand_layout.setContentsMargins(14, 12, 10, 6)
        brand_layout.setSpacing(6)

        self._lbl_brand = QLabel("ICIAGRO")
        self._lbl_brand.setObjectName("sidebarTitle")
        self._sidebar_extra.append(self._lbl_brand)

        self._btn_toggle = QPushButton("‹")
        self._btn_toggle.setObjectName("sidebarToggle")
        self._btn_toggle.setFixedSize(26, 26)
        self._btn_toggle.setCursor(Qt.PointingHandCursor)
        self._btn_toggle.setToolTip("Contraer menú")
        self._btn_toggle.clicked.connect(self._toggle_sidebar)

        brand_layout.addWidget(self._lbl_brand)
        brand_layout.addStretch()
        brand_layout.addWidget(self._btn_toggle)
        layout.addWidget(brand_row)

        self._lbl_ver = QLabel("v2.0 · Hongos del Páramo")
        self._lbl_ver.setObjectName("sidebarVersion")
        self._lbl_ver.setAlignment(Qt.AlignCenter)
        self._lbl_ver.setContentsMargins(14, 0, 14, 8)
        self._sidebar_extra.append(self._lbl_ver)
        layout.addWidget(self._lbl_ver)

        layout.addWidget(self._sep())

        # ── Navigation items ──────────────────────────────────────────
        nav = QWidget()
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(6, 8, 6, 8)
        nav_layout.setSpacing(2)

        # INICIO
        nav_layout.addWidget(self._make_section_label("INICIO"))
        self._add_nav(nav_layout, "carga", "Cargar archivo")

        nav_layout.addSpacing(4)
        nav_layout.addWidget(self._sep())
        nav_layout.addSpacing(4)

        # PROVEEDORES
        nav_layout.addWidget(self._make_section_label("PROVEEDORES"))
        self._add_nav(nav_layout, "proveedores", "Gestión Proveedores")
        self._add_nav(nav_layout, "evaluacion",  "Evaluación Prov.")

        nav_layout.addSpacing(4)
        nav_layout.addWidget(self._sep())
        nav_layout.addSpacing(4)

        # CLIENTES
        nav_layout.addWidget(self._make_section_label("CLIENTES"))
        self._add_nav(nav_layout, "clientes", "Gestión Clientes")

        nav_layout.addSpacing(4)
        nav_layout.addWidget(self._sep())
        nav_layout.addSpacing(4)

        # TRAZABILIDAD
        nav_layout.addWidget(self._make_section_label("TRAZABILIDAD"))
        self._add_nav(nav_layout, "recepcion",  "Recepción MP")
        self._add_nav(nav_layout, "produccion", "Producción Interna")
        self._add_nav(nav_layout, "terminado",  "Prod. Terminado")
        self._add_nav(nav_layout, "expedicion", "Expedición y Ventas")
        self._add_nav(nav_layout, "retiro",     "Retiro de Producto")

        nav_layout.addSpacing(4)
        nav_layout.addWidget(self._sep())
        nav_layout.addSpacing(4)

        # HERRAMIENTAS
        nav_layout.addWidget(self._make_section_label("HERRAMIENTAS"))
        self._add_nav(nav_layout, "etiquetas", "Etiquetas")
        self._add_nav(nav_layout, "reporte",   "Reportes / Exportar")

        nav_layout.addStretch()
        layout.addWidget(nav, 1)

        # ── Integrantes ───────────────────────────────────────────────
        layout.addWidget(self._sep())

        self._lbl_integ = QLabel("Integrantes")
        self._lbl_integ.setObjectName("sidebarVersion")
        self._lbl_integ.setAlignment(Qt.AlignCenter)
        self._lbl_integ.setContentsMargins(0, 8, 0, 2)
        self._sidebar_extra.append(self._lbl_integ)
        layout.addWidget(self._lbl_integ)

        for nombre in ("Anthony Mata Quirós", "Camila Gómez Sequeira"):
            lbl = QLabel(f"· {nombre}")
            lbl.setObjectName("sidebarVersion")
            lbl.setAlignment(Qt.AlignCenter)
            self._sidebar_extra.append(lbl)
            layout.addWidget(lbl)

        layout.addSpacing(8)
        layout.addWidget(self._sep())
        layout.addSpacing(6)

        # ── Danger button ─────────────────────────────────────────────
        self._btn_borrar = QPushButton(" Cambiar Excel")
        self._btn_borrar.setObjectName("dangerButton")
        self._btn_borrar.setCursor(Qt.PointingHandCursor)
        self._btn_borrar.setFixedHeight(34)
        self._btn_borrar.setIcon(make_icon("warning", "#EF4444", 14))
        self._btn_borrar.setIconSize(QSize(14, 14))
        self._btn_borrar.clicked.connect(self._solicitar_borrar_excel)

        btn_wrapper = QWidget()
        bw_layout = QHBoxLayout(btn_wrapper)
        bw_layout.setContentsMargins(8, 0, 8, 8)
        bw_layout.addWidget(self._btn_borrar)
        layout.addWidget(btn_wrapper)
        self._sidebar_extra.append(self._btn_borrar)

        return self._sidebar_widget

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet("color:#1A3050;")
        return f

    def _make_section_label(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "font-size:9px;color:#1E3A5F;font-weight:800;"
            "letter-spacing:2.5px;padding:4px 10px 2px 10px;"
        )
        self._section_labels.append(lbl)
        return lbl

    def _add_nav(self, layout: QVBoxLayout, key: str, label: str) -> None:
        btn = QPushButton(f" {label}")
        btn.setObjectName("navButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        btn.setIcon(self._nav_icons_n[key])
        btn.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        btn.setToolTip("")
        btn.clicked.connect(lambda checked=False, k=key: self._ir_a(k))
        layout.addWidget(btn)
        self._nav_btn[key] = btn
        self._nav_labels[key] = label

    # ─────────────────── SIDEBAR TOGGLE ─────────────────────────────

    def _toggle_sidebar(self) -> None:
        self._sidebar_expanded = not self._sidebar_expanded
        w = self._SIDEBAR_EXPANDED if self._sidebar_expanded else self._SIDEBAR_COLLAPSED
        self._sidebar_widget.setFixedWidth(w)

        # Show/hide text-only elements
        for widget in self._sidebar_extra:
            widget.setVisible(self._sidebar_expanded)
        for lbl in self._section_labels:
            lbl.setVisible(self._sidebar_expanded)

        # Update toggle arrow direction + tooltip
        if self._sidebar_expanded:
            self._btn_toggle.setText("‹")
            self._btn_toggle.setToolTip("Contraer menú")
        else:
            self._btn_toggle.setText("›")
            self._btn_toggle.setToolTip("Expandir menú")

        # Update nav button text / tooltips
        for key, btn in self._nav_btn.items():
            if self._sidebar_expanded:
                btn.setText(f" {self._nav_labels[key]}")
                btn.setToolTip("")
            else:
                btn.setText("")
                btn.setToolTip(self._nav_labels[key])

        self._update_nav_styles()

    def _update_nav_styles(self) -> None:
        collapsed = not self._sidebar_expanded
        for k, btn in self._nav_btn.items():
            is_active = k == self._active_key
            if collapsed:
                name = "navButtonActiveCollapsed" if is_active else "navButtonCollapsed"
            else:
                name = "navButtonActive" if is_active else "navButton"
            btn.setObjectName(name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.setIcon(self._nav_icons_a[k] if is_active else self._nav_icons_n[k])

    # ─────────────────── PÁGINA DE CARGA ────────────────────────────

    def _build_carga_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageContainer")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(48, 48, 48, 48)
        outer.setSpacing(24)
        outer.setAlignment(Qt.AlignTop)

        title = QLabel("Cargar archivo de trazabilidad")
        title.setObjectName("pageTitle")
        sub = QLabel(
            "Carga el archivo Excel del sistema de trazabilidad de Hongos del Páramo "
            "(.xlsx) para comenzar a trabajar con los módulos."
        )
        sub.setObjectName("pageSubtitle")
        sub.setWordWrap(True)
        outer.addWidget(title)
        outer.addWidget(sub)

        # ── Estado 0: sin archivo ──────────────────────────────────────
        self._carga_stack = QStackedWidget()

        empty = QWidget()
        empty_lay = QVBoxLayout(empty)
        empty_lay.setContentsMargins(0, 0, 0, 0)
        empty_lay.setSpacing(16)

        self.drop_zone = DropZoneWidget()
        self.drop_zone.setMinimumHeight(180)
        self.drop_zone.archivo_cargado.connect(self._cargar_excel)
        empty_lay.addWidget(self.drop_zone)

        info = QFrame()
        info.setObjectName("card")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(20, 16, 20, 16)
        info_lay.setSpacing(8)
        info_title = QLabel("Archivo esperado")
        info_title.setObjectName("cardTitle")
        info_lay.addWidget(info_title)
        for b in [
            "Archivo Excel (.xlsx o .xlsm) del sistema de trazabilidad Hongos del Páramo",
            "Hojas requeridas: Proveedores, Evaluacion_Proveedores, Clientes, Recepcion_MP,",
            "  Produccion_Interna, Producto_Terminado, Expedicion_Ventas, Retiro_Producto",
        ]:
            lbl = QLabel(f"  ·  {b}")
            lbl.setObjectName("pageSubtitle")
            info_lay.addWidget(lbl)
        empty_lay.addWidget(info)
        empty_lay.addStretch()
        self._carga_stack.addWidget(empty)   # índice 0

        # ── Estado 1: archivo ya cargado ──────────────────────────────
        self._carga_stack.addWidget(self._build_carga_loaded_card())  # índice 1

        outer.addWidget(self._carga_stack, 1)
        return page

    def _build_carga_loaded_card(self) -> QWidget:
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        card = QFrame()
        card.setObjectName("card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(28, 22, 28, 26)
        card_lay.setSpacing(16)

        # Header con checkmark
        hdr = QHBoxLayout()
        check_lbl = QLabel("✓")
        check_lbl.setStyleSheet(
            "font-size:34px;font-weight:900;color:#10B981;background:transparent;"
        )
        check_lbl.setFixedWidth(44)
        hdr_title = QLabel("Archivo Excel cargado correctamente")
        hdr_title.setObjectName("cardTitle")
        hdr.addWidget(check_lbl)
        hdr.addWidget(hdr_title)
        hdr.addStretch()
        card_lay.addLayout(hdr)

        # Nombre del archivo
        self.lbl_carga_nombre = QLabel("—")
        self.lbl_carga_nombre.setStyleSheet(
            "background:#061A10;border:1px solid #059669;border-radius:8px;"
            "padding:9px 16px;font-size:13px;font-weight:700;color:#10B981;"
        )
        card_lay.addWidget(self.lbl_carga_nombre)

        # Stats de contenido
        self.lbl_carga_stats = QLabel("Cargando estadísticas...")
        self.lbl_carga_stats.setObjectName("pageSubtitle")
        card_lay.addWidget(self.lbl_carga_stats)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1A3050;")
        card_lay.addWidget(sep)

        # Mensaje de bloqueo
        lock_msg = QLabel(
            "El módulo de carga está bloqueado mientras hay un archivo activo.\n"
            "Para cambiar el archivo Excel usa el botón  \"Cambiar Excel\"  en el panel izquierdo."
        )
        lock_msg.setObjectName("pageSubtitle")
        lock_msg.setWordWrap(True)
        card_lay.addWidget(lock_msg)

        lay.addWidget(card)
        lay.addStretch()
        return container

    # ─────────────────── FOOTER ─────────────────────────────────────

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(32)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)

        left = QLabel("ICIAGRO CORE · Sistema de Trazabilidad Hongos del Páramo")
        left.setObjectName("footerText")

        center = QLabel("Desarrollado por Steven Mata Quirós")
        center.setObjectName("footerText")
        center.setAlignment(Qt.AlignCenter)

        right = QLabel("Universidad Nacional de Costa Rica · Sede Brunca · 2026")
        right.setObjectName("footerText")
        right.setAlignment(Qt.AlignRight)

        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(center)
        layout.addStretch()
        layout.addWidget(right)
        return footer

    # ─────────────────── NAVEGACIÓN ─────────────────────────────────

    def _ir_a(self, key: str) -> None:
        self._active_key = key
        self._update_nav_styles()

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
        ruta = self._settings.value(self._KEY_EXCEL, "")
        if ruta and os.path.isfile(ruta):
            self._cargar_excel(ruta, silencioso=True)
        else:
            self._ir_a("carga")

    def _cargar_excel(self, ruta: str, silencioso: bool = False) -> None:
        try:
            service = HongosService(ruta)
            self._service = service

            self._settings.setValue(self._KEY_EXCEL, ruta)

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

            n_prov = len(service.get_proveedores_df())
            n_cli  = len(service.get_clientes_df())
            n_prod = len(service.get_producciones_df())

            # Actualizar panel de carga → estado "cargado"
            self.lbl_carga_nombre.setText(nombre)
            self.lbl_carga_stats.setText(
                f"Proveedores: {n_prov}  ·  Clientes: {n_cli}  ·  Lotes de producción: {n_prod}"
            )
            self._carga_stack.setCurrentIndex(1)

            if not silencioso:
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

    # ─────────────────── BORRAR / CAMBIAR EXCEL ─────────────────────

    def _solicitar_borrar_excel(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Autenticación requerida")
        dlg.setFixedWidth(360)
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        dlg.setStyleSheet("""
            QDialog {
                background-color: #0D1B2E;
                border: 1px solid #1A3050;
            }
            QLabel {
                color: #CBD5E1;
                background: transparent;
                font-family: "Segoe UI Variable", "Segoe UI", system-ui;
            }
            QLineEdit {
                background-color: #0A1525;
                border: 1px solid #1A3050;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 13px;
                color: #E2E8F0;
                min-height: 36px;
                font-family: "Segoe UI Variable", "Segoe UI", system-ui;
            }
            QLineEdit:focus {
                border-color: #10B981;
                background-color: #091827;
            }
            QPushButton {
                background-color: #059669;
                border: 1px solid #10B981;
                border-radius: 7px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 700;
                color: #FFFFFF;
                min-width: 90px;
                font-family: "Segoe UI Variable", "Segoe UI", system-ui;
            }
            QPushButton:hover {
                background-color: #10B981;
                border-color: #34D399;
            }
            QPushButton[text="Cancelar"] {
                background-color: #0A1525;
                border: 1px solid #1A3050;
                color: #64748B;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #0F1E35;
                border-color: #2D4F72;
                color: #94A3B8;
            }
            QDialogButtonBox {
                background: transparent;
            }
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(14)

        icono = QLabel("Autenticación requerida")
        icono.setStyleSheet(
            "font-size:16px;font-weight:800;color:#F1F5F9;"
            "font-family:'Segoe UI Variable','Segoe UI',system-ui;"
        )
        layout.addWidget(icono)

        titulo = QLabel("Ingresa la contraseña para cambiar el archivo Excel.")
        titulo.setWordWrap(True)
        titulo.setStyleSheet(
            "font-size:12px;color:#475569;"
            "font-family:'Segoe UI Variable','Segoe UI',system-ui;"
        )
        layout.addWidget(titulo)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1A3050;")
        layout.addWidget(sep)

        lbl_pwd = QLabel("CONTRASEÑA")
        lbl_pwd.setStyleSheet(
            "font-size:10px;font-weight:700;color:#1E3A5F;letter-spacing:1.5px;"
            "font-family:'Segoe UI Variable','Segoe UI',system-ui;"
        )
        layout.addWidget(lbl_pwd)

        self._pwd_input = QLineEdit()
        self._pwd_input.setEchoMode(QLineEdit.Password)
        self._pwd_input.setPlaceholderText("••••••••")
        layout.addWidget(self._pwd_input)

        self._pwd_error = QLabel("")
        self._pwd_error.setStyleSheet(
            "color:#EF4444;font-size:11px;font-weight:500;"
        )
        layout.addWidget(self._pwd_error)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Confirmar")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.accepted.connect(lambda: self._verificar_clave(dlg))
        botones.rejected.connect(dlg.reject)
        self._pwd_input.returnPressed.connect(lambda: self._verificar_clave(dlg))
        layout.addWidget(botones)

        self._pwd_dialog = dlg
        dlg.exec()

    def _verificar_clave(self, dlg: QDialog) -> None:
        if self._pwd_input.text() == "123":
            dlg.accept()
            self._borrar_excel()
        else:
            self._pwd_error.setText("Contraseña incorrecta. Intenta de nuevo.")
            self._pwd_input.clear()
            self._pwd_input.setFocus()

    def _borrar_excel(self) -> None:
        self._service = None
        self._settings.remove(self._KEY_EXCEL)
        self.lbl_archivo.setText("Sin archivo cargado")
        self._carga_stack.setCurrentIndex(0)   # resetear a estado vacío
        self._ir_a("carga")
