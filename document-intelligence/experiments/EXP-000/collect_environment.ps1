# EXP-000 — coleta do inventário real de ambiente (somente leitura, local, sem rede).
# Uso (PowerShell, a partir de document-intelligence/):
#   powershell -ExecutionPolicy Bypass -File experiments\EXP-000\collect_environment.ps1
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$os  = Get-CimInstance Win32_OperatingSystem
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
"## CPU";  "$($cpu.Name) | $($cpu.NumberOfCores) núcleos / $($cpu.NumberOfLogicalProcessors) threads"
"## RAM";  "$ram GB"
"## GPU"
Get-CimInstance Win32_VideoController | ForEach-Object {
  "$($_.Name) | driver $($_.DriverVersion) | VRAM(reportada) $([math]::Round($_.AdapterRAM/1GB,1)) GB"
}
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
  "## nvidia-smi"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else { "## nvidia-smi: não encontrado (sem GPU NVIDIA/driver)" }
"## Armazenamento (unidade do projeto)"
$d = Get-PSDrive -Name ((Get-Location).Path.Substring(0,1))
"Livre: $([math]::Round($d.Free/1GB,1)) GB"
Get-PhysicalDisk | ForEach-Object { "$($_.FriendlyName) | $($_.MediaType) | $([math]::Round($_.Size/1GB)) GB" }
"## Sistema Operacional"
"$($os.Caption) | versão $($os.Version) | build $($os.BuildNumber) | $($os.OSArchitecture)"
"## Shell"; "PowerShell $($PSVersionTable.PSVersion)"
"## Toolchain"
"uv: $(uv --version)"
"python (uv): $(uv run python --version)"
"git: $(git --version)"
"git core.autocrlf: $(git config core.autocrlf)"
"## Python / torch / CUDA"
uv run python -c "import sys,locale;print('encoding',sys.getdefaultencoding(),locale.getpreferredencoding())"
uv run python -c "import importlib.util as u;print('torch instalado:', u.find_spec('torch') is not None)"
"## Testes"
Measure-Command { uv run pytest -q | Out-Host } | ForEach-Object { "uv run pytest: $($_.TotalSeconds) s" }
uv run ruff check .
