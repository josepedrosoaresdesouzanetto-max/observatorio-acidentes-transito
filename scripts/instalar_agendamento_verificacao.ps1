param(
    [string]$TaskName = "Observatorio PRF - Verificar dados publicos",
    [string]$DiaDaSemana = "Monday",
    [string]$Horario = "09:00"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Runner = Join-Path $PSScriptRoot "verificar_dados_publicos_semanal.ps1"

if (-not (Test-Path $Runner)) {
    throw "Script de verificacao nao encontrado: $Runner"
}

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Runner`"" `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DiaDaSemana -At $Horario
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20)

$Description = "Consulta a fonte publica da PRF, compara com os CSVs locais e grava relatorio em logs. Nao baixa nem sobrescreve dados brutos."

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description $Description `
    -Force | Out-Null

Write-Host "Agendamento criado/atualizado: $TaskName"
Write-Host "Frequencia: semanal, $DiaDaSemana as $Horario"
Write-Host "Projeto: $ProjectRoot"
Write-Host "Script: $Runner"
