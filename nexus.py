#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
 ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
 ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
 ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
 ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
       Smart File Organizer  •  v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXUS — Intelligent file organizer with real-time monitoring.
Usage: python nexus.py [command] [options]
"""

import os
import sys
import json
import shutil
import logging
import argparse
import fnmatch
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict

# ── Optional: watchdog ────────────────────────────────────────────────────────
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object  # type: ignore

# ── Optional: colorama (Windows ANSI support) ─────────────────────────────────
try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANSI COLORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


def clr(text: str, color: str) -> str:
    return f"{color}{text}{C.RESET}"

def info(msg: str):  print(f"  {clr('•', C.CYAN)}  {msg}")
def ok(msg: str):    print(f"  {clr('✔', C.GREEN)}  {msg}")
def warn(msg: str):  print(f"  {clr('⚠', C.YELLOW)}  {msg}")
def err(msg: str):   print(f"  {clr('✖', C.RED)}  {msg}")

def move_msg(src: str, dst: str):
    print(f"  {clr('→', C.BLUE)}  {clr(src, C.WHITE)}  {clr('▸', C.GRAY)}  {clr(dst, C.GREEN)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONFIG_FILE  = "nexus_config.json"
HISTORY_FILE = ".nexus_history.json"
LOG_FILE     = "nexus.log"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEFAULT CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "watch_folder": "~/Downloads",
    "dest_folder": "",
    "organize_subfolders": False,
    "monitor_delay_seconds": 3,
    "dry_run": False,
    "log_level": "INFO",
    "exclude_patterns": [
        ".DS_Store", "Thumbs.db", "desktop.ini",
        ".nexus_history.json", "nexus.log", "nexus_config.json", "nexus.py"
    ],
    "exclude_folders": [
        ".git", "__pycache__", "node_modules"
    ],
    "categories": {
        "Documentos": {
            "emoji": "📄",
            "folder_name": "Documentos",
            "extensions": [
                ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
                ".pages", ".tex", ".md", ".rst", ".epub", ".mobi"
            ],
            "subcategories": {
                "Facturas": {
                    "name_patterns": ["factura", "invoice", "recibo", "receipt", "billing"]
                },
                "Contratos": {
                    "name_patterns": ["contrato", "contract", "acuerdo", "agreement", "nda"]
                },
                "CVs": {
                    "name_patterns": ["cv", "resume", "curriculum", "hoja_de_vida"]
                }
            }
        },
        "Imagenes": {
            "emoji": "🖼️",
            "folder_name": "Imagenes",
            "extensions": [
                ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
                ".tiff", ".tif", ".ico", ".raw", ".cr2", ".nef", ".heic",
                ".heif", ".avif"
            ],
            "subcategories": {
                "Screenshots": {
                    "name_patterns": ["screenshot", "captura", "pantalla", "screen", "snap"]
                },
                "Wallpapers": {
                    "name_patterns": ["wallpaper", "fondo", "background"]
                }
            }
        },
        "Videos": {
            "emoji": "🎬",
            "folder_name": "Videos",
            "extensions": [
                ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
                ".webm", ".m4v", ".3gp", ".ogv", ".ts", ".m2ts", ".vob"
            ],
            "subcategories": {}
        },
        "Audio": {
            "emoji": "🎵",
            "folder_name": "Audio",
            "extensions": [
                ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma",
                ".m4a", ".opus", ".aiff", ".mid", ".midi", ".ape"
            ],
            "subcategories": {}
        },
        "Comprimidos": {
            "emoji": "📦",
            "folder_name": "Comprimidos",
            "extensions": [
                ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
                ".tgz", ".cab", ".iso", ".lz4"
            ],
            "subcategories": {}
        },
        "Ejecutables": {
            "emoji": "💻",
            "folder_name": "Ejecutables",
            "extensions": [
                ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm",
                ".appimage", ".apk", ".ipa", ".bat", ".cmd"
            ],
            "subcategories": {}
        },
        "Hojas_de_Calculo": {
            "emoji": "📊",
            "folder_name": "Hojas_de_Calculo",
            "extensions": [".xlsx", ".xls", ".csv", ".ods", ".numbers", ".tsv"],
            "subcategories": {}
        },
        "Presentaciones": {
            "emoji": "🎯",
            "folder_name": "Presentaciones",
            "extensions": [".pptx", ".ppt", ".odp", ".key"],
            "subcategories": {}
        },
        "Codigo": {
            "emoji": "💾",
            "folder_name": "Codigo",
            "extensions": [
                ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
                ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".php",
                ".rb", ".swift", ".kt", ".dart", ".lua", ".r", ".m", ".sh",
                ".ps1", ".ipynb", ".vue", ".svelte"
            ],
            "subcategories": {}
        },
        "Datos": {
            "emoji": "🗄️",
            "folder_name": "Datos",
            "extensions": [
                ".json", ".xml", ".yaml", ".yml", ".toml", ".ini",
                ".sql", ".db", ".sqlite", ".sqlite3", ".env", ".conf"
            ],
            "subcategories": {}
        },
        "Fuentes": {
            "emoji": "🔤",
            "folder_name": "Fuentes",
            "extensions": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
            "subcategories": {}
        },
        "Torrents": {
            "emoji": "📡",
            "folder_name": "Torrents",
            "extensions": [".torrent"],
            "subcategories": {}
        }
    },
    "others_folder": "Otros"
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Config:
    """Loads, validates, and saves NEXUS configuration."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @classmethod
    def load(cls, path: str = CONFIG_FILE) -> "Config":
        p = Path(path)
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                merged = cls._deep_merge(DEFAULT_CONFIG, user_data)
                return cls(merged)
            except (json.JSONDecodeError, OSError) as e:
                warn(f"No se pudo leer '{path}': {e}. Usando configuración por defecto.")
        return cls(DEFAULT_CONFIG.copy())

    @classmethod
    def _deep_merge(cls, base: dict, override: dict) -> dict:
        result = base.copy()
        for key, val in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = cls._deep_merge(result[key], val)
            else:
                result[key] = val
        return result

    def save(self, path: str = CONFIG_FILE):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def watch_folder(self) -> Path:
        return Path(self._data.get("watch_folder", "~/Downloads")).expanduser()

    @property
    def dest_folder(self) -> Optional[Path]:
        d = self._data.get("dest_folder", "")
        return Path(d).expanduser() if d else None

    @property
    def dry_run(self) -> bool:
        return self._data.get("dry_run", False)

    @property
    def monitor_delay(self) -> int:
        return int(self._data.get("monitor_delay_seconds", 3))

    @property
    def organize_subfolders(self) -> bool:
        return self._data.get("organize_subfolders", False)

    @property
    def exclude_patterns(self) -> List[str]:
        return self._data.get("exclude_patterns", [])

    @property
    def exclude_folders(self) -> List[str]:
        return self._data.get("exclude_folders", [])

    @property
    def categories(self) -> Dict[str, Any]:
        return self._data.get("categories", {})

    @property
    def others_folder(self) -> str:
        return self._data.get("others_folder", "Otros")

    def get_raw(self, key: str, default=None):
        return self._data.get(key, default)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE CLASSIFIER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FileClassifier:
    """
    Classifies a file into (folder_name, subcategory) based on:
      1. Extension matching
      2. Name-pattern matching within subcategories
    """

    def __init__(self, config: Config):
        self.config = config
        # Build fast lookup: extension (lowercase) → category key
        self._ext_map: Dict[str, str] = {}
        for cat_key, cat_data in config.categories.items():
            for ext in cat_data.get("extensions", []):
                self._ext_map[ext.lower()] = cat_key

    def classify(self, filepath: Path) -> Tuple[str, str]:
        """
        Returns (folder_name, subcategory_name).
        subcategory_name is "" when no subcategory matched.
        """
        name_lower = filepath.name.lower()

        # Support compound extensions like .tar.gz
        suffix = filepath.suffix.lower()
        if len(filepath.suffixes) >= 2:
            compound = "".join(filepath.suffixes[-2:]).lower()
            if compound in self._ext_map:
                suffix = compound

        cat_key = self._ext_map.get(suffix)
        if cat_key is None:
            return self.config.others_folder, ""

        cat_data    = self.config.categories[cat_key]
        folder_name = cat_data.get("folder_name", cat_key)
        subcategory = self._match_subcategory(name_lower, cat_data)
        return folder_name, subcategory

    def _match_subcategory(self, name_lower: str, cat_data: Dict) -> str:
        for sub_name, sub_data in cat_data.get("subcategories", {}).items():
            for pattern in sub_data.get("name_patterns", []):
                if re.search(pattern, name_lower, re.IGNORECASE):
                    return sub_name
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE ORGANIZER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FileOrganizer:
    """
    Moves files into categorized folders and maintains a JSON history for rollback.
    """

    def __init__(self, classifier: FileClassifier, config: Config,
                 history_file: str = HISTORY_FILE):
        self.classifier   = classifier
        self.config       = config
        self.history_file = Path(history_file)
        self.logger       = logging.getLogger("nexus.organizer")

    # ── Public API ────────────────────────────────────────────────────────────

    def organize(self, source_dir: Path, dest_dir: Path) -> Dict[str, Any]:
        """
        Scan source_dir and move every qualifying file into dest_dir/<category>/.
        Returns a stats dict.
        """
        stats: Dict[str, Any] = defaultdict(int)
        category_counts: Dict[str, int] = defaultdict(int)
        category_sizes:  Dict[str, int] = defaultdict(int)

        files = self._collect_files(source_dir)
        stats["total_found"] = len(files)

        for fp in files:
            if self._is_excluded(fp):
                stats["skipped"] += 1
                continue

            category, subcategory = self.classifier.classify(fp)
            target_dir = dest_dir / category
            if subcategory:
                target_dir = target_dir / subcategory

            dest_path = self._resolve_dest(fp, target_dir)

            try:
                file_size = fp.stat().st_size
                if not self.config.dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(fp), str(dest_path))
                    self._log_action({
                        "timestamp":   datetime.now().isoformat(),
                        "action":      "move",
                        "src":         str(fp),
                        "dst":         str(dest_path),
                        "category":    category,
                        "subcategory": subcategory,
                        "size_bytes":  file_size
                    })

                rel = str(dest_path.relative_to(dest_dir))
                move_msg(fp.name, rel)
                self.logger.info(f"MOVED  {fp}  →  {dest_path}")
                stats["moved"] += 1
                category_counts[category] += 1
                category_sizes[category]  += file_size

            except (OSError, shutil.Error) as e:
                err(f"Error moviendo {fp.name}: {e}")
                self.logger.error(f"ERROR  {fp}: {e}")
                stats["errors"] += 1

        stats["by_category"]      = dict(category_counts)
        stats["by_category_size"] = dict(category_sizes)
        return dict(stats)

    def rollback(self, steps: int = 0) -> List[str]:
        """
        Undo the last N moves (steps=0 → undo all).
        Returns a list of restored filenames.
        """
        history = self._load_history()
        if not history:
            warn("No hay historial de acciones para revertir.")
            return []

        to_undo = history if steps == 0 else history[-steps:]
        restored: List[str] = []

        for action in reversed(to_undo):
            src = Path(action["dst"])
            dst = Path(action["src"])
            if not src.exists():
                warn(f"Archivo ya no existe, omitiendo: {src.name}")
                continue
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                ok(f"Restaurado: {dst.name}")
                restored.append(dst.name)
                self.logger.info(f"ROLLBACK  {src}  →  {dst}")
            except (OSError, shutil.Error) as e:
                err(f"Error restaurando {src.name}: {e}")

        if restored:
            remaining = history[: len(history) - len(to_undo)]
            self._save_history(remaining)

        return restored

    def search(self, query: str, directory: Path) -> List[Dict]:
        """
        Case-insensitive recursive search for files matching query.
        Returns list of result dicts sorted by filename.
        """
        results: List[Dict] = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)

        for fp in directory.rglob("*"):
            if fp.is_file() and pattern.search(fp.name):
                try:
                    stat = fp.stat()
                    results.append({
                        "name":       fp.name,
                        "path":       str(fp),
                        "relative":   str(fp.relative_to(directory)),
                        "size_bytes": stat.st_size,
                        "modified":   datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "category":   fp.parts[len(directory.parts)] if len(fp.parts) > len(directory.parts) else "Raíz"
                    })
                except OSError:
                    pass

        return sorted(results, key=lambda x: x["name"].lower())

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _collect_files(self, source_dir: Path) -> List[Path]:
        if self.config.organize_subfolders:
            return [
                fp for fp in source_dir.rglob("*")
                if fp.is_file() and not self._in_excluded_folder(fp, source_dir)
            ]
        return [fp for fp in source_dir.iterdir() if fp.is_file()]

    def _is_excluded(self, fp: Path) -> bool:
        name = fp.name
        return any(fnmatch.fnmatch(name.lower(), p.lower()) for p in self.config.exclude_patterns)

    def _in_excluded_folder(self, fp: Path, base: Path) -> bool:
        excluded = set(self.config.exclude_folders)
        parts    = set(fp.relative_to(base).parts[:-1])
        return bool(parts & excluded)

    def _resolve_dest(self, src: Path, target_dir: Path) -> Path:
        """Avoid overwriting existing files by appending _1, _2 …"""
        dest = target_dir / src.name
        if not dest.exists():
            return dest
        counter = 1
        while dest.exists():
            dest = target_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1
        return dest

    def _log_action(self, action: Dict):
        history = self._load_history()
        history.append(action)
        self._save_history(history)

    def _load_history(self) -> List[Dict]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save_history(self, history: List[Dict]):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE WATCH HANDLER  (requires watchdog)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if WATCHDOG_AVAILABLE:
    class FileWatchHandler(FileSystemEventHandler):   # type: ignore
        """
        Classifies and moves new files as they appear in the watched folder.
        A small delay is applied so partial downloads have time to complete.
        """

        def __init__(self, organizer: FileOrganizer, dest_dir: Path, delay: int = 3):
            super().__init__()
            self.organizer = organizer
            self.dest_dir  = dest_dir
            self.delay     = delay
            self._pending: Dict[str, float] = {}
            self.logger    = logging.getLogger("nexus.watcher")

        def on_created(self, event):
            if not event.is_directory:
                self._schedule(event.src_path)

        def on_moved(self, event):
            if not event.is_directory:
                self._schedule(event.dest_path)

        def _schedule(self, path_str: str):
            self._pending[path_str] = time.time() + self.delay

        def flush_pending(self):
            now   = time.time()
            ready = [p for p, t in list(self._pending.items()) if now >= t]
            for path_str in ready:
                del self._pending[path_str]
                fp = Path(path_str)
                if not fp.exists() or not fp.is_file():
                    continue
                if self.organizer._is_excluded(fp):
                    continue
                category, subcategory = self.organizer.classifier.classify(fp)
                target_dir = self.dest_dir / category
                if subcategory:
                    target_dir = target_dir / subcategory
                dest_path = self.organizer._resolve_dest(fp, target_dir)
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    size = fp.stat().st_size
                    shutil.move(str(fp), str(dest_path))
                    self.organizer._log_action({
                        "timestamp":   datetime.now().isoformat(),
                        "action":      "move",
                        "src":         path_str,
                        "dst":         str(dest_path),
                        "category":    category,
                        "subcategory": subcategory,
                        "size_bytes":  size
                    })
                    label = f"{category}/{subcategory}" if subcategory else category
                    ok(f"[WATCHER] {fp.name}  →  {label}")
                    self.logger.info(f"WATCHER  {fp}  →  {dest_path}")
                except (OSError, shutil.Error) as e:
                    err(f"[WATCHER] Error con {fp.name}: {e}")
                    self.logger.error(f"WATCHER ERROR  {fp}: {e}")

