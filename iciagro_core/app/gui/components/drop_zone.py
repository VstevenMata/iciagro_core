from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DropZoneWidget(QWidget):
    """
    Widget drag & drop para cargar archivos .xlsx o .xlsm.
    Emite `archivo_cargado` con la ruta del archivo cuando se suelta un archivo válido.
    """

    archivo_cargado = Signal(str)

    _EXTS = (".xlsx", ".xlsm")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self._loaded = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("📂")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")

        self.text_label = QLabel("Arrastra el archivo Excel aquí\n(.xlsx o .xlsm)")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet(
            "color: #94A3B8; font-size: 13px; background: transparent; border: none;"
        )

        self.sub_label = QLabel("o haz clic para seleccionar")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet(
            "color: #64748B; font-size: 11px; background: transparent; border: none;"
        )

        layout.addWidget(self.icon_label)
        layout.addSpacing(6)
        layout.addWidget(self.text_label)
        layout.addWidget(self.sub_label)

    def mousePressEvent(self, event) -> None:
        from PySide6.QtWidgets import QFileDialog
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Excel (*.xlsx *.xlsm)",
        )
        if ruta:
            self._cargar(ruta)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().endswith(self._EXTS) for u in urls):
                self.setObjectName("dropZoneActive")
                self.style().unpolish(self)
                self.style().polish(self)
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        obj = "dropZoneLoaded" if self._loaded else "dropZone"
        self.setObjectName(obj)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            ruta = url.toLocalFile()
            if ruta.endswith(self._EXTS):
                self._cargar(ruta)
                break

    def _cargar(self, ruta: str) -> None:
        nombre = ruta.replace("\\", "/").split("/")[-1]
        self._loaded = True
        self.icon_label.setText("✅")
        self.text_label.setText(f"Archivo cargado:\n{nombre}")
        self.sub_label.setText("Clic para cambiar el archivo")
        self.setObjectName("dropZoneLoaded")
        self.style().unpolish(self)
        self.style().polish(self)
        self.archivo_cargado.emit(ruta)
