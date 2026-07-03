param(
    [string]$ReportName = "status_dados_publicos.md"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $ProjectRoot "logs"
$PythonVenv = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = if (Test-Path $PythonVenv) { $PythonVenv } else { "python" }

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$LogPath = Join-Path $LogDir "verificacao_dados_publicos_$Timestamp.log"
$ReportPath = Join-Path $LogDir $ReportName

Set-Location $ProjectRoot

"# Verificacao automatica de dados publicos" | Out-File -FilePath $LogPath -Encoding utf8
"Data/hora: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $LogPath -Encoding utf8 -Append
"Projeto: $ProjectRoot" | Out-File -FilePath $LogPath -Encoding utf8 -Append
"" | Out-File -FilePath $LogPath -Encoding utf8 -Append

& $Python -m src.verificar_dados_publicos --salvar-relatorio $ReportPath 2>&1 |
    Tee-Object -FilePath $LogPath -Append

$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
    "Resultado: falha na verificacao. Consulte $LogPath" | Out-File -FilePath $LogPath -Encoding utf8 -Append
    exit $ExitCode
}

"Resultado: verificacao concluida. Relatorio: $ReportPath" | Out-File -FilePath $LogPath -Encoding utf8 -Append
exit 0
