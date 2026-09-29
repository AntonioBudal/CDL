@echo off
chcp 65001 >nul
echo ========================================================
echo   Encerrando o servidor do Leitorum em segundo plano...
echo ========================================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "$conns = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue; if ($conns) { foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force; Write-Host 'Processo (PID' $c.OwningProcess ') encerrado com sucesso.' -ForegroundColor Green } } else { Write-Host 'Nenhum processo escutando na porta 8000.' -ForegroundColor Yellow }"
echo.
pause
