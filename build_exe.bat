@echo off
setlocal
cd /d "%~dp0"

echo ==========================================================
echo   Cor Bloom Tracking Assistant - creazione eseguibile
echo ==========================================================
echo.

set "PYTHON=py -3"
py -3 --version >nul 2>&1
if errorlevel 1 set "PYTHON=python"
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato. Installa Python 3.10+ da python.org
    echo          ricordandoti di spuntare "Add python.exe to PATH".
    pause
    exit /b 1
)

set "VENV=%~dp0.venv-build"
set "VPY=%VENV%\Scripts\python.exe"

if not exist "%VPY%" (
    echo [1/5] Creo l'ambiente virtuale di build...
    %PYTHON% -m venv "%VENV%" || goto :fail
) else (
    echo [1/5] Ambiente virtuale gia' presente.
)

echo [2/5] Installo le dipendenze...
"%VPY%" -m pip install --upgrade pip >nul || goto :fail
"%VPY%" -m pip install -r requirements.txt pyinstaller || goto :fail

echo [3/5] Scarico Chromium dentro il pacchetto playwright...
set "PLAYWRIGHT_BROWSERS_PATH=0"
"%VPY%" -m playwright install chromium || goto :fail

echo [4/5] Pulisco le build precedenti...
if exist "%~dp0build" rmdir /s /q "%~dp0build"
if exist "%~dp0dist" rmdir /s /q "%~dp0dist"

echo [5/5] Compilo. Servono diversi minuti, non chiudere la finestra...
"%VPY%" -m PyInstaller --noconfirm tracking_assistant.spec || goto :fail

set "OUT=%~dp0dist\CorBloomTrackingAssistant"
if not exist "%OUT%\CorBloomTrackingAssistant.exe" goto :fail

if not exist "%OUT%\.env" (
    if exist "%~dp0.env" (
        copy /y "%~dp0.env" "%OUT%\.env" >nul
        echo Copiato il tuo .env accanto all'eseguibile.
    ) else (
        copy /y "%~dp0.env.example" "%OUT%\.env" >nul
        echo Copiato .env.example come .env: aprilo e inserisci le credenziali Shopify.
    )
)

if exist "%~dp0dianxiaomi_state.json" copy /y "%~dp0dianxiaomi_state.json" "%OUT%\" >nul

echo.
echo ==========================================================
echo   Build completata.
echo.
echo   Cartella da distribuire:
echo     %OUT%
echo   Eseguibile da avviare:
echo     CorBloomTrackingAssistant.exe
echo.
echo   Va copiata tutta la cartella, non solo il file .exe.
echo   Prima del primo uso: apri .env e inserisci le credenziali,
echo   poi lancia una volta CorBloomTrackingAssistant.exe --setup-session
echo   per il login manuale a dianxiaomi.
echo ==========================================================
pause
exit /b 0

:fail
echo.
echo [ERRORE] Build interrotta. Il messaggio di errore e' qui sopra.
pause
exit /b 1
