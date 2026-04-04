<div align="center">

```
 ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
 ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
 ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
 ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
 ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

**Smart File Organizer** — Organiza tu caos en segundos.

[![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0ea5e9?style=flat-square)](https://github.com/Brausin/nexus-organizer)
[![Version](https://img.shields.io/badge/Version-1.0.0-a855f7?style=flat-square)](CHANGELOG.md)


</div>

---

## ¿Qué es NEXUS?

NEXUS es un organizador de archivos inteligente por línea de comandos, desarrollado por **[Brausin](https://github.com/Brausin)**. Analiza una carpeta, clasifica cada archivo por extensión y nombre, y los mueve a una estructura ordenada de subcarpetas — todo en segundos, sin configuración previa y con soporte para deshacer cualquier cambio.

```
Descargas/                         Descargas/
├── presupuesto.xlsx                ├── Documentos/
├── foto_vacaciones.jpg    ──►      │   └── Facturas/
├── factura_marzo.pdf               │       └── factura_marzo.pdf
├── cancion.mp3                     ├── Hojas_de_Calculo/
├── pelicula.mkv                    │   └── presupuesto.xlsx
└── setup.exe                       ├── Imagenes/
                                    │   └── foto_vacaciones.jpg
                                    ├── Audio/
                                    │   └── cancion.mp3
                                    ├── Videos/
                                    │   └── pelicula.mkv
                                    └── Ejecutables/
                                        └── setup.exe
```

---

## Características

- **13 categorías** con reconocimiento automático por extensión
- **Subcategorías inteligentes** — detecta facturas, contratos, CVs, screenshots y wallpapers por nombre
- **Monitoreo en tiempo real** — vigila una carpeta y organiza los archivos nuevos al instante
- **Rollback completo** — deshace cualquier movimiento, uno a uno o todos a la vez
- **Modo simulación** — previsualiza los cambios sin mover nada (`--dry-run`)
- **Búsqueda integrada** — encuentra archivos dentro de tu estructura organizada
- **Estadísticas** — resumen visual por categoría y tamaño
- **Configuración JSON** — personaliza categorías, exclusiones y comportamiento
- **Sin base de datos** — historial guardado en un simple archivo `.json`
- **Multiplataforma** — Windows, macOS y Linux

---

## Instalación

### Requisitos

- Python 3.7 o superior

### 1. Clona el repositorio

```bash
git clone https://github.com/Brausin/nexus-organizer.git
cd nexus-organizer
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

> `watchdog` y `colorama` son opcionales. Sin ellas, todos los comandos funcionan excepto `watch`.

### Windows — instalación con doble clic

Ejecuta **`instalar.bat`** y listo.

---

## Uso

### Organizar una carpeta

```bash
python nexus.py organize ~/Downloads
```

```bash
# Especificar carpeta destino
python nexus.py organize ~/Downloads --dest ~/Organizado

# Simular sin mover archivos
python nexus.py organize ~/Downloads --dry-run

# Incluir subcarpetas
python nexus.py organize ~/Downloads --recursive
```

### Monitoreo en tiempo real

```bash
python nexus.py watch ~/Downloads
python nexus.py watch ~/Downloads --dest ~/Organizado --delay 5
```

### Deshacer cambios

```bash
# Revertir todos los movimientos
python nexus.py rollback

# Revertir los últimos N movimientos
python nexus.py rollback --steps 10
```

### Buscar archivos

```bash
python nexus.py search "factura" --folder ~/Organizado
python nexus.py search "*.pdf" --folder ~/Organizado
```

### Ver estadísticas

```bash
python nexus.py stats ~/Organizado
```

### Generar configuración por defecto

```bash
python nexus.py init
```

### Windows — uso rápido

Doble clic en **`organizar.bat`** para organizar tu carpeta de Descargas al instante.

---

## Categorías

| Categoría | Extensiones |
|---|---|
| Documentos | `.pdf` `.doc` `.docx` `.txt` `.epub` `.md` … |
| Imagenes | `.jpg` `.png` `.gif` `.webp` `.svg` `.heic` … |
| Videos | `.mp4` `.mkv` `.avi` `.mov` `.webm` … |
| Audio | `.mp3` `.wav` `.flac` `.aac` `.ogg` … |
| Comprimidos | `.zip` `.rar` `.7z` `.tar.gz` `.iso` … |
| Ejecutables | `.exe` `.msi` `.dmg` `.apk` `.deb` … |
| Hojas de Cálculo | `.xlsx` `.csv` `.ods` `.numbers` … |
| Presentaciones | `.pptx` `.ppt` `.key` `.odp` |
| Código | `.py` `.js` `.ts` `.html` `.go` `.rs` … |
| Datos | `.json` `.xml` `.yaml` `.sql` `.db` … |
| Fuentes | `.ttf` `.otf` `.woff` `.woff2` |
| Torrents | `.torrent` |
| Otros | Todo lo que no encaje en ninguna categoría |

---

## Configuración

El archivo `nexus_config.json` controla el comportamiento de NEXUS. Puedes editarlo manualmente o generarlo con `python nexus.py init`.

```jsonc
{
  "watch_folder": "~/Downloads",      // Carpeta vigilada por defecto
  "dest_folder": "",                  // Destino (vacío = misma carpeta)
  "organize_subfolders": false,       // Incluir subdirectorios
  "monitor_delay_seconds": 3,         // Espera antes de mover (watch)
  "dry_run": false,                   // Modo simulación global
  "log_level": "INFO",                // DEBUG | INFO | WARNING | ERROR
  "exclude_patterns": [               // Archivos a ignorar
    ".DS_Store", "Thumbs.db"
  ],
  "categories": { ... }               // Personaliza o añade categorías
}
```

---

## Estructura del proyecto

```
nexus-organizer/
├── nexus.py              # Aplicación principal
├── nexus_config.json     # Configuración por defecto
├── requirements.txt      # Dependencias Python
├── instalar.bat          # Setup rápido en Windows
├── organizar.bat         # Organizar Descargas con doble clic
├── nexus.bat             # CLI wrapper para Windows
├── CHANGELOG.md          # Historial de versiones
└── LICENSE               # Licencia MIT
```

---

## Tecnologías

| Herramienta | Uso |
|---|---|
| [Python 3.7+](https://python.org) | Lenguaje principal |
| [pathlib](https://docs.python.org/3/library/pathlib.html) | Manejo multiplataforma de rutas |
| [argparse](https://docs.python.org/3/library/argparse.html) | Interfaz de línea de comandos |
| [watchdog](https://github.com/gorakhargosh/watchdog) | Monitoreo del sistema de archivos |
| [colorama](https://github.com/tartley/colorama) | Colores ANSI en Windows |
| JSON | Configuración y historial de movimientos |


---

## Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

Desarrollado por **[Brausin](https://github.com/Brausin)**

</div>
