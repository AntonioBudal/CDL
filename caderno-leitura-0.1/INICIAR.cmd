@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" goto not_installed
"backend\.venv\Scripts\python.exe" iniciar.py
if errorlevel 1 goto failed
exit /b 0
:not_installed
echo Execute INSTALAR.cmd antes de abrir o caderno.
pause
exit /b 1
:failed
echo.
echo O servidor foi encerrado ou nao conseguiu iniciar. Confira a mensagem acima.
pause
exit /b 1
