# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y el proyecto usa [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] — 2025-04-02 · Brausin

### Añadido
- Comando `organize` con soporte para carpeta origen y destino personalizados
- Comando `watch` para monitoreo en tiempo real con `watchdog`
- Comando `rollback` para revertir movimientos (parcial o total)
- Comando `search` con soporte para patrones glob
- Comando `stats` con resumen por categoría y tamaño
- Comando `init` para generar `nexus_config.json` con valores por defecto
- 13 categorías de archivos configurables vía JSON
- Subcategorías inteligentes por nombre: Facturas, Contratos, CVs, Screenshots, Wallpapers
- Modo simulación `--dry-run` para previsualizar cambios sin moverlos
- Modo recursivo `--recursive` para incluir subdirectorios
- Historial persistente en `.nexus_history.json`
- Colores ANSI con fallback graceful en terminales sin soporte
- Scripts `.bat` para uso rápido en Windows
