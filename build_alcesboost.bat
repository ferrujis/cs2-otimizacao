@echo off
REM Script para gerar alcesboost.exe usando PyInstaller
REM A flag --uac-admin adiciona a exigência de execução como Administrador
pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=alcesboost.ico --name alcesboost main.py

echo Build concluído. O executável estará em dist\alcesboost.exe
pause
