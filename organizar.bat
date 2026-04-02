@echo off
cd /d "%~dp0"
echo.
echo  NEXUS - Organizador de Archivos
echo  ================================
echo.

:: Carpeta a organizar (por defecto: Descargas)
set "CARPETA=%USERPROFILE%\Downloads"

:: Si quieres organizar otra carpeta, cambia la linea de arriba.
:: Ejemplo: set "CARPETA=C:\Users\juans\Desktop"

echo  Organizando: %CARPETA%
echo.

python nexus.py organize "%CARPETA%"

echo.
pause
