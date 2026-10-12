@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 jogar_visual.py
) else (
    python jogar_visual.py
)
if errorlevel 1 (
    echo.
    echo Nao foi possivel iniciar. E necessario ter Python 3.10 ou superior instalado.
    pause
)
