from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from gui.main_window import MainWindow


class HeroBanner(QFrame):
    def __init__(self, image_path: Optional[str] = None) -> None:
        super().__init__()
        self.setObjectName("hero")
        self._image_path = image_path
        self._last_size = QSize()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.overlay = QWidget()
        self.overlay.setObjectName("heroOverlay")

        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(48, 40, 48, 40)
        overlay_layout.setSpacing(16)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(24)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        title = QLabel("ICIAGRO CORE")
        title.setObjectName("title")

        subtitle = QLabel("Sistema Analítico de Datos")
        subtitle.setObjectName("subtitle")

        course = QLabel("Ingeniería en Calidad e Innovación Agroalimentaria - 2026")
        course.setObjectName("course")

        hero_title = QLabel("UNIVERSIDAD NACIONAL DE COSTA RICA")
        hero_title.setObjectName("heroTitle")

        hero_subtitle = QLabel("Sede Regional Brunca - ICIAGRO")
        hero_subtitle.setObjectName("heroSubtitle")

        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)
        left_layout.addWidget(course)
        left_layout.addSpacing(10)
        left_layout.addWidget(hero_title)
        left_layout.addWidget(hero_subtitle)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(self._resolve_logo_path())
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(
                    QSize(120, 120),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        right_layout.addWidget(logo_label)
        right_layout.addSpacing(8)

        integrantes_title = QLabel("Integrantes")
        integrantes_title.setObjectName("sectionTitle")
        integrantes_title.setAlignment(Qt.AlignLeft)

        right_layout.addWidget(integrantes_title)

        for name in (
            "- Anthony Mata Quirós",
            "- Camila Gómez Sequeira",
        ):
            item = QLabel(name)
            item.setObjectName("listItem")
            item.setAlignment(Qt.AlignLeft)
            right_layout.addWidget(item)

        top_layout.addLayout(left_layout)
        top_layout.addStretch()
        top_layout.addLayout(right_layout)

        overlay_layout.addLayout(top_layout)
        overlay_layout.addStretch()

        self._action_layout = QHBoxLayout()
        self._action_layout.addStretch()
        self._action_layout.addStretch()

        overlay_layout.addLayout(self._action_layout)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label, 0, 0)
        layout.addWidget(self.overlay, 0, 0)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._refresh_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        if self.size() != self._last_size:
            self._refresh_pixmap()

    def _refresh_pixmap(self) -> None:
        size = self.size()

        if size.width() < 2 or size.height() < 2:
            return

        self._last_size = size
        pixmap = self._load_pixmap(size)
        self.image_label.setPixmap(pixmap)

    def _load_pixmap(self, size: QSize) -> QPixmap:
        if self._image_path:
            source = QPixmap(self._image_path)
            if not source.isNull():
                return source.scaled(
                    size,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
        return self._build_fallback_pixmap(size)

    def _build_fallback_pixmap(self, size: QSize) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = pixmap.rect()
        gradient = QLinearGradient(0, 0, size.width(), size.height())
        gradient.setColorAt(0.0, QColor("#0F172A"))
        gradient.setColorAt(0.6, QColor("#111827"))
        gradient.setColorAt(1.0, QColor("#0B1120"))
        painter.fillRect(rect, gradient)
        painter.end()
        return pixmap

    def _resolve_logo_path(self) -> str:
        if getattr(sys, "frozen", False):
            assets_dir = Path(sys._MEIPASS) / "assets"
        else:
            assets_dir = Path(__file__).resolve().parents[1] / "assets"
        candidate = assets_dir / "logo_hongos.png"
        return str(candidate) if candidate.is_file() else ""

    def set_action_button(self, button: QPushButton) -> None:
        self._action_layout.insertWidget(1, button, 0, Qt.AlignHCenter)


class WelcomeView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("root")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        hero = HeroBanner(self._resolve_hero_path())
        hero.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.start_button = QPushButton("Ingresar al sistema")
        self.start_button.setObjectName("primaryButton")
        self.start_button.setCursor(Qt.PointingHandCursor)
        hero.set_action_button(self.start_button)

        # Connect button to open ExcelView
        self.start_button.clicked.connect(self._open_excel_view)

        root_layout.addWidget(hero)

    def _resolve_hero_path(self) -> Optional[str]:
        if getattr(sys, "frozen", False):
            assets_dir = Path(sys._MEIPASS) / "assets"
        else:
            assets_dir = Path(__file__).resolve().parents[1] / "assets"

        candidate = assets_dir / "logo_hongos.png"
        return str(candidate) if candidate.is_file() else None

    def _open_excel_view(self) -> None:
        self.window().close()
        self._main = MainWindow()
        self._main.show()
        self._main.showMaximized()