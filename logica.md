# Análisis Completo del Excel — Trazabilidad Hongos El Páramo
## Para integración en ICIAGRO CORE

**Archivo analizado:** `trazabilidad_hongos_el_paramo_listo.xlsm`
**Sistema destino:** ICIAGRO CORE — Python + PySide6 + openpyxl
**Analizado por:** Steven Mata

---

# 1. Resumen General del Archivo

| Propiedad | Valor |
|---|---|
| Formato | `.xlsm` (Excel con macros VBA habilitadas) |
| Contiene VBA | ✅ Sí |
| Total de hojas | 7 |
| Empresa | Lácteos del Páramo |
| Prefijo empresa | `LDP` |
| Formato código trazabilidad | `EMP-CMP-PV-YYJJJ-SEQ` |
| Ejemplo código | `LDP-PEC-01-26068-001` |

---

# 2. Mapa de Hojas

| Hoja | Rol | Activa | Descripción |
|---|---|---|---|
| `Registro_MP` | Principal | ✅ | Registro de recepción de materia prima con trazabilidad |
| `Catalogo_Proveedores` | Referencia | ✅ | Catálogo maestro de proveedores cargado externamente |
| `Hoja1` | Auxiliar | ⚠️ | Lista de proveedores original + lista de responsables |
| `Control` | Configuración | ✅ | Parámetros de control: prefijo, empresa, estados, códigos MP |
| `reprte` | Reporte | ⚠️ | Vista de reporte (datos espejados de Registro_MP) |
| `Instructivo` | Documentación | ✅ | Instrucciones de uso del sistema |
| `Hoja3` | Auxiliar | ⚠️ | Copia de datos de Registro_MP (posiblemente temporal) |

---

# 3. Hoja: `Registro_MP` — PRINCIPAL

## Estructura

| Fila | Contenido |
|---|---|
| 1 | Título: `Registro de Materia Prima y Trazabilidad - Lácteos del Páramo` |
| 2 | Prefijo de lote + Formato del código + Ejemplo |
| 3 | Vacía |
| 4 | Sección: `Captura de recepción` |
| 5 | Encabezados de columnas |
| 6+ | Datos de registros (hasta fila 306) |

## Columnas (Fila 5 — Encabezados)

| Col | Letra | Nombre | Tipo | Entrada |
|---|---|---|---|---|
| 1 | A | Fecha recepción | DATE | Manual |
| 2 | B | Código proveedor | TEXT | Manual (lista desplegable) |
| 3 | C | Nombre del proveedor | TEXT | **FÓRMULA** — VLOOKUP |
| 4 | D | Materia prima | TEXT | **FÓRMULA** — VLOOKUP |
| 5 | E | Cantidad de sacos | NUMBER | Manual |
| 6 | F | Lote proveedor | TEXT | Manual |
| 7 | G | Observaciones | TEXT | Manual |
| 8 | H | Responsable recepción | TEXT | Manual (lista desplegable) |
| 9 | I | Vida útil | TEXT | **FÓRMULA** — VLOOKUP |
| 10 | J | Almacenamiento | TEXT | **FÓRMULA** — VLOOKUP |
| 11 | K | Código MP | TEXT | **FÓRMULA** — VLOOKUP |
| 12 | L | Secuencia día | NUMBER | **FÓRMULA** — COUNTIFS |
| 13 | M | Código lote trazabilidad | TEXT | **FÓRMULA** — Generación automática |
| 14 | N | Revisión lote proveedor | TEXT | **FÓRMULA** — Control duplicados |
| 15 | O | Producto / presentación | TEXT | **FÓRMULA** — VLOOKUP |

## Fórmulas Críticas (a replicar en Python)

### Columna C — Nombre del proveedor
```excel
=IFERROR(VLOOKUP($B6, Catalogo_Proveedores!$A$3:$M$4, 2, FALSE), "")
```
**Python equivalente:**
```python
def get_nombre_proveedor(codigo_proveedor, catalogo_df):
    match = catalogo_df[catalogo_df['Código Proveedor'] == codigo_proveedor]
    return match['Nombre del Proveedor'].values[0] if not match.empty else ""
```

### Columna D — Materia prima
```excel
=IFERROR(VLOOKUP($B6, Catalogo_Proveedores!$A$3:$M$4, 6, FALSE), "")
```
→ Columna 6 del catálogo = `Producto que abastece`

