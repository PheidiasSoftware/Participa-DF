@echo off
chcp 65001 > nul
setlocal

REM Vai para a pasta raiz do projeto
pushd ..

REM Ativa venv se existir
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

REM Treinamento simples com dataset padrao
python main.py --data data\dataset_treinamento_acesso_informacao.xlsx --threshold 0.70

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Ocorreu um erro. Verifique se o Python esta instalado e se as dependencias estao no requirements.txt.
) else (
  echo.
  echo Treinamento concluido. Saidas em outputs\ e relatorios em reports\.
  echo Arquivo XLSX gerado: outputs\rotulos_fracos.xlsx
)

popd
pause
