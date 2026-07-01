@echo off
setlocal

cd /d "%~dp0"
set "PY_LOCAL=C:\Users\thiag\Documents\Codex\2026-06-02\files-mentioned-by-the-user-gerador\outputs\.python_build\python.exe"
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:8765/'"

if exist "%PY_LOCAL%" (
    "%PY_LOCAL%" "%~dp0app.py"
    goto fim
)

where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0app.py"
    goto fim
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0app.py"
    goto fim
)

echo Nenhum Python foi encontrado para abrir o monitor web.
pause
exit /b 1

:fim
if errorlevel 1 (
    echo.
    echo O monitor web foi encerrado com erro.
    pause
)