### Columna I — Vida útil
```excel
=IFERROR(VLOOKUP($B6, Catalogo_Proveedores!$A$3:$M$4, 11, FALSE), "")
```
→ Columna 11 del catálogo = `Vida útil`

### Columna J — Almacenamiento
```excel
=IFERROR(VLOOKUP($B6, Catalogo_Proveedores!$A$3:$M$4, 10, FALSE), "")
```
→ Columna 10 del catálogo = `Condiciones de almacenamiento`

### Columna K — Código MP
```excel
=IFERROR(VLOOKUP($B6, Catalogo_Proveedores!$A$3:$M$4, 12, FALSE), "")
```
→ Columna 12 del catálogo = `Código MP`

### Columna L — Secuencia del día (autoincremental por fecha)
```excel
=IF(OR($A6="",$K6=""), "", COUNTIFS($A$6:$A6, $A6, $K$6:$K6, $K6))
```
**Python equivalente:**
```python
def calcular_secuencia_dia(df, fecha, codigo_mp):
    subset = df[(df['Fecha recepción'] == fecha) & (df['Código MP'] == codigo_mp)]
    return len(subset) + 1
```

### Columna M — Código lote trazabilidad ⭐ CRÍTICA
```excel
=IF(OR($A6="",$B6=""), "",
  Control!$B$2 & "-" & $K6 & "-" & RIGHT($B6,2) & "-"
  & TEXT($A6, "YY") & TEXT($A6 - DATE(YEAR($A6),1,0), "000")
  & "-" & TEXT($L6,"000"))
```

**Desglose del código:**
```
LDP  - PEC  - 01  - 26  068  - 001
[1]   [2]    [3]   [4]  [5]   [6]

[1] Prefijo empresa    → Control!B2 = "LDP"
[2] Código MP          → Col K = "PEC"
[3] Últimos 2 del cód  → RIGHT("PROV-PEC-01", 2) = "01"
[4] Año 2 dígitos      → TEXT(fecha, "YY") = "26"
[5] Día juliano 3 dig  → día del año con ceros = "068"
[6] Secuencia 3 dig    → TEXT(secuencia, "000") = "001"
```

**Python equivalente:**
```python
from datetime import datetime

def generar_codigo_trazabilidad(fecha, codigo_proveedor, codigo_mp, secuencia, prefijo="LDP"):
    anno = fecha.strftime("%y")                          # "26"
    dia_juliano = fecha.timetuple().tm_yday              # 68
    dia_str = str(dia_juliano).zfill(3)                  # "068"
    proveedor_sufijo = codigo_proveedor[-2:]             # "01"
    seq_str = str(secuencia).zfill(3)                    # "001"
    return f"{prefijo}-{codigo_mp}-{proveedor_sufijo}-{anno}{dia_str}-{seq_str}"
    # Resultado: LDP-PEC-01-26068-001
```

### Columna N — Revisión lote proveedor (detección de duplicados)
```excel
=IF($F6="", "", IF(COUNTIFS($B$6:$B$304,$B6,$F$6:$F$304,$F6)>1,"REVISAR","OK"))
```
**Python equivalente:**
```python
def revisar_lote_proveedor(df, codigo_proveedor, lote_proveedor):
    duplicados = df[
        (df['Código proveedor'] == codigo_proveedor) &
        (df['Lote proveedor'] == lote_proveedor)
    ]
    return "REVISAR" if len(duplicados) > 1 else "OK"
```

### Columna O — Producto / presentación
```excel
=IFERROR(VLOOKUP($B6, Catalogo_Proveedores!$A$3:$M$4, 13, FALSE), "")
```
→ Columna 13 del catálogo = `Producto / presentación`

---

# 4. Hoja: `Catalogo_Proveedores` — REFERENCIA MAESTRA

## Estructura

| Fila | Contenido |
|---|---|
| 1 | Título: `Catálogo de proveedores cargado desde archivo del usuario` |
| 2 | Encabezados |
| 3+ | Datos de proveedores |

## Columnas del Catálogo (13 columnas)

