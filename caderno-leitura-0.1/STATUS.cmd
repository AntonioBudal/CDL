@echo off
chcp 65001 >nul
echo ========================================================
echo   Verificando status do servidor Leitorum...
echo ========================================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "$conns = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue; if ($conns) { Write-Host 'Leitorum esta ATIVO e rodando em segundo plano!' -ForegroundColor Green; Write-Host 'Porta: 8000 (PID: ' $conns[0].OwningProcess ')' -ForegroundColor Green; Write-Host 'Acesse no navegador: http://localhost:8000' -ForegroundColor Cyan } else { Write-Host 'Leitorum esta PARADO (porta 8000 livre).' -ForegroundColor Yellow }"
echo.
pause
