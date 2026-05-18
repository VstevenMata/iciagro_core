from __future__ import annotations

from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class TablaRegistros(QTableWidget):
    """
    Tabla de registros con estilo empresarial oscuro.
    Resalta en amarillo filas con 'REVISAR' en columna de revisión.
    """

    fila_seleccionada = Signal(int)

    COLOR_REVISAR_BG = QColor("#2D1F0A")
    COLOR_REVISAR_TXT = QColor("#8B6F47")
    COLOR_OK_TXT = QColor("#3F6B4B")

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup()

    def _setup(self) -> None:
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.setWordWrap(False)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def cargar_dataframe(self, df: pd.DataFrame) -> None:
        """Carga un DataFrame de pandas en la tabla."""
        self.setSortingEnabled(False)
        self.clearContents()
        self.setRowCount(0)
        self.setColumnCount(0)

        if df.empty:
            return

        headers = [str(h) for h in df.columns]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(len(df))

        col_revision = 13 if len(headers) > 13 else -1

        for row_idx, (_, row) in enumerate(df.iterrows()):
            revision_val = ""
            if col_revision >= 0 and len(row) > col_revision:
                revision_val = str(row.iloc[col_revision] or "").strip()

            for col_idx, val in enumerate(row):
                texto = "" if val is None else str(val)
                item = QTableWidgetItem(texto)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

                if revision_val == "REVISAR":
                    item.setBackground(self.COLOR_REVISAR_BG)
                    if col_idx == col_revision:
                        item.setForeground(self.COLOR_REVISAR_TXT)
                elif revision_val == "OK" and col_idx == col_revision:
                    item.setForeground(self.COLOR_OK_TXT)

                self.setItem(row_idx, col_idx, item)

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def cargar_lista(self, headers: list[str], filas: list[list]) -> None:
        """Carga una lista de filas directamente."""
        import pandas as pd
        if not filas:
            self.clearContents()
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            self.setRowCount(0)
            return
        df = pd.DataFrame(filas, columns=headers)
        self.cargar_dataframe(df)

    def _on_selection_changed(self) -> None:
        selected = self.selectedItems()
        if selected:
            self.fila_seleccionada.emit(self.currentRow())