| # | Nombre | Ejemplo |
|---|---|---|
| 1 | Código Proveedor | `PROV-PEC-01` |
| 2 | Nombre del Proveedor | `Ingredientes Alimentarios Centroamericanos S.A.` |
| 3 | Ubicación | `San José, Costa Rica` |
| 4 | Teléfono | `+506 2222-4587` |
| 5 | Correo electrónico | `ventas@ingredientesca.com` |
| 6 | Producto que abastece | `Pectina cítrica grado alimentario (INS 440)` |
| 7 | Tipo de aditivo | `Estabilizante / gelificante` |
| 8 | Presentación | `Sacos de 25 kg` |
| 9 | Uso en el producto | `Estabilización de yogurt y productos lácteos` |
| 10 | Condiciones de almacenamiento | `Lugar fresco y seco` |
| 11 | Vida útil | `24 meses` |
| 12 | Código MP | `PEC` |
| 13 | Producto / presentación | `Pectina cítrica grado alimentario (INS 440) \| Sacos de 25 kg` |

## Proveedores actuales

| Código | Nombre | MP | Código MP |
|---|---|---|---|
| PROV-PEC-01 | Ingredientes Alimentarios Centroamericanos S.A. | Pectina cítrica grado alimentario (INS 440) | PEC |
| PROV-PEC-02 | Aditivos Naturales de Centroamérica S.A. | Pectina de alta metoxilación (INS 440) | PEC |

---

# 5. Hoja: `Control` — CONFIGURACIÓN

| Parámetro | Valor |
|---|---|
| Prefijo empresa | `LDP` |
| Empresa | `Lácteos del Páramo` |
| Estado: Recibido | `Recibido` |
| Estado: Cuarentena | `Cuarentena` |
| Estado: Liberado | `Liberado` |
| Estado: Rechazado | `Rechazado` |
| Código MP: PEC | `Pectina` |

**Python — Cargar configuración:**
```python
def cargar_configuracion(wb):
    ws = wb['Control']
    config = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:
            config[row[0]] = row[1]
    return config
```

---

# 6. Hoja: `Instructivo` — REGLAS DE NEGOCIO

| # | Función | Descripción |
|---|---|---|
| 1 | Captura en Registro_MP | Registra fecha, código proveedor, cantidad, lote, observaciones, responsable y estado |
| 2 | Autocompletado | Nombre proveedor, materia prima, vida útil y almacenamiento se llenan automáticamente desde Catalogo_Proveedores |
| 3 | Código trazabilidad | Generado automáticamente: `EMP-CMP-PV-YYJJJ-SEQ` |
| 4 | Control duplicados | Columna N marca `REVISAR` si el mismo lote del proveedor aparece más de una vez |
| 5 | Escalabilidad | Al agregar proveedores al catálogo, el sistema sigue funcionando automáticamente |

---

# 7. Hoja: `reprte` — REPORTE

Espeja los datos de `Registro_MP` con los mismos 13 campos.
Empieza en celda `C3` (no en A1).
Funciona como vista previa de reporte.

**En Python:** Esta hoja puede ignorarse y generarse dinámicamente en PDF.

---

# 8. Hoja: `Hoja1` — AUXILIAR

Contiene:
- Lista original de proveedores (mismas 11 columnas que Catálogo pero sin Código MP ni Producto/presentación)
- Lista de responsables válidos: `Camila Gomez`, `Anthony Mata`
- Números del 1 al 10 (posiblemente para dropdowns)

**En Python:** Usar como fuente de lista de responsables para el ComboBox.

---

# 9. Datos de Muestra en `Registro_MP`

| Campo | Registro 1 | Registro 2 |
|---|---|---|
| Fecha | 2026-03-18 | 2026-03-19 |
| Código proveedor | PROV-PEC-01 | PROV-PEC-02 |
| Nombre proveedor | Ingredientes Alimentarios Centroamericanos S.A. | Aditivos Naturales de Centroamérica S.A. |
| Materia prima | Pectina cítrica grado alimentario (INS 440) | Pectina de alta metoxilación (INS 440) |
| Cantidad sacos | 4 | 6 |
| Lote proveedor | A202025 | C303495 |
| Observaciones | Estaba en buen estado | Estaba en mal estado |
| Responsable | Anthony Mata | Camila Gomez |
| Vida útil | 24 meses | 24 meses |
| Almacenamiento | Lugar fresco y seco | Ambiente seco y protegido de humedad |
| Código MP | PEC | PEC |
| Secuencia día | 1 | 1 |
| Código lote | LDP-PEC-01-077-001 | LDP-PEC-02-YY078-001 |
| Revisión | OK | OK |
| Producto/presentación | Pectina cítrica grado alimentario (INS 440) \| Sacos de 25 kg | Pectina de alta metoxilación (INS 440) \| Sacos de 25 kg |

---

# 10. Arquitectura de Lectura en Python

## Servicio principal: `excel_service.py`

