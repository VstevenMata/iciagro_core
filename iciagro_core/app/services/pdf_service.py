from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ── Paleta empresarial ──
COLOR_FONDO_HEADER = colors.HexColor("#1E293B")
COLOR_FILA_PAR = colors.HexColor("#111827")
COLOR_FILA_IMPAR = colors.HexColor("#0F172A")
COLOR_REVISAR = colors.HexColor("#2D1F0A")
COLOR_BORDE = colors.HexColor("#334155")
COLOR_VERDE = colors.HexColor("#3F6B4B")
COLOR_TEXTO_HEADER = colors.HexColor("#94A3B8")
COLOR_TEXTO = colors.HexColor("#E5E7EB")
COLOR_BLANCO = colors.white


class PDFService:
    """Generador de reportes PDF profesionales con reportlab."""

    def generar_reporte(
        self,
        df: pd.DataFrame,
        ruta_destino: str,
        empresa: str = "Lácteos del Páramo",
        prefijo: str = "LDP",
        filtros: Optional[dict] = None,
        responsable_reporte: str = "",
    ) -> str:
        """
        Genera el PDF de reporte y lo guarda en ruta_destino.
        Retorna la ruta del archivo generado.
        """
        doc = SimpleDocTemplate(
            ruta_destino,
            pagesize=landscape(A4),
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = self._build_styles()
        story = []

        story += self._build_header(empresa, prefijo, styles)
        story.append(Spacer(1, 0.4 * cm))

        if filtros:
            story += self._build_filtros(filtros, styles)
            story.append(Spacer(1, 0.3 * cm))

        story += self._build_summary(df, styles)
        story.append(Spacer(1, 0.4 * cm))

        if not df.empty:
            story.append(self._build_table(df))
        else:
            story.append(Paragraph("No hay registros para mostrar.", styles["body"]))

        story.append(Spacer(1, 0.5 * cm))
        story += self._build_footer(responsable_reporte, styles)

        doc.build(story)
        return ruta_destino

    # ─────────────────── ESTILOS ────────────────────────────────

    def _build_styles(self) -> dict:
        ss = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "title",
                fontName="Helvetica-Bold",
                fontSize=16,
                textColor=COLOR_TEXTO,
                alignment=TA_LEFT,
                spaceAfter=2,
            ),
            "subtitle": ParagraphStyle(
                "subtitle",
                fontName="Helvetica",
                fontSize=10,
                textColor=COLOR_TEXTO_HEADER,
                alignment=TA_LEFT,
                spaceAfter=2,
            ),
            "section": ParagraphStyle(
                "section",
                fontName="Helvetica-Bold",
                fontSize=10,
                textColor=COLOR_VERDE,
                alignment=TA_LEFT,
                spaceAfter=4,
            ),
            "body": ParagraphStyle(
                "body",
                fontName="Helvetica",
                fontSize=9,
                textColor=COLOR_TEXTO,
                alignment=TA_LEFT,
            ),
            "footer": ParagraphStyle(
                "footer",
                fontName="Helvetica",
                fontSize=8,
                textColor=COLOR_TEXTO_HEADER,
                alignment=TA_CENTER,
            ),
            "badge_ok": ParagraphStyle(
                "badge_ok",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=COLOR_VERDE,
                alignment=TA_CENTER,
            ),
            "badge_revisar": ParagraphStyle(
                "badge_revisar",
                fontName="Helvetica-Bold",
                fontSize=8,
                textColor=colors.HexColor("#8B6F47"),
                alignment=TA_CENTER,
            ),
        }

    # ─────────────────── HEADER ─────────────────────────────────

    def _build_header(self, empresa: str, prefijo: str, styles: dict) -> list:
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        return [
            Paragraph(f"REPORTE DE TRAZABILIDAD — {prefijo}", styles["title"]),
            Paragraph(empresa, styles["subtitle"]),
            Paragraph(
                f"Sistema ICIAGRO CORE  ·  Generado: {fecha_str}", styles["subtitle"]
            ),
            HRFlowable(
                width="100%",
                thickness=1,
                color=COLOR_BORDE,
                spaceAfter=0.3 * cm,
            ),
        ]

    # ─────────────────── FILTROS ────────────────────────────────

    def _build_filtros(self, filtros: dict, styles: dict) -> list:
        partes = []
        for k, v in filtros.items():
            if v:
                partes.append(f"<b>{k}:</b> {v}")
        if not partes:
            return []
        texto = "  ·  ".join(partes)
        return [
            Paragraph("Filtros aplicados:", styles["section"]),
            Paragraph(texto, styles["body"]),
        ]

    # ─────────────────── RESUMEN ────────────────────────────────

    def _build_summary(self, df: pd.DataFrame, styles: dict) -> list:
        total = len(df)
        try:
            col_sacos = df.columns[4]
            total_sacos = df[col_sacos].apply(
                lambda x: int(x) if x is not None else 0
            ).sum()
        except Exception:
            total_sacos = 0

        try:
            col_rev = df.columns[13]
            por_revisar = len(df[df[col_rev].astype(str) == "REVISAR"])
        except Exception:
            por_revisar = 0

        resumen = [
            Paragraph("Resumen", styles["section"]),
            Paragraph(
                f"Total de registros: <b>{total}</b>  ·  "
                f"Total sacos recibidos: <b>{total_sacos}</b>  ·  "
                f"Lotes por revisar: <b>{por_revisar}</b>",
                styles["body"],
            ),
        ]
        return resumen

    # ─────────────────── TABLA ──────────────────────────────────

    def _build_table(self, df: pd.DataFrame) -> Table:
        headers = [str(h) for h in df.columns]

        col_widths = self._calcular_anchos(len(headers))

        table_data = [headers]

        for _, row in df.iterrows():
            fila = []
            for val in row:
                texto = "" if val is None else str(val)
                fila.append(texto)
            table_data.append(fila)

        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        style_cmds = [
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_FONDO_HEADER),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_TEXTO_HEADER),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            # Filas
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("TEXTCOLOR", (0, 1), (-1, -1), COLOR_TEXTO),
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.3, COLOR_BORDE),
            ("LINEBELOW", (0, 0), (-1, 0), 1, COLOR_VERDE),
        ]

        # Colores alternos y resaltado REVISAR
        try:
            col_revision = 13  # Columna N (índice 13)
            for row_idx in range(1, len(table_data)):
                bg = COLOR_FILA_PAR if row_idx % 2 == 0 else COLOR_FILA_IMPAR
                style_cmds.append(
                    ("BACKGROUND", (0, row_idx), (-1, row_idx), bg)
                )
                rev_val = str(table_data[row_idx][col_revision]).strip()
                if rev_val == "REVISAR":
                    style_cmds.append(
                        ("BACKGROUND", (0, row_idx), (-1, row_idx), COLOR_REVISAR)
                    )
                    style_cmds.append(
                        (
                            "TEXTCOLOR",
                            (col_revision, row_idx),
                            (col_revision, row_idx),
                            colors.HexColor("#8B6F47"),
                        )
                    )
                    style_cmds.append(
                        (
                            "FONTNAME",
                            (col_revision, row_idx),
                            (col_revision, row_idx),
                            "Helvetica-Bold",
                        )
                    )
        except (IndexError, ValueError):
            pass

        table.setStyle(TableStyle(style_cmds))
        return table

    def _calcular_anchos(self, n_cols: int) -> list:
        page_width = landscape(A4)[0] - 3 * cm
        if n_cols == 0:
            return []
        base = page_width / n_cols
        return [base] * n_cols

    # ─────────────────── FOOTER ─────────────────────────────────

    def _build_footer(self, responsable: str, styles: dict) -> list:
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        texto = f"ICIAGRO CORE — Sistema de Trazabilidad  ·  {fecha_str}"
        if responsable:
            texto += f"  ·  Generado por: {responsable}"
        return [
            HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDE),
            Spacer(1, 0.2 * cm),
            Paragraph(texto, styles["footer"]),
        ]