else:
    class FileWatchHandler:  # type: ignore  # stub
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REPORT GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ReportGenerator:
    """Generates ASCII bar charts and statistics."""

    BAR_WIDTH = 36

    def __init__(self, config: Config):
        self.config = config

    def print_organize_report(self, stats: Dict[str, Any], dest_dir: Path):
        total   = stats.get("total_found", 0)
        moved   = stats.get("moved",       0)
        skipped = stats.get("skipped",     0)
        errors  = stats.get("errors",      0)

        print()
        print(clr("  ━" * 25, C.CYAN))
        print(clr("  📊  REPORTE DE ORGANIZACIÓN", C.BOLD + C.CYAN))
        print(clr("  ━" * 25, C.CYAN))
        print(f"\n  {clr('Archivos encontrados :', C.WHITE)} {clr(str(total),   C.YELLOW)}")
        print(f"  {clr('Archivos organizados :', C.WHITE)} {clr(str(moved),   C.GREEN)}")
        print(f"  {clr('Omitidos             :', C.WHITE)} {clr(str(skipped), C.GRAY)}")
        print(f"  {clr('Errores              :', C.WHITE)} {clr(str(errors),  C.RED)}")

        by_cat  = stats.get("by_category",      {})
        by_size = stats.get("by_category_size", {})
        if by_cat:
            print()
            print(clr("  Por categoría:", C.BOLD))
            self._print_bar_chart(by_cat, by_size)

        total_size = sum(by_size.values())
        print(f"\n  {clr('Espacio organizado   :', C.WHITE)} {clr(_fmt_size(total_size), C.MAGENTA)}")
        print(f"  {clr('Carpeta destino      :', C.WHITE)} {clr(str(dest_dir),         C.BLUE)}")

        if stats.get("dry_run"):
            warn("MODO SIMULACIÓN — ningún archivo fue movido.")
        else:
            print(clr("\n  ✨  ¡Organización completada!", C.GREEN + C.BOLD))

        print(clr("  ━" * 25 + "\n", C.CYAN))

    def print_scan_stats(self, directory: Path):
        counts: Dict[str, int] = defaultdict(int)
        sizes:  Dict[str, int] = defaultdict(int)
        total_files = 0

        for fp in directory.rglob("*"):
            if fp.is_file():
                parts    = fp.relative_to(directory).parts
                category = parts[0] if parts else "Raíz"
                try:
                    sz = fp.stat().st_size
                except OSError:
                    sz = 0
                counts[category] += 1
                sizes[category]  += sz
                total_files      += 1

        print()
        print(clr("  ━" * 25, C.CYAN))
        print(clr("  📁  ESTADÍSTICAS DE CARPETA", C.BOLD + C.CYAN))
        print(clr("  ━" * 25, C.CYAN))
        print(f"\n  {clr('Directorio     :', C.WHITE)} {clr(str(directory), C.BLUE)}")
        print(f"  {clr('Total archivos :', C.WHITE)} {clr(str(total_files), C.YELLOW)}")
        print(f"  {clr('Tamaño total   :', C.WHITE)} {clr(_fmt_size(sum(sizes.values())), C.MAGENTA)}")

        if counts:
            print()
            print(clr("  Distribución:", C.BOLD))
            self._print_bar_chart(counts, sizes)

        print(clr("  ━" * 25 + "\n", C.CYAN))

    def _print_bar_chart(self, counts: Dict[str, int], sizes: Dict[str, int]):
        max_count = max(counts.values(), default=1)
        for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            bar_len  = int((count / max_count) * self.BAR_WIDTH)
            bar      = "█" * bar_len + "░" * (self.BAR_WIDTH - bar_len)
            label    = f"{cat:<22}"[:22]
            size_str = _fmt_size(sizes.get(cat, 0))
            print(
                f"  {clr(label, C.WHITE)}  "
                f"{clr(bar, C.CYAN)}  "
                f"{clr(str(count), C.YELLOW):>4} archivos  "
                f"{clr(size_str, C.GRAY)}"
            )


