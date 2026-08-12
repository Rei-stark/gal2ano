# PowerShell: cria venv e instala dependências
param(
    [string]$VenvName = ".venv"
)
python -m venv $VenvName
& "$PSScriptRoot\..\$VenvName\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r "$PSScriptRoot\..\requirements.txt"
Write-Host "Ambiente criado e dependências instaladas. Ative o venv com: .\$VenvName\Scripts\Activate.ps1" -ForegroundColor Green
