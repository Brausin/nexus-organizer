@echo off
REM setup_dev.bat — Configura el entorno de desarrollo local
REM Ejecutar una vez al clonar el repositorio

echo [nexus_organizer] Configurando entorno de desarrollo...

REM Instalar dependencias Python
pip install -r requirements.txt

REM Instalar hook pre-commit
if not exist ".git\hooks" mkdir .git\hooks
copy /Y ".github\hooks\pre-commit" ".git\hooks\pre-commit" >nul
echo [OK] Pre-commit hook instalado

REM Configurar plantilla de mensajes de commit
git config commit.template .gitmessage
echo [OK] Plantilla de commit configurada

echo.
echo [nexus_organizer] Entorno listo. Rama actual:
git branch --show-current
