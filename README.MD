# Sistema de Gestión Excel + PDF + GUI en Python

## Objetivo

Crear una aplicación de escritorio en Python que:

* Lea archivos Excel
* Relacione múltiples hojas internas
* Autocomplete información
* Genere reportes PDF
* Permita exportar Excel/PDF
* Tenga interfaz gráfica moderna
* Funcione como `.exe`
* No requiera Python instalado
* Oculte archivos internos al usuario
* Sea fácil de instalar y usar

---

# Arquitectura General

## Flujo del sistema

```text
Usuario
   ↓
Sistema.exe
   ↓
Interfaz gráfica (PySide6)
   ↓
Motor de lógica Python
   ↓
Excel Base (AppData)
   ↓
Generación PDF / Exportaciones
```

---

# Tecnologías Principales

| Área           | Librería    |
| -------------- | ----------- |
| GUI            | PySide6     |
| Excel          | pandas      |
| Excel avanzado | openpyxl    |
| PDF            | reportlab   |
| Configuración  | json        |
| Ejecutable     | PyInstaller |
| Instalador     | Inno Setup  |

---

# Librerías Python

## Instalar dependencias

```bash
pip install pandas
pip install openpyxl
pip install pyside6
pip install reportlab
pip install pyinstaller
```

---

# Arquitectura de Carpetas (Desarrollo)

```text
project/
│
├── app/
│   ├── gui/
│   ├── services/
│   ├── models/
│   ├── utils/
│   ├── exports/
│   ├── assets/
│   └── main.py
│
├── database/
│   └── database.xlsx
│
├── reports/
│
├── backups/
│
├── requirements.txt
│
└── README.md
```

---

# Arquitectura Final para Usuario

El usuario SOLO verá:

```text
Sistema.exe
```

o:

```text
Setup.exe
```

---

# Carpetas Internas Automáticas

El sistema creará automáticamente:

```text
C:\Users\USER\AppData\Local\MiSistema\
```

## Estructura interna

```text
/data
/reports
/backups
/config
```

---

# Archivos Internos

## Base Excel

```text
database.xlsx
```

## Configuración

```text
settings.json
```

## Reportes PDF

```text
Reporte_2026_05.pdf
```

---

# Manejo de Excel

## Librerías

* pandas
* openpyxl

## Funciones

* Leer múltiples hojas
* Relacionar información
* Buscar datos
* Actualizar celdas
* Validar información
* Exportar Excel
* Autocompletado

---

# Relaciones Entre Hojas

Ejemplo:

## Hoja Clientes

| id_cliente | nombre |
| ---------- | ------ |
| 1          | Steven |

## Hoja Ventas

| id_cliente | total |
| ---------- | ----- |
| 1          | 5000  |

El sistema:

* detecta ID
* busca cliente
* autocompleta datos

---

# Interfaz Gráfica

## Framework

```text
PySide6 (Qt)
```

## Funciones GUI

* Formularios
* Tablas
* Botones
* Filtros
* Búsqueda
* Exportar PDF
* Exportar Excel
* Dashboards
* Temas oscuros
* Ventanas modernas

---

# Generación de PDFs

## Librería

```text
reportlab
```

## Funciones

* Reportes empresariales
* Tablas
* Logos
* Encabezados
* Totales
* Estadísticas
* Exportación automática

---

# Exportaciones

El usuario podrá:

## Exportar Excel

```text
Guardar como...
```

## Exportar PDF

```text
Guardar reporte...
```

Seleccionando:

* Desktop
* USB
* Downloads
* Ruta personalizada

---

# Ejecutable Final

## Generar .exe

```bash
pyinstaller --onefile --windowed app/main.py
```

## Parámetros

| Parámetro  | Función           |
| ---------- | ----------------- |
| --onefile  | Un solo archivo   |
| --windowed | Sin consola negra |

---

# Resultado Final

```text
Sistema.exe
```

---

# Instalador Profesional

## Herramienta

```text
Inno Setup
```

## Funciones

* Instalar sistema
* Crear accesos directos
* Configurar carpetas
* Instalar automáticamente

---

# Requisitos del Usuario

## El usuario NO necesita:

* Python
* pip
* Visual Studio
* Librerías
* Consola

Todo viaja integrado dentro del `.exe`.

---

# Ventajas de esta Arquitectura

* Profesional
* Fácil de usar
* Portable
* Datos ocultos
* Fácil mantenimiento
* Fácil actualización
* No depende de Python instalado

---

# Escalabilidad

## Para proyectos pequeños/medianos

Excel funciona correctamente.

## Para proyectos grandes futuros

Migrar a:

```text
SQLite
```

sin cambiar demasiado la interfaz.

---

# Recomendación Final

Usar:

* Excel como almacenamiento principal inicial
* AppData para datos ocultos
* PySide6 para GUI moderna
* PyInstaller para `.exe`
* Inno Setup para instalador
* Arquitectura modular desde el inicio
    