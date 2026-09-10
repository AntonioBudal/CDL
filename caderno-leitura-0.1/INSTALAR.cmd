@echo off
setlocal
cd /d "%~dp0"
py -3.13 --version >nul 2>&1
if errorlevel 1 goto python_missing
py -3.13 instalar.py
if errorlevel 1 goto failed
echo.
echo Pronto. Abra INICIAR.cmd para usar o caderno.
pause
exit /b 0
:python_missing
echo Python 3.13 nao encontrado. Instale-o conforme o LEIA-ME-0.1.md.
echo Se instalou sem o comando py, use o caminho do python.exe para executar instalar.py.
pause
exit /b 1
:failed
echo.
echo A instalacao nao terminou. Confira o erro acima e o LEIA-ME-0.1.md.
pause
exit /b 1
