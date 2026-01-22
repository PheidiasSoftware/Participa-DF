@echo off
title MeuCMD

chcp 65001 > nul
setlocal

REM Ativa venv se existir
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

REM Mensagem simples (sem mostrar caminho)
if "%VIRTUAL_ENV%"=="" (
  echo Ambiente virtual: NAO ATIVO
) else (
  echo Ambiente virtual: ATIVO
)

REM Predicao simples usando o modelo salvo
python predict.py --input data\AMOSTRA_e-SIC.xlsx --output outputs\predictions.csv --threshold 0.70

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Ocorreu um erro. Verifique se o modelo foi treinado e se os arquivos existem.
) else (
  echo.
  echo Predicao concluida. Arquivos gerados:
  echo - outputs\predictions.csv
  echo - outputs\predictions.xlsx
)

pause
