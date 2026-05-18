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

    /* ── WELCOME ── */
    QFrame#hero {
        background-color: transparent;
        border: none;
    }

    QWidget#heroOverlay {
        background-color: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 rgba(11, 17, 32, 175),
            stop: 0.55 rgba(11, 17, 32, 110),
            stop: 1 rgba(11, 17, 32, 210)
        );
    }

    QLabel#title {
        font-size: 26px;
        font-weight: 600;
        letter-spacing: 1px;
        color: #E5E7EB;
    }

    QLabel#subtitle {
        color: #94A3B8;
        font-size: 14px;
    }

    QLabel#course {
        color: #94A3B8;
        font-size: 13px;
    }

    QLabel#heroTitle {
        font-size: 18px;
        font-weight: 600;
        color: #E5E7EB;
    }

    QLabel#heroSubtitle {
        color: #94A3B8;
        font-size: 12px;
    }

    QLabel#sectionTitle {
        font-size: 14px;
        font-weight: 600;
        color: #E5E7EB;
    }

    QLabel#listItem {
        color: #94A3B8;
        font-size: 13px;
    }

    /* ── BOTONES ── */
    QPushButton#primaryButton {
        background-color: #3F6B4B;
        border: 1px solid #4F7D5C;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 14px;
        font-weight: 600;
        color: #FFFFFF;
    }

    QPushButton#primaryButton:hover {
        background-color: #4F7D5C;
        border-color: #5A8F68;
    }

    QPushButton#primaryButton:pressed {
        background-color: #35593F;
    }

    QPushButton#secondaryButton {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        color: #E5E7EB;
    }

    QPushButton#secondaryButton:hover {
        background-color: #263347;
        border-color: #4A5568;
    }

    QPushButton#secondaryButton:pressed {
        background-color: #1A2535;
    }

    QPushButton#dangerButton {
        background-color: #7F1D1D;
        border: 1px solid #991B1B;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        color: #FFFFFF;
    }

    QPushButton#dangerButton:hover {
        background-color: #991B1B;
    }

    /* ── MAIN WINDOW ── */
    QWidget#mainWindow {
        background-color: #0B1120;
    }

    /* ── SIDEBAR ── */
    QWidget#sidebar {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }

    QLabel#sidebarTitle {
        font-size: 13px;
        font-weight: 700;
        color: #3F6B4B;
        letter-spacing: 2px;
    }

    QLabel#sidebarVersion {
        font-size: 10px;
        color: #64748B;
    }

    QPushButton#navButton {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        color: #94A3B8;
        text-align: left;
    }

    QPushButton#navButton:hover {
        background-color: #1E293B;
        color: #E5E7EB;
    }

    QPushButton#navButtonActive {
        background-color: #1E293B;
        border: none;
        border-left: 3px solid #3F6B4B;
        border-radius: 0px 8px 8px 0px;
        padding: 10px 16px;
        font-size: 13px;
        color: #E5E7EB;
        font-weight: 600;
        text-align: left;
    }

    /* ── HEADER ── */
    QWidget#appHeader {
        background-color: #0F172A;
        border-bottom: 1px solid #1E293B;
    }

    QLabel#headerTitle {
        font-size: 15px;
        font-weight: 600;
        color: #E5E7EB;
    }

    QLabel#headerSubtitle {
        font-size: 11px;
        color: #64748B;
    }

    QLabel#statusBadge {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 11px;
        color: #94A3B8;
    }

    /* ── CONTENT AREA ── */
    QWidget#contentArea {
        background-color: #0B1120;
    }

    QWidget#pageContainer {
        background-color: #0B1120;
    }

    /* ── CARDS ── */
    QFrame#card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    QLabel#cardTitle {
        font-size: 15px;
        font-weight: 600;
        color: #E5E7EB;
    }

    QLabel#cardSubtitle {
        font-size: 12px;
        color: #64748B;
    }

    /* ── LABELS ── */
    QLabel#fieldLabel {
        font-size: 12px;
        color: #94A3B8;
        font-weight: 500;
    }

    QLabel#autoValue {
        background-color: #111827;
        border: 1px solid #1E293B;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        color: #64748B;
    }

    QLabel#pageTitle {
        font-size: 20px;
        font-weight: 600;
        color: #E5E7EB;
    }

    QLabel#pageSubtitle {
        font-size: 13px;
        color: #64748B;
    }

    /* ── INPUTS ── */
    QLineEdit, QTextEdit {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 7px 10px;
        font-size: 13px;
        color: #E5E7EB;
    }

    QLineEdit:focus, QTextEdit:focus {
        border-color: #3F6B4B;
        background-color: #111827;
    }

    QLineEdit:disabled, QTextEdit:disabled {
        background-color: #111827;
        color: #64748B;
        border-color: #1E293B;
    }

    QComboBox {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 7px 10px;
        font-size: 13px;
        color: #E5E7EB;
    }

    QComboBox:focus {
        border-color: #3F6B4B;
    }

    QComboBox::drop-down {
        border: none;
        width: 20px;
    }

    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }

    QComboBox QAbstractItemView {
        background-color: #0F172A;
        border: 1px solid #334155;
        color: #E5E7EB;
        selection-background-color: #1E293B;
        selection-color: #E5E7EB;
    }

    QDateEdit {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 7px 10px;
        font-size: 13px;
        color: #E5E7EB;
    }

    QDateEdit:focus {
        border-color: #3F6B4B;
    }

    QDateEdit::drop-down {
        border: none;
        width: 20px;
    }

    QSpinBox {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 7px 10px;
        font-size: 13px;
        color: #E5E7EB;
    }

    QSpinBox:focus {
        border-color: #3F6B4B;
    }

    QSpinBox::up-button, QSpinBox::down-button {
        border: none;
        width: 16px;
        background-color: #1E293B;
    }

    /* ── TABLAS ── */
    QTableWidget {
        background-color: #111827;
        alternate-background-color: #0F172A;
        color: #E5E7EB;
        gridline-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        font-size: 12px;
        selection-background-color: #1E3A2F;
        selection-color: #E5E7EB;
    }

    QTableWidget::item {
        padding: 6px 10px;
        border: none;
    }

    QTableWidget::item:selected {
        background-color: #1E3A2F;
        color: #E5E7EB;
    }

    QTableWidget::item:hover {
        background-color: #1F2937;
    }

    QHeaderView::section {
        background-color: #1E293B;
        color: #94A3B8;
        border: none;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
        padding: 8px 10px;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
    }

    QHeaderView::section:first {
        border-left: none;
    }

    /* ── SCROLL BARS ── */
    QScrollBar:vertical {
        background: #0F172A;
        width: 8px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #334155;
        border-radius: 4px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background: #4A5568;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background: #0F172A;
        height: 8px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background: #334155;
        border-radius: 4px;
        min-width: 20px;
    }

    QScrollBar::handle:horizontal:hover {
        background: #4A5568;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* ── DROP ZONE ── */
    QWidget#dropZone {
        background-color: #1E293B;
        border: 2px dashed #334155;
        border-radius: 12px;
    }

    QWidget#dropZoneActive {
        background-color: #1E293B;
        border: 2px dashed #3F6B4B;
        border-radius: 12px;
    }

    QWidget#dropZoneLoaded {
        background-color: #1A2D22;
        border: 2px solid #3F6B4B;
        border-radius: 12px;
    }

    /* ── SEPARADORES ── */
    QFrame[frameShape="4"] {
        color: #1E293B;
    }

    QFrame[frameShape="5"] {
        color: #1E293B;
    }

    /* ── TOOLTIPS ── */
    QToolTip {
        background-color: #1E293B;
        border: 1px solid #334155;
        color: #E5E7EB;
        padding: 4px 8px;
        border-radius: 4px;
    }

    /* ── MESSAGE BOX ── */
    QMessageBox {
        background-color: #1E293B;
    }

    QMessageBox QPushButton {
        background-color: #3F6B4B;
        border: 1px solid #4F7D5C;
        border-radius: 6px;
        padding: 6px 16px;
        color: #FFFFFF;
        min-width: 70px;
    }

    QMessageBox QPushButton:hover {
        background-color: #4F7D5C;
    }

    /* ── BADGE STATUS ── */
    QLabel#badgeOK {
        background-color: #1A2D22;
        border: 1px solid #3F6B4B;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        color: #4F7D5C;
        font-weight: 600;
    }

    QLabel#badgeREVISAR {
        background-color: #2D1F0A;
        border: 1px solid #8B6F47;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        color: #8B6F47;
        font-weight: 600;
    }

    /* ── FOOTER ── */
    QWidget#footer {
        background-color: #0F172A;
        border-top: 1px solid #1E293B;
    }

    QLabel#footerText {
        font-size: 11px;
        color: #334155;
    }
    """
