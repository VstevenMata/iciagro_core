import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

from gui.styles import build_stylesheet
from gui.welcome_view import WelcomeView


def _resolve_asset(name: str) -> str:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return str(base / "assets" / name)


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(build_stylesheet())

    icon_path = _resolve_asset("logo_hongos.png")
    if Path(icon_path).is_file():
        app.setWindowIcon(QIcon(icon_path))

    window = QMainWindow()
    window.setWindowTitle("ICIAGRO CORE")
    window.resize(1200, 760)
    window.setMinimumSize(1024, 680)
    window.setCentralWidget(WelcomeView())
    window.show()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
