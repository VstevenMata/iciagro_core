def _write_arrow_svgs() -> tuple[str, str]:
    """Writes up/down triangle SVGs to temp dir. Returns (up_url, down_url)."""
    import tempfile
    from pathlib import Path

    tmp = Path(tempfile.gettempdir()) / "iciagro_ui"
    tmp.mkdir(exist_ok=True)
    color = "#94A3B8"
    (tmp / "arrow_up.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 6">'
        f'<polygon points="5,0 0,6 10,6" fill="{color}"/></svg>',
        encoding="utf-8",
    )
    (tmp / "arrow_down.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 6">'
        f'<polygon points="0,0 10,0 5,6" fill="{color}"/></svg>',
        encoding="utf-8",
    )
    up = str(tmp / "arrow_up.svg").replace("\\", "/")
    dn = str(tmp / "arrow_down.svg").replace("\\", "/")
    return up, dn


def build_stylesheet() -> str:
    """
    Sistema de diseño enterprise — ICIAGRO CORE
    Paleta: Navy-black + Emerald accent | Fuente: Segoe UI Variable / Inter
    Contraste WCAG AA+ en todos los textos primarios.
    """
    _up, _dn = _write_arrow_svgs()
    return """
    /* ══════════════════════════════════════════════════════
       GLOBAL RESET & BASE
    ══════════════════════════════════════════════════════ */
    * {
        font-family: "Segoe UI Variable", "Segoe UI", "Inter", "Roboto", system-ui, sans-serif;
        font-size: 13px;
        color: #CBD5E1;
        outline: none;
    }

    QMainWindow, QWidget#root, QDialog {
        background-color: #060D1A;
    }

    /* ══════════════════════════════════════════════════════
       WELCOME VIEW
    ══════════════════════════════════════════════════════ */
    QFrame#hero { background-color: transparent; border: none; }

    QWidget#heroOverlay {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0.00 rgba(4,8,18,0.92),
            stop:0.45 rgba(4,8,18,0.82),
            stop:0.72 rgba(4,8,18,0.68),
            stop:1.00 rgba(4,8,18,0.50)
        );
    }

    QLabel#title {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: 0.8px;
        color: #FFFFFF;
    }

    QLabel#subtitle {
        color: #E2E8F0;
        font-size: 14px;
        font-weight: 500;
    }

    QLabel#course {
        color: #CBD5E1;
        font-size: 12px;
        font-weight: 400;
    }

    QLabel#heroTitle {
        font-size: 18px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 0.3px;
    }

    QLabel#heroSubtitle {
        color: #CBD5E1;
        font-size: 11px;
        font-weight: 500;
    }

    QLabel#sectionTitle {
        font-size: 13px;
        font-weight: 700;
        color: #FFFFFF;
    }

    QLabel#listItem {
        color: #CBD5E1;
        font-size: 12px;
        font-weight: 400;
    }

    /* ══════════════════════════════════════════════════════
       MAIN LAYOUT
    ══════════════════════════════════════════════════════ */
    QWidget#mainWindow { background-color: #060D1A; }
    QWidget#contentArea, QWidget#pageContainer { background-color: #060D1A; }

    /* ══════════════════════════════════════════════════════
       HEADER
    ══════════════════════════════════════════════════════ */
    QWidget#appHeader {
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #0D1B2E,
            stop:1 #091523
        );
        border-bottom: 1px solid #1A3050;
    }

    QLabel#headerTitle {
        font-size: 14px;
        font-weight: 700;
        color: #E2E8F0;
        letter-spacing: 0.2px;
    }

    QLabel#headerSubtitle {
        font-size: 11px;
        color: #475569;
        font-weight: 400;
    }

    QLabel#statusBadge {
        background-color: #0F1E35;
        border: 1px solid #1E3A5F;
        border-radius: 5px;
        padding: 3px 10px;
        font-size: 11px;
        color: #64748B;
        font-weight: 500;
    }

    /* ══════════════════════════════════════════════════════
       SIDEBAR
    ══════════════════════════════════════════════════════ */
    QWidget#sidebar {
        background-color: #08111F;
        border-right: 1px solid #0F1E35;
    }

    QLabel#sidebarTitle {
        font-size: 14px;
        font-weight: 800;
        color: #10B981;
        letter-spacing: 3px;
    }

    QLabel#sidebarVersion {
        font-size: 10px;
        color: #2D4F72;
        font-weight: 400;
    }

    /* ── Sidebar toggle button ─────────────────────────────────── */
    QPushButton#sidebarToggle {
        background-color: transparent;
        border: 1px solid #1A3050;
        border-radius: 5px;
        padding: 0px;
        font-size: 14px;
        font-weight: 700;
        color: #2D4F72;
        text-align: center;
    }

    QPushButton#sidebarToggle:hover {
        background-color: #0F1E35;
        color: #10B981;
        border-color: #2D4F72;
    }

    QPushButton#sidebarToggle:pressed {
        background-color: #152840;
    }

    /* ── Nav buttons — expanded ────────────────────────────────── */
    QPushButton#navButton {
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 9px 14px;
        font-size: 12px;
        font-weight: 500;
        color: #475569;
        text-align: left;
    }

    QPushButton#navButton:hover {
        background-color: #0F1E35;
        color: #CBD5E1;
    }

    QPushButton#navButton:pressed {
        background-color: #152840;
    }

    QPushButton#navButtonActive {
        background-color: #0F2238;
        border: none;
        border-left: 3px solid #10B981;
        border-radius: 0px 6px 6px 0px;
        padding: 9px 14px 9px 11px;
        font-size: 12px;
        font-weight: 700;
        color: #10B981;
        text-align: left;
    }

    /* ── Nav buttons — collapsed (icon only) ───────────────────── */
    QPushButton#navButtonCollapsed {
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 10px 6px;
        font-size: 12px;
        color: transparent;
        text-align: center;
    }

    QPushButton#navButtonCollapsed:hover {
        background-color: #0F1E35;
    }

    QPushButton#navButtonCollapsed:pressed {
        background-color: #152840;
    }

    QPushButton#navButtonActiveCollapsed {
        background-color: #0F2238;
        border: none;
        border-left: 3px solid #10B981;
        border-radius: 0px 6px 6px 0px;
        padding: 10px 3px;
        color: transparent;
        text-align: center;
    }

    /* ══════════════════════════════════════════════════════
       FOOTER
    ══════════════════════════════════════════════════════ */
    QWidget#footer {
        background-color: #08111F;
        border-top: 1px solid #0F1E35;
    }

    QLabel#footerText {
        font-size: 10px;
        color: #2D4F72;
        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* ══════════════════════════════════════════════════════
       CARDS
    ══════════════════════════════════════════════════════ */
    QFrame#card {
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #0D1B2E,
            stop:1 #0A1525
        );
        border: 1px solid #1A3050;
        border-radius: 10px;
    }

    QLabel#cardTitle {
        font-size: 14px;
        font-weight: 700;
        color: #E2E8F0;
        letter-spacing: 0.1px;
    }

    QLabel#cardSubtitle { font-size: 11px; color: #475569; }

    /* ══════════════════════════════════════════════════════
       PAGE HEADERS
    ══════════════════════════════════════════════════════ */
    QLabel#pageTitle {
        font-size: 22px;
        font-weight: 800;
        color: #F1F5F9;
        letter-spacing: -0.3px;
    }

    QLabel#pageSubtitle {
        font-size: 12px;
        color: #475569;
        font-weight: 400;
        line-height: 1.5;
    }

    /* ══════════════════════════════════════════════════════
       LABELS DE FORMULARIO
    ══════════════════════════════════════════════════════ */
    QLabel#fieldLabel {
        font-size: 11px;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    QLabel#autoValue {
        background-color: #0A1525;
        border: 1px solid #1A3050;
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 12px;
        color: #475569;
        font-weight: 500;
    }

    /* ══════════════════════════════════════════════════════
       INPUTS
    ══════════════════════════════════════════════════════ */
    QLineEdit, QTextEdit {
        background-color: #0A1525;
        border: 1px solid #1A3050;
        border-radius: 7px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: 400;
        color: #E2E8F0;
        selection-background-color: #10B981;
        selection-color: #000;
        min-height: 34px;
    }

    QLineEdit:focus, QTextEdit:focus {
        border-color: #10B981;
        background-color: #091827;
        color: #F1F5F9;
    }

    QLineEdit:disabled, QTextEdit:disabled {
        background-color: #080F1A;
        color: #1E3A5F;
        border-color: #0F1E35;
    }

    QLineEdit:hover:!focus, QTextEdit:hover:!focus {
        border-color: #2D4F72;
    }

    /* ══════════════════════════════════════════════════════
       COMBOBOX
    ══════════════════════════════════════════════════════ */
    QComboBox {
        background-color: #0A1525;
        border: 1px solid #1A3050;
        border-radius: 7px;
        padding: 8px 32px 8px 12px;
        font-size: 13px;
        font-weight: 400;
        color: #E2E8F0;
        min-height: 34px;
    }

    QComboBox:focus {
        border-color: #10B981;
        background-color: #091827;
    }

    QComboBox:hover:!focus { border-color: #2D4F72; }

    QComboBox:disabled {
        background-color: #080F1A;
        color: #1E3A5F;
        border-color: #0F1E35;
    }

    QComboBox::drop-down {
        border: none;
        border-left: 1px solid #1A3050;
        width: 30px;
        border-radius: 0 7px 7px 0;
        background-color: #0D1B2E;
    }

    QComboBox::drop-down:hover {
        background-color: #152840;
    }

    QComboBox::down-arrow {
        width: 10px;
        height: 10px;
    }

    QComboBox QAbstractItemView {
        background-color: #0D1B2E;
        border: 1px solid #1A3050;
        border-radius: 7px;
        color: #CBD5E1;
        padding: 4px;
        outline: none;
        selection-background-color: #0F2238;
        selection-color: #10B981;
    }

    QComboBox QAbstractItemView::item {
        padding: 7px 12px;
        border-radius: 5px;
        min-height: 28px;
    }

    QComboBox QAbstractItemView::item:hover {
        background-color: #152840;
        color: #E2E8F0;
    }

    /* ══════════════════════════════════════════════════════
       DATE EDIT
    ══════════════════════════════════════════════════════ */
    QDateEdit {
        background-color: #0A1525;
        border: 1px solid #1A3050;
        border-radius: 7px;
        padding: 8px 12px;
        font-size: 13px;
        color: #E2E8F0;
        min-height: 34px;
    }

    QDateEdit:focus { border-color: #10B981; background-color: #091827; }
    QDateEdit:hover:!focus { border-color: #2D4F72; }

    QDateEdit::drop-down {
        border: none;
        width: 28px;
    }

    QCalendarWidget {
        background-color: #0D1B2E;
        color: #CBD5E1;
        border: 1px solid #1A3050;
        border-radius: 8px;
    }

    QCalendarWidget QAbstractItemView {
        background-color: #0D1B2E;
        color: #CBD5E1;
        selection-background-color: #10B981;
        selection-color: #000000;
    }

    /* ══════════════════════════════════════════════════════
       SPINBOXES
    ══════════════════════════════════════════════════════ */
    QSpinBox, QDoubleSpinBox {
        background-color: #0A1525;
        border: 1px solid #1A3050;
        border-radius: 7px;
        padding: 8px 12px;
        font-size: 13px;
        color: #E2E8F0;
        min-height: 34px;
    }

    QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #10B981;
        background-color: #091827;
    }

    QSpinBox:hover:!focus, QDoubleSpinBox:hover:!focus {
        border-color: #2D4F72;
    }

    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        border: none;
        border-left: 1px solid #1A3050;
        width: 22px;
        background-color: #0D1B2E;
    }

    QSpinBox::up-button { border-radius: 0 7px 0 0; border-bottom: 1px solid #1A3050; }
    QSpinBox::down-button { border-radius: 0 0 7px 0; }
    QDoubleSpinBox::up-button { border-radius: 0 7px 0 0; border-bottom: 1px solid #1A3050; }
    QDoubleSpinBox::down-button { border-radius: 0 0 7px 0; }

    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #152840;
    }

    /* ══════════════════════════════════════════════════════
       BOTONES
    ══════════════════════════════════════════════════════ */
    QPushButton#primaryButton {
        background-color: #059669;
        border: 1px solid #10B981;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 0.2px;
    }

    QPushButton#primaryButton:hover {
        background-color: #10B981;
        border-color: #34D399;
    }

    QPushButton#primaryButton:pressed {
        background-color: #047857;
        border-color: #059669;
    }

    QPushButton#primaryButton:disabled {
        background-color: #0A2518;
        border-color: #0F3620;
        color: #1A4D2E;
    }

    QPushButton#secondaryButton {
        background-color: transparent;
        border: 1px solid #1A3050;
        border-radius: 8px;
        padding: 9px 20px;
        font-size: 13px;
        font-weight: 600;
        color: #94A3B8;
    }

    QPushButton#secondaryButton:hover {
        background-color: #0F1E35;
        border-color: #2D4F72;
        color: #CBD5E1;
    }

    QPushButton#secondaryButton:pressed {
        background-color: #152840;
    }

    QPushButton#dangerButton {
        background-color: #7F1D1D;
        border: 1px solid #991B1B;
        border-radius: 8px;
        padding: 9px 20px;
        font-size: 13px;
        font-weight: 700;
        color: #FEE2E2;
        letter-spacing: 0.2px;
    }

    QPushButton#dangerButton:hover {
        background-color: #991B1B;
        border-color: #B91C1C;
        color: #FFFFFF;
    }

    QPushButton#dangerButton:pressed {
        background-color: #6B1010;
    }

    /* ══════════════════════════════════════════════════════
       TABLAS
    ══════════════════════════════════════════════════════ */
    QTableWidget {
        background-color: #080F1A;
        alternate-background-color: #0A1422;
        color: #CBD5E1;
        gridline-color: #0F1E35;
        border: 1px solid #1A3050;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 400;
        selection-background-color: #0F2238;
        selection-color: #E2E8F0;
    }

    QTableWidget::item {
        padding: 7px 12px;
        border: none;
        border-bottom: 1px solid #0D1A2C;
    }

    QTableWidget::item:selected {
        background-color: #0F2238;
        color: #E2E8F0;
        border-left: 2px solid #10B981;
    }

    QTableWidget::item:hover {
        background-color: #0C1930;
    }

    QHeaderView::section {
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #0D1B2E,
            stop:1 #091523
        );
        color: #10B981;
        border: none;
        border-right: 1px solid #0F1E35;
        border-bottom: 2px solid #10B981;
        padding: 9px 12px;
        font-weight: 700;
        font-size: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    QHeaderView::section:first { border-left: none; }
    QHeaderView::section:last  { border-right: none; }

    /* ══════════════════════════════════════════════════════
       SCROLL BARS
    ══════════════════════════════════════════════════════ */
    QScrollBar:vertical {
        background: #060D1A;
        width: 6px;
        margin: 0px;
        border-radius: 3px;
    }

    QScrollBar::handle:vertical {
        background: #1A3050;
        border-radius: 3px;
        min-height: 24px;
    }

    QScrollBar::handle:vertical:hover { background: #10B981; }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

    QScrollBar:horizontal {
        background: #060D1A;
        height: 6px;
        margin: 0px;
        border-radius: 3px;
    }

    QScrollBar::handle:horizontal {
        background: #1A3050;
        border-radius: 3px;
        min-width: 24px;
    }

    QScrollBar::handle:horizontal:hover { background: #10B981; }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

    /* ══════════════════════════════════════════════════════
       DROP ZONE
    ══════════════════════════════════════════════════════ */
    QWidget#dropZone {
        background-color: #0A1525;
        border: 2px dashed #1A3050;
        border-radius: 12px;
    }

    QWidget#dropZoneActive {
        background-color: #091827;
        border: 2px dashed #10B981;
        border-radius: 12px;
    }

    QWidget#dropZoneLoaded {
        background-color: #061A10;
        border: 2px solid #10B981;
        border-radius: 12px;
    }

    /* ══════════════════════════════════════════════════════
       SEPARADORES
    ══════════════════════════════════════════════════════ */
    QFrame[frameShape="4"] { color: #0F1E35; }
    QFrame[frameShape="5"] { color: #0F1E35; }

    /* ══════════════════════════════════════════════════════
       TOOLTIPS
    ══════════════════════════════════════════════════════ */
    QToolTip {
        background-color: #0D1B2E;
        border: 1px solid #1A3050;
        color: #CBD5E1;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
    }

    /* ══════════════════════════════════════════════════════
       MESSAGE BOX
    ══════════════════════════════════════════════════════ */
    QMessageBox {
        background-color: #0D1B2E;
    }

    QMessageBox QLabel {
        color: #CBD5E1;
        font-size: 13px;
        min-width: 300px;
    }

    QMessageBox QPushButton {
        background-color: #059669;
        border: 1px solid #10B981;
        border-radius: 7px;
        padding: 7px 20px;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 12px;
        min-width: 80px;
    }

    QMessageBox QPushButton:hover { background-color: #10B981; }

    /* ══════════════════════════════════════════════════════
       BADGES DE ESTADO
    ══════════════════════════════════════════════════════ */
    QLabel#badgeOK {
        background-color: #061A10;
        border: 1px solid #059669;
        border-radius: 5px;
        padding: 2px 10px;
        font-size: 10px;
        color: #10B981;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    QLabel#badgeREVISAR {
        background-color: #1A0F00;
        border: 1px solid #D97706;
        border-radius: 5px;
        padding: 2px 10px;
        font-size: 10px;
        color: #F59E0B;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* ══════════════════════════════════════════════════════
       BADGES DE CLASIFICACIÓN (Evaluaciones)
    ══════════════════════════════════════════════════════ */
    QLabel#badgeExcelente {
        background-color: #052E16;
        border: 1px solid #16A34A;
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        color: #4ADE80;
        letter-spacing: 0.3px;
    }

    QLabel#badgeAceptable {
        background-color: #1A2E05;
        border: 1px solid #65A30D;
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        color: #A3E635;
        letter-spacing: 0.3px;
    }

    QLabel#badgeCondicionado {
        background-color: #1A1100;
        border: 1px solid #D97706;
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        color: #FCD34D;
        letter-spacing: 0.3px;
    }

    QLabel#badgePeligro {
        background-color: #1A0505;
        border: 1px solid #DC2626;
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        color: #F87171;
        letter-spacing: 0.3px;
    }

    QLabel#badgeNeutral {
        background-color: #0A1525;
        border: 1px solid #1A3050;
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        color: #475569;
        letter-spacing: 0.3px;
    }

    /* ══════════════════════════════════════════════════════
       TABS (Etiquetas)
    ══════════════════════════════════════════════════════ */
    QTabWidget#etiquetasTabs::pane {
        background-color: #060D1A;
        border: 1px solid #1A3050;
        border-radius: 8px;
        top: -1px;
    }

    QTabWidget#etiquetasTabs > QTabBar::tab {
        background-color: #0A1525;
        color: #475569;
        border: 1px solid #1A3050;
        border-bottom: none;
        border-radius: 7px 7px 0 0;
        padding: 9px 22px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 2px;
    }

    QTabWidget#etiquetasTabs > QTabBar::tab:selected {
        background-color: #0D1B2E;
        color: #10B981;
        border-color: #1A3050;
        border-bottom-color: #0D1B2E;
        font-weight: 700;
    }

    QTabWidget#etiquetasTabs > QTabBar::tab:hover:!selected {
        background-color: #0F1E35;
        color: #94A3B8;
    }

    /* ══════════════════════════════════════════════════════
       DIALOG (Cambiar Excel - modal de contraseña)
    ══════════════════════════════════════════════════════ */
    QDialog {
        background-color: #0D1B2E;
        border: 1px solid #1A3050;
    }

    /* ══════════════════════════════════════════════════════
       SCROLL AREA
    ══════════════════════════════════════════════════════ */
    QScrollArea {
        background: transparent;
        border: none;
    }

    QScrollArea > QWidget > QWidget {
        background: transparent;
    }

    /* ══════════════════════════════════════════════════════
       CHECKBOX
    ══════════════════════════════════════════════════════ */
    QCheckBox {
        color: #94A3B8;
        font-size: 13px;
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #1A3050;
        border-radius: 4px;
        background-color: #0A1525;
    }

    QCheckBox::indicator:checked {
        background-color: #059669;
        border-color: #10B981;
    }

    QCheckBox::indicator:hover {
        border-color: #2D4F72;
    }
    """ + f"""
    /* ══════════════════════════════════════════════════════
       FLECHAS SPINBOX / COMBOBOX (generadas en runtime)
    ══════════════════════════════════════════════════════ */
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url({_up});
        width: 8px;
        height: 6px;
    }}

    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url({_dn});
        width: 8px;
        height: 6px;
    }}

    QComboBox::down-arrow, QDateEdit::down-arrow {{
        image: url({_dn});
        width: 8px;
        height: 6px;
    }}
    """
