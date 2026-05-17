
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QKeySequence, QAction
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ExcelView(QMainWindow):
    """Vista estilo Excel moderna y elegante."""

    def __init__(self, rows: int = 100, columns: int = 20) -> None:
        super().__init__()

        self.setObjectName("excelView")
        self.setWindowTitle("Hoja de Cálculo - ICIAGRO")
        self.resize(1300, 750)

        # =========================
        # CENTRAL
        # =========================
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        # =========================
        # TABLE
        # =========================
        self.table = QTableWidget()
        self.table.setRowCount(rows)
        self.table.setColumnCount(columns)

        central_layout.addWidget(self.table)

        # =========================
        # DATA
        # =========================
        self._data: List[List[Optional[str]]] = [
            [None for _ in range(columns)] for _ in range(rows)
        ]

        self.copy_data: List[List[str]] = []

        # =========================
        # SETUP
        # =========================
        self._setup_headers()
        self._setup_grid()
        self._apply_excel_style()
        self._init_data()
        self._setup_shortcuts()

    # =========================================================
    # HEADERS
    # =========================================================
    def _setup_headers(self) -> None:
        """Configura headers tipo Excel."""

        # Columnas A, B, C...
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem(self._column_number_to_letter(col))
            self.table.setHorizontalHeaderItem(col, item)

        # Filas 1,2,3...
        for row in range(self.table.rowCount()):
            item = QTableWidgetItem(str(row + 1))
            self.table.setVerticalHeaderItem(row, item)

    def _column_number_to_letter(self, col: int) -> str:
        """Convierte índice a letras Excel."""

        result = ""

        while col >= 0:
            result = chr(ord("A") + (col % 26)) + result
            col = col // 26 - 1

        return result

    # =========================================================
    # GRID
    # =========================================================
    def _setup_grid(self) -> None:
        """Configura líneas."""

        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)

    # =========================================================
    # DATA
    # =========================================================
    def _init_data(self) -> None:
        """Datos iniciales."""

        self._data[0][0] = "Nombre"
        self._data[0][1] = "Edad"
        self._data[0][2] = "Ciudad"

        self._data[1][0] = "Juan"
        self._data[1][1] = "25"
        self._data[1][2] = "San José"

        self._data[2][0] = "Ana"
        self._data[2][1] = "30"
        self._data[2][2] = "Alajuela"

        self._data[3][0] = "Carlos"
        self._data[3][1] = "22"
        self._data[3][2] = "Heredia"

        for row in range(len(self._data)):
            for col in range(len(self._data[row])):

                value = self._data[row][col]

                if value is not None:
                    item = QTableWidgetItem(str(value))

                    # Texto negro
                    item.setForeground(QColor("#000000"))

                    # Centrar headers
                    if row == 0:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.table.setItem(row, col, item)

    # =========================================================
    # STYLE
    # =========================================================
    def _apply_excel_style(self) -> None:
        """Aplica estilo moderno."""

        # Fuente
        font = self.table.font()
        font.setFamily("Segoe UI")
        font.setPointSize(10)

        self.table.setFont(font)

        # Tamaños
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setDefaultSectionSize(140)

        # Resize
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )

        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.Fixed
        )

        # Selección
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        # Alternancia
        self.table.setAlternatingRowColors(True)

        # Editar
        self.table.setEditTriggers(
            QTableWidget.DoubleClicked
            | QTableWidget.EditKeyPressed
        )

        # Paleta
        palette = self.table.palette()

        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.AlternateBase, QColor("#F7F9FB"))
        palette.setColor(QPalette.Text, QColor("#000000"))

        self.table.setPalette(palette)

        # CSS COMPLETO
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F7F9FB;
                color: #000000;
                gridline-color: #D6DCE5;
                border: 1px solid #C8D0DA;
                selection-background-color: #D6EAF8;
                selection-color: #000000;
                font-size: 11px;
            }

            QTableWidget::item {
                padding: 6px;
                border: none;
                color: #000000;
            }

            QTableWidget::item:selected {
                background-color: #AED6F1;
                color: #000000;
            }

            QHeaderView::section {
                background-color: #E9EEF4;
                color: #000000;
                border: 1px solid #C8D0DA;
                padding: 6px;
                font-weight: bold;
                font-size: 11px;
            }

            QScrollBar:vertical {
                background: #F0F2F5;
                width: 12px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #C0C7D1;
                border-radius: 5px;
                min-height: 25px;
            }

            QScrollBar::handle:vertical:hover {
                background: #AAB2BD;
            }

            QScrollBar:horizontal {
                background: #F0F2F5;
                height: 12px;
                margin: 0px;
            }

            QScrollBar::handle:horizontal {
                background: #C0C7D1;
                border-radius: 5px;
                min-width: 25px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #AAB2BD;
            }

            QCornerButton::section {
                background-color: #E9EEF4;
                border: 1px solid #C8D0DA;
            }
        """)

    # =========================================================
    # SHORTCUTS
    # =========================================================
    def _setup_shortcuts(self) -> None:
        """Atajos Ctrl+C / Ctrl+V."""

        copy_action = QAction(self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_to_clipboard)
        self.addAction(copy_action)

        paste_action = QAction(self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_from_clipboard)
        self.addAction(paste_action)

    # =========================================================
    # COPY
    # =========================================================
    def copy_to_clipboard(self) -> None:
        """Copia celdas."""

        selected_ranges = self.table.selectedRanges()

        if not selected_ranges:
            return

        copied_text = ""

        for selected_range in selected_ranges:

            for row in range(
                selected_range.topRow(),
                selected_range.bottomRow() + 1
            ):

                row_data = []

                for col in range(
                    selected_range.leftColumn(),
                    selected_range.rightColumn() + 1
                ):

                    item = self.table.item(row, col)

                    row_data.append(item.text() if item else "")

                copied_text += "\t".join(row_data) + "\n"

        QApplication.clipboard().setText(copied_text)

    # =========================================================
    # PASTE
    # =========================================================
    def paste_from_clipboard(self) -> None:
        """Pega datos."""

        text = QApplication.clipboard().text()

        if not text:
            return

        rows = text.split("\n")

        current_row = self.table.currentRow()
        current_col = self.table.currentColumn()

        for r, row_text in enumerate(rows):

            if not row_text.strip():
                continue

            cols = row_text.split("\t")

            for c, value in enumerate(cols):

                row_position = current_row + r
                col_position = current_col + c

                if (
                    row_position < self.table.rowCount()
                    and col_position < self.table.columnCount()
                ):
                    item = QTableWidgetItem(value)
                    item.setForeground(QColor("#000000"))

                    self.table.setItem(
                        row_position,
                        col_position,
                        item
                    )

    # =========================================================
    # GET DATA
    # =========================================================
    def get_data(self) -> List[List[Optional[str]]]:
        """Obtiene datos."""

        data: List[List[Optional[str]]] = []

        for row in range(self.table.rowCount()):

            row_data: List[Optional[str]] = []

            for col in range(self.table.columnCount()):

                item = self.table.item(row, col)

                row_data.append(item.text() if item else None)

            data.append(row_data)

        return data


# =============================================================
# MAIN
# =============================================================
if __name__ == "__main__":

    app = QApplication([])

    window = ExcelView()

    window.show()

    app.exec()
