def build_stylesheet() -> str:
    return """
    * {
        font-family: "Segoe UI", "Inter", "Roboto";
        font-size: 14px;
        color: #E5E7EB;
    }

    QMainWindow, QWidget#root {
        background-color: #0B1120;
    }

    QFrame#header {
        background-color: transparent;
    }

    QLabel#title {
        font-size: 26px;
        font-weight: 600;
        letter-spacing: 1px;
    }

    QLabel#subtitle {
        color: #94A3B8;
        font-size: 14px;
    }

    QLabel#course {
        color: #94A3B8;
        font-size: 13px;
    }

    QLabel#brandTag {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 12px;
    }

    QFrame#hero {
        background-color: transparent;
        border: none;
    }

    QWidget#heroOverlay {
        background-color: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 rgba(11, 17, 32, 170),
            stop: 0.55 rgba(11, 17, 32, 110),
            stop: 1 rgba(11, 17, 32, 200)
        );
    }

    QLabel#heroTitle {
        font-size: 18px;
        font-weight: 600;
    }

    QLabel#heroSubtitle {
        color: #94A3B8;
        font-size: 12px;
    }

    QPushButton#primaryButton {
        background-color: red;
        border: 1px solid #4F7D5C;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 14px;
        font-weight: 600;
    }

    QPushButton#primaryButton:hover {
        background-color: green;
    }

    QPushButton#primaryButton:pressed {
        background-color: red;
    }

    QLabel#sectionTitle {
        font-size: 14px;
        font-weight: 600;
    }

    QLabel#listItem {
        color: #94A3B8;
        font-size: 13px;
    }
    """