```python
import openpyxl
import pandas as pd
from datetime import datetime

class ExcelService:

    REGISTRO_MP_HEADER_ROW = 5
    REGISTRO_MP_DATA_START = 6
    CATALOGO_HEADER_ROW = 2
    CATALOGO_DATA_START = 3

    def __init__(self, ruta_excel: str):
        self.ruta = ruta_excel
        self.wb = openpyxl.load_workbook(ruta_excel, keep_vba=True, data_only=True)
        self.config = self._cargar_config()
        self.catalogo = self._cargar_catalogo()
        self.responsables = self._cargar_responsables()

    def _cargar_config(self) -> dict:
        ws = self.wb['Control']
        config = {'prefijo': 'LDP', 'empresa': '', 'estados': [], 'codigos_mp': {}}
        estados = []
        codigos_mp = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] == 'Prefijo empresa':
                config['prefijo'] = row[1]
            elif row[0] == 'Empresa':
                config['empresa'] = row[1]
            elif row[0] == 'Estados permitidos' or (row[0] is None and row[1]):
                if row[1]:
                    estados.append(row[1])
            elif row[0] and row[1] and row[0] not in ('Prefijo empresa', 'Empresa', 'Parámetros de control', 'Código MP'):
                codigos_mp[row[0]] = row[1]
        config['estados'] = estados
        config['codigos_mp'] = codigos_mp
        return config

    def _cargar_catalogo(self) -> pd.DataFrame:
        ws = self.wb['Catalogo_Proveedores']
        filas = []
        headers = None
        for i, row in enumerate(ws.iter_rows(min_row=self.CATALOGO_HEADER_ROW, values_only=True)):
            if i == 0:
                headers = list(row)
            elif any(v is not None for v in row):
                filas.append(row)
        return pd.DataFrame(filas, columns=headers)

    def _cargar_responsables(self) -> list:
        ws = self.wb['Hoja1']
        responsables = []
        for row in ws.iter_rows(values_only=True):
            val = row[0]
            if val and isinstance(val, str) and not val.startswith('Código'):
                responsables.append(val.strip())
        return responsables

    def cargar_registros(self) -> pd.DataFrame:
        ws = self.wb['Registro_MP']
        headers = [cell.value for cell in ws[self.REGISTRO_MP_HEADER_ROW]]
        filas = []
        for row in ws.iter_rows(
            min_row=self.REGISTRO_MP_DATA_START,
            max_row=ws.max_row,
            values_only=True
        ):
            if any(v is not None for v in row):
                filas.append(row)
        return pd.DataFrame(filas, columns=headers)

    def autocompletar_proveedor(self, codigo_proveedor: str) -> dict:
        """Replica los VLOOKUP del Excel"""
        cat = self.catalogo
        match = cat[cat['Código Proveedor'] == codigo_proveedor]
        if match.empty:
            return {}
        row = match.iloc[0]
        return {
            'nombre_proveedor': row['Nombre del Proveedor'],
            'materia_prima': row['Producto que abastece'],
            'vida_util': row['Vida útil'],
            'almacenamiento': row['Condiciones de almacenamiento'],
            'codigo_mp': row['Código MP'],
            'producto_presentacion': row['Producto / presentación'],
        }

    def generar_codigo_trazabilidad(
        self, fecha: datetime, codigo_proveedor: str,
        codigo_mp: str, secuencia: int
    ) -> str:
        """Replica la fórmula de columna M"""
        prefijo = self.config['prefijo']
        anno = fecha.strftime("%y")
        dia_juliano = str(fecha.timetuple().tm_yday).zfill(3)
        sufijo_proveedor = codigo_proveedor[-2:]
        seq = str(secuencia).zfill(3)
        return f"{prefijo}-{codigo_mp}-{sufijo_proveedor}-{anno}{dia_juliano}-{seq}"

    def calcular_secuencia(
        self, df: pd.DataFrame, fecha: datetime, codigo_mp: str
    ) -> int:
        """Replica la fórmula COUNTIFS de columna L"""
        if df.empty:
            return 1
        subset = df[
            (pd.to_datetime(df['Fecha recepción']).dt.date == fecha.date()) &
            (df['Código MP'] == codigo_mp)
        ]
        return len(subset) + 1

    def revisar_lote(
        self, df: pd.DataFrame, codigo_proveedor: str, lote: str
    ) -> str:
        """Replica la fórmula de columna N"""
        if not lote:
            return ""
        dups = df[
            (df['Código proveedor'] == codigo_proveedor) &
            (df['Lote proveedor'] == lote)
        ]
        return "REVISAR" if len(dups) > 1 else "OK"

    def guardar_registro(self, nuevo_registro: dict):
        """Guarda un nuevo registro en Registro_MP"""
        wb_write = openpyxl.load_workbook(self.ruta, keep_vba=True)
        ws = wb_write['Registro_MP']
        next_row = ws.max_row + 1
        ws.cell(row=next_row, column=1, value=nuevo_registro['fecha'])
        ws.cell(row=next_row, column=2, value=nuevo_registro['codigo_proveedor'])
        ws.cell(row=next_row, column=3, value=nuevo_registro['nombre_proveedor'])
        ws.cell(row=next_row, column=4, value=nuevo_registro['materia_prima'])
        ws.cell(row=next_row, column=5, value=nuevo_registro['cantidad_sacos'])
        ws.cell(row=next_row, column=6, value=nuevo_registro['lote_proveedor'])
        ws.cell(row=next_row, column=7, value=nuevo_registro['observaciones'])
        ws.cell(row=next_row, column=8, value=nuevo_registro['responsable'])
        ws.cell(row=next_row, column=9, value=nuevo_registro['vida_util'])
        ws.cell(row=next_row, column=10, value=nuevo_registro['almacenamiento'])
        ws.cell(row=next_row, column=11, value=nuevo_registro['codigo_mp'])
        ws.cell(row=next_row, column=12, value=nuevo_registro['secuencia'])
        ws.cell(row=next_row, column=13, value=nuevo_registro['codigo_trazabilidad'])
        ws.cell(row=next_row, column=14, value=nuevo_registro['revision_lote'])
        ws.cell(row=next_row, column=15, value=nuevo_registro['producto_presentacion'])
        wb_write.save(self.ruta)

    def exportar_excel(self, df: pd.DataFrame, ruta_destino: str):
        """Exporta los registros a un nuevo Excel limpio"""
        with pd.ExcelWriter(ruta_destino, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Registro_MP', index=False)
```

