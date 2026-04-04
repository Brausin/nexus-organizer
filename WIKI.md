# NEXUS

Organizador de archivos inteligente por linea de comandos. Analiza carpetas, clasifica archivos por extension y nombre, y los mueve a una estructura ordenada.

## Que hace

NEXUS toma una carpeta desordenada y la organiza automaticamente en subcarpetas por categoria. Soporta 13 categorias con deteccion inteligente de subcategorias como facturas, contratos, CVs, screenshots y wallpapers.

## Comandos principales

- `organize` — Clasifica y mueve archivos a carpetas organizadas
- `watch` — Monitoreo en tiempo real, organiza archivos nuevos al instante
- `rollback` — Deshace cualquier movimiento, uno a uno o todos a la vez
- `search` — Encuentra archivos dentro de la estructura organizada
- `stats` — Resumen visual por categoria y tamano
- `init` — Genera configuracion por defecto

## Uso rapido

```bash
python nexus.py organize ~/Downloads
python nexus.py watch ~/Downloads
python nexus.py rollback --steps 10
python nexus.py search "factura" --folder ~/Organizado
```

## Modo simulacion

Previsualiza los cambios sin mover nada:

```bash
python nexus.py organize ~/Downloads --dry-run
```

## Configuracion

Todo se controla desde `nexus_config.json`: carpeta vigilada, destino, categorias personalizadas, patrones de exclusion y nivel de log.

## Stack

- Python 3.7+
- watchdog para monitoreo del filesystem
- colorama para colores ANSI en Windows
- Sin base de datos, historial en JSON

## Plataformas

Windows, macOS y Linux. En Windows incluye scripts `.bat` para instalacion y uso rapido con doble clic.
