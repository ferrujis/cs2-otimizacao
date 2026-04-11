@echo off
REM Build limpo para alcesboost.exe usando PyInstaller.
REM Remove arquivos antigos, atualiza dependências e ignora pacote inválido 'platform'.

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo Limpando builds antigos...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist alcesboost.spec del /f /q alcesboost.spec

echo Instalando dependências (excluindo 'platform')...
python -m pip install --upgrade pip
for /f "usebackq delims=" %%a in ("requirements.txt") do (
    set "line=%%a"
    if not "!line!"=="" (
        if /i not "!line!"=="platform" (
            if not "!line:~0,1!"=="#" (
                echo Instalando !line!... 
                python -m pip install "!line!"
            )
        )
    )
)

echo Gerando executavel...
python -m PyInstaller --noconfirm --onefile --windowed --uac-admin --icon=alcesboost.ico --name alcesboost main.py

echo Build concluido. Verifique dist\alcesboost.exe
pause
endlocal