---

# 11. Exportación con Drag & Drop

## Implementación en PySide6

```python
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent

class DropZoneWidget(QWidget):
    """
    Widget que acepta drag & drop de archivos Excel (.xlsx, .xlsm)
    Al soltar el archivo, lo carga automáticamente en el sistema.
    """

    archivo_cargado = Signal(str)  # Emite la ruta del archivo

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #1E293B;
                border: 2px dashed #334155;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(self)
        self.label = QLabel("Arrastra el archivo Excel aquí\n(.xlsx o .xlsm)")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().endswith(('.xlsx', '.xlsm')) for u in urls):
                self.setStyleSheet("""
                    QWidget {
                        background: #1E293B;
                        border: 2px dashed #3F6B4B;
                        border-radius: 12px;
                    }
                """)
                event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background: #1E293B;
                border: 2px dashed #334155;
                border-radius: 12px;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            ruta = url.toLocalFile()
            if ruta.endswith(('.xlsx', '.xlsm')):
                self.label.setText(f"✅ Cargado: {ruta.split('/')[-1]}")
                self.archivo_cargado.emit(ruta)
                break
        self.setStyleSheet("""
            QWidget {
                background: #1E293B;
                border: 2px dashed #334155;
                border-radius: 12px;
            }
        """)
```

---

# 12. Flujo de Operaciones del Sistema

```text
USUARIO
  │
  ▼
[Drag & Drop Excel] ──────────────────────────┐
  │                                            │
  ▼                                            ▼
ExcelService.load()                    Catalogo_Proveedores
  │                                    Control (config)
  │                                    Hoja1 (responsables)
  ▼
[Formulario de Registro]
  │
  ├─ Campo: Fecha recepción          → Manual
  ├─ Campo: Código proveedor         → ComboBox (desde catálogo)
  ├─ Campo: Nombre proveedor         → Autocompletado (VLOOKUP Python)
  ├─ Campo: Materia prima            → Autocompletado (VLOOKUP Python)
  ├─ Campo: Cantidad de sacos        → Manual numérico
  ├─ Campo: Lote proveedor           → Manual
  ├─ Campo: Observaciones            → Manual texto libre
  ├─ Campo: Responsable recepción    → ComboBox (desde Hoja1)
  ├─ Campo: Vida útil                → Autocompletado
  ├─ Campo: Almacenamiento           → Autocompletado
  ├─ Campo: Código MP                → Autocompletado
  ├─ Campo: Secuencia día            → Calculado (COUNTIFS Python)
  ├─ Campo: Código trazabilidad      → Generado automático
  ├─ Campo: Revisión lote            → Calculado (COUNTIFS Python)
  └─ Campo: Producto/presentación    → Autocompletado
  │
  ▼
[Guardar en Excel]
  │
  ├─ openpyxl.save() → .xlsm original
  │
  └─ [Exportar PDF / Excel]
       │
       ├─ reportlab → PDF profesional
       └─ pandas ExcelWriter → .xlsx limpio
```

