@echo off
title MeuCMD

chcp 65001 > nul
setlocal

REM Cria ambiente virtual e instala dependencias
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Ambiente virtual criado em .venv e dependencias instaladas.
pause