def _fmt_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024  # type: ignore[assignment]
    return f"{size_bytes:.1f} PB"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def setup_logging(level: str = "INFO", log_file: str = LOG_FILE):
    numeric = getattr(logging, level.upper(), logging.INFO)
    handlers: List[logging.Handler] = [
        logging.FileHandler(log_file, encoding="utf-8")
    ]
    if numeric <= logging.DEBUG:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s  [%(levelname)-8s]  %(name)s  —  %(message)s",
        handlers=handlers
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BANNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_banner():
    print(f"{C.CYAN}{C.BOLD}")
    print(" ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗")
    print(" ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝")
    print(" ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗")
    print(" ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║")
    print(" ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║")
    print(" ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝")
    print(f"{C.RESET}{C.GRAY}        Smart File Organizer  •  v1.0.0{C.RESET}")
    print(f"{C.GRAY} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_organize(args, config: Config, organizer: FileOrganizer, reporter: ReportGenerator):
    source = Path(args.folder).expanduser() if args.folder else config.watch_folder
    dest   = Path(args.dest).expanduser()   if getattr(args, "dest", None) else (config.dest_folder or source)

    if not source.exists():
        err(f"La carpeta '{source}' no existe.")
        sys.exit(1)

    if getattr(args, "dry_run", False):
        config._data["dry_run"] = True

    info(f"Fuente  : {clr(str(source), C.YELLOW)}")
    info(f"Destino : {clr(str(dest),   C.YELLOW)}")
    if config.dry_run:
        warn("MODO SIMULACIÓN activado — ningún archivo será movido.")
    print()

    stats = organizer.organize(source, dest)
    reporter.print_organize_report(stats, dest)


def cmd_watch(args, config: Config, organizer: FileOrganizer):
    if not WATCHDOG_AVAILABLE:
        err("watchdog no instalado. Ejecuta:  pip install watchdog")
        sys.exit(1)

    source = Path(args.folder).expanduser() if getattr(args, "folder", None) else config.watch_folder
    dest   = Path(args.dest).expanduser()   if getattr(args, "dest",   None) else (config.dest_folder or source)

    if not source.exists():
        err(f"La carpeta '{source}' no existe.")
        sys.exit(1)

    delay   = getattr(args, "delay", None) or config.monitor_delay
    handler = FileWatchHandler(organizer, dest, delay=delay)
    observer = Observer()
    observer.schedule(handler, str(source), recursive=False)
    observer.start()

    ok(f"Monitoreando : {clr(str(source), C.YELLOW)}")
    ok(f"Destino      : {clr(str(dest),   C.YELLOW)}")
    info(f"Demora       : {delay}s por archivo nuevo")
    print(clr("\n  Presiona Ctrl+C para detener.\n", C.GRAY))

    try:
        while True:
            handler.flush_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print()
    ok("Monitor detenido.")


def cmd_rollback(args, organizer: FileOrganizer):
    steps = getattr(args, "steps", 0) or 0
    label = f"las últimas {steps}" if steps else "todas las"
    info(f"Revirtiendo {label} acciones…\n")
    restored = organizer.rollback(steps)
    print()
    if restored:
        ok(f"{len(restored)} archivo(s) restaurado(s).")
    else:
        warn("Nada que revertir.")


def cmd_search(args, organizer: FileOrganizer, config: Config):
    folder = Path(args.folder).expanduser() if getattr(args, "folder", None) else (config.dest_folder or config.watch_folder)
    query  = args.query

    if not folder.exists():
        err(f"La carpeta '{folder}' no existe.")
        sys.exit(1)

    info(f"Buscando '{clr(query, C.YELLOW)}' en {clr(str(folder), C.BLUE)}…\n")
    results = organizer.search(query, folder)

    if not results:
        warn("No se encontraron resultados.")
        return

    print(clr(f"  {'ARCHIVO':<36} {'CATEGORÍA':<22} {'TAMAÑO':>10}  MODIFICADO", C.BOLD))
    print(clr("  " + "─" * 82, C.GRAY))
    for r in results:
        name  = r["name"][:35]
        cat   = r["category"][:21]
        size  = _fmt_size(r["size_bytes"])
        mtime = r["modified"]
        print(
            f"  {clr(f'{name:<36}', C.WHITE)}"
            f"{clr(f'{cat:<22}', C.CYAN)}"
            f"{clr(f'{size:>10}', C.YELLOW)}  "
            f"{clr(mtime, C.GRAY)}"
        )
    print()
    ok(f"{len(results)} resultado(s) encontrado(s).")


def cmd_stats(args, config: Config, reporter: ReportGenerator):
    folder = Path(args.folder).expanduser() if getattr(args, "folder", None) else (config.dest_folder or config.watch_folder)
    if not folder.exists():
        err(f"La carpeta '{folder}' no existe.")
        sys.exit(1)
    reporter.print_scan_stats(folder)


def cmd_init(config: Config):
    p = Path(CONFIG_FILE)
    if p.exists():
        warn(f"'{CONFIG_FILE}' ya existe — será sobrescrito.")
    config._data = DEFAULT_CONFIG.copy()
    config.save()
    ok(f"Configuración generada: {clr(CONFIG_FILE, C.YELLOW)}")
    info("Edita el archivo para personalizar categorías y rutas.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARGUMENT PARSER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="NEXUS — Smart File Organizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python nexus.py organize ~/Downloads
  python nexus.py organize ~/Downloads --dest ~/Organizado --dry-run
  python nexus.py watch ~/Downloads --dest ~/Organizado
  python nexus.py search factura --folder ~/Organizado
  python nexus.py rollback --steps 5
  python nexus.py stats ~/Organizado
  python nexus.py init
        """
    )
    parser.add_argument(
        "--config", default=CONFIG_FILE,
        help=f"Ruta al archivo de configuración (default: {CONFIG_FILE})"
    )

    sub = parser.add_subparsers(dest="command", metavar="COMANDO")

    # ── organize ──────────────────────────────────────────────────────────────
    p_org = sub.add_parser("organize", aliases=["org", "o"],
                            help="Organizar archivos en una carpeta")
    p_org.add_argument("folder", nargs="?",
                       help="Carpeta a organizar (sobreescribe config)")
    p_org.add_argument("--dest", "-d",
                       help="Carpeta destino (default: misma carpeta fuente)")
    p_org.add_argument("--dry-run", action="store_true",
                       help="Simular sin mover archivos")
    p_org.add_argument("--recursive", "-r", action="store_true",
                       help="Incluir subcarpetas")

    # ── watch ─────────────────────────────────────────────────────────────────
    p_watch = sub.add_parser("watch", aliases=["w"],
                              help="Monitoreo en tiempo real con watchdog")
    p_watch.add_argument("folder", nargs="?",
                         help="Carpeta a monitorear")
    p_watch.add_argument("--dest", "-d",
                         help="Carpeta destino")
    p_watch.add_argument("--delay", "-t", type=int,
                         help="Segundos de espera antes de mover (default: 3)")

    # ── rollback ──────────────────────────────────────────────────────────────
    p_rb = sub.add_parser("rollback", aliases=["undo", "rb"],
                           help="Revertir últimas acciones")
    p_rb.add_argument("--steps", "-n", type=int, default=0,
                      help="Cantidad de pasos a revertir (0 = todos)")

    # ── search ────────────────────────────────────────────────────────────────
    p_srch = sub.add_parser("search", aliases=["find", "s"],
                             help="Buscar archivos dentro de las carpetas organizadas")
    p_srch.add_argument("query",
                        help="Texto a buscar en nombres de archivo")
    p_srch.add_argument("--folder", "-f",
                        help="Carpeta raíz donde buscar")

    # ── stats ─────────────────────────────────────────────────────────────────
    p_stats = sub.add_parser("stats",
                              help="Ver estadísticas de una carpeta organizada")
    p_stats.add_argument("folder", nargs="?",
                         help="Carpeta a analizar")

    # ── init ──────────────────────────────────────────────────────────────────
    sub.add_parser("init",
                   help=f"Crear {CONFIG_FILE} con configuración por defecto")

    return parser


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    parser = build_parser()
    args   = parser.parse_args()

    config = Config.load(getattr(args, "config", CONFIG_FILE))
    setup_logging(config.get_raw("log_level", "INFO"), LOG_FILE)

    if getattr(args, "dry_run",   False): config._data["dry_run"]            = True
    if getattr(args, "recursive", False): config._data["organize_subfolders"] = True

    classifier = FileClassifier(config)
    organizer  = FileOrganizer(classifier, config)
    reporter   = ReportGenerator(config)

    command = getattr(args, "command", None)

    if command in ("organize", "org", "o"):
        print_banner()
        cmd_organize(args, config, organizer, reporter)

    elif command in ("watch", "w"):
        print_banner()
        cmd_watch(args, config, organizer)

    elif command in ("rollback", "undo", "rb"):
        print_banner()
        cmd_rollback(args, organizer)

    elif command in ("search", "find", "s"):
        print_banner()
        cmd_search(args, organizer, config)

    elif command == "stats":
        print_banner()
        cmd_stats(args, config, reporter)

    elif command == "init":
        print_banner()
        cmd_init(config)

    else:
        print_banner()
        parser.print_help()


if __name__ == "__main__":
    main()