---

# 13. Estructura de Módulos Recomendada

```text
iciagro_core/
└── app/
    ├── services/
    │   ├── excel_service.py        ← Lectura/escritura Excel (este módulo)
    │   ├── trazabilidad_service.py ← Generación códigos, VLOOKUP, COUNTIFS
    │   └── pdf_service.py          ← Generación reportes PDF (reportlab)
    │
    ├── models/
    │   ├── registro_mp.py          ← Dataclass del registro
    │   └── proveedor.py            ← Dataclass del proveedor
    │
    ├── gui/
    │   ├── pages/
    │   │   ├── registro_page.py    ← Formulario de registro MP
    │   │   ├── catalogo_page.py    ← Vista del catálogo de proveedores
    │   │   └── reporte_page.py     ← Visualización y exportación
    │   └── components/
    │       ├── drop_zone.py        ← Widget drag & drop
    │       └── tabla_registros.py  ← QTableWidget de registros
    │
    └── utils/
        └── date_utils.py           ← Utilidades de fecha y día juliano
```

---

# 14. Campos Manuales vs Automáticos (Resumen)

| Campo | Manual | Automático | Fuente |
|---|---|---|---|
| Fecha recepción | ✅ | | Usuario |
| Código proveedor | ✅ | | ComboBox catálogo |
| Nombre proveedor | | ✅ | Catálogo col 2 |
| Materia prima | | ✅ | Catálogo col 6 |
| Cantidad de sacos | ✅ | | Usuario |
| Lote proveedor | ✅ | | Usuario |
| Observaciones | ✅ | | Usuario |
| Responsable | ✅ | | ComboBox Hoja1 |
| Vida útil | | ✅ | Catálogo col 11 |
| Almacenamiento | | ✅ | Catálogo col 10 |
| Código MP | | ✅ | Catálogo col 12 |
| Secuencia día | | ✅ | COUNTIFS Python |
| Código trazabilidad | | ✅ | Fórmula Python |
| Revisión lote | | ✅ | COUNTIFS Python |
| Producto/presentación | | ✅ | Catálogo col 13 |

---

# 15. Estados de Revisión de Lote

| Valor | Significado |
|---|---|
| `OK` | El lote del proveedor no está duplicado |
| `REVISAR` | El mismo lote del mismo proveedor aparece más de una vez |
| `""` | No hay lote registrado |

---

# 16. Consideraciones para PDF

El PDF de reporte debe incluir:

- Encabezado con logo + nombre empresa (`Lácteos del Páramo`) + prefijo (`LDP`)
- Filtros aplicados (por fecha, proveedor, estado)
- Tabla con todos los campos de `Registro_MP`
- Resaltar en amarillo filas con `REVISAR` en columna N
- Totales: cantidad de registros, total de sacos recibidos
- Pie de página con fecha de generación y responsable

---

# 17. Notas Importantes para el Desarrollo

1. **El archivo es `.xlsm`** — siempre usar `keep_vba=True` en openpyxl para no corromper las macros.
2. **No re-ejecutar fórmulas** — todas las fórmulas se replican en Python. Los valores se guardan como valores directos, no como fórmulas.
3. **Drag & Drop del catálogo** — el sistema debe permitir cargar un catálogo externo diferente y actualizar automáticamente la hoja `Catalogo_Proveedores`.
4. **Secuencia por día** — la secuencia se reinicia cada día, no es global.
5. **Día juliano** — usar `datetime.timetuple().tm_yday`, no calcularlo manualmente.
6. **Duplicados** — la revisión de duplicados aplica por combinación `(codigo_proveedor, lote_proveedor)`, no solo por lote.

---

*Documento generado para ICIAGRO CORE — Sistema de Gestión y Automatización Empresarial*
*Análisis basado en: `trazabilidad_hongos_el_paramo_listo.xlsm`*