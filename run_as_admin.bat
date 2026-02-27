@echo off
REM Script para executar o aplicativo CS2 Optimizer como Administrador

echo Iniciando CS2 Optimizer como Administrador...
timeout /t 2

REM Alterar para o diretorio do script
cd /d "%~dp0"

REM Executar o Python com direitos de admin
powershell -Command "Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList 'main.py' -Verb RunAs"

pause
