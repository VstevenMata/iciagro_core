# Comandos — ICIAGRO CORE

## Correr en desarrollo

```powershell
.\iciagro_core\venv\Scripts\python.exe .\iciagro_core\app\main.py
```

## Actualizar el .exe (cuando hay cambios nuevos)

```powershell
Stop-Process -Name "ICIAGRO_CORE" -Force -ErrorAction SilentlyContinue; .\iciagro_core\venv\Scripts\pyinstaller.exe .\iciagro_core\iciagro.spec --clean
```

> Cierra la app si está abierta y sobreescribe el mismo .exe en `dist\`.

## Correr el .exe

```powershell
.\dist\ICIAGRO_CORE.exe
```
