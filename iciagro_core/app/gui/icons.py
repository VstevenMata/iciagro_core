"""SVG navigation icons for ICIAGRO CORE."""
from __future__ import annotations

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_WRAP = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
    ' fill="none" stroke="{c}" stroke-width="2"'
    ' stroke-linecap="round" stroke-linejoin="round">{b}</svg>'
)

_BODIES: dict[str, str] = {
    "carga": (
        '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<polyline points="9 22 9 12 15 12 15 22"/>'
    ),
    "proveedores": (
        '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>'
        '<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
    ),
    "evaluacion": (
        '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02'
        ' 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
    ),
    "clientes": (
        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "recepcion": (
        '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>'
        '<path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2'
        'v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>'
    ),
    "produccion": (
        '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
        '<polyline points="2 17 12 22 22 17"/>'
        '<polyline points="2 12 12 17 22 12"/>'
    ),
    "terminado": (
        '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0'
        'l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0'
        'l7-4A2 2 0 0 0 21 16z"/>'
        '<polyline points="3.27 6.96 12 12.01 20.73 6.96"/>'
        '<line x1="12" y1="22.08" x2="12" y2="12"/>'
    ),
    "expedicion": (
        '<rect x="1" y="3" width="15" height="13"/>'
        '<polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>'
        '<circle cx="5.5" cy="18.5" r="2.5"/>'
        '<circle cx="18.5" cy="18.5" r="2.5"/>'
    ),
    "retiro": (
        '<polyline points="1 4 1 10 7 10"/>'
        '<path d="M3.51 15a9 9 0 1 0 .49-3.99"/>'
    ),
    "etiquetas": (
        '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10'
        'l8.59 8.59a2 2 0 0 1 0 2.82z"/>'
        '<line x1="7" y1="7" x2="7.01" y2="7"/>'
    ),
    "reporte": (
        '<line x1="18" y1="20" x2="18" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/>'
    ),
    "warning": (
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3'
        'L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
}


def _make_pixmap(key: str, color: str, size: int) -> QPixmap:
    body = _BODIES.get(key, "")
    svg = _WRAP.format(c=color, b=body).encode()
    renderer = QSvgRenderer(QByteArray(svg))
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    renderer.render(p)
    p.end()
    return px


def make_icon(key: str, color: str = "#64748B", size: int = 18) -> QIcon:
    return QIcon(_make_pixmap(key, color, size))
