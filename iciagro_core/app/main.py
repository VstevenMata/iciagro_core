import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from gui.styles import build_stylesheet
from gui.welcome_view import WelcomeView


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(build_stylesheet())

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
