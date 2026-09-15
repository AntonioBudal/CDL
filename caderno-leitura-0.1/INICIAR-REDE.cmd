@echo off
call "%~dp0backend\.venv\Scripts\python.exe" "%~dp0iniciar.py" --host 0.0.0.0 --port 8000

exit /b %errorlevel%    