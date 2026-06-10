# run_classify_nosleep.ps1
# Esegue la pipeline di classificazione KB impedendo lo sleep del PC.
# Uso: .\scripts\run_classify_nosleep.ps1 -Model qwen2.5-32b

param(
    [string]$Model = "qwen2.5-32b",
    [string]$Workspace = "mio-studio"
)

# Impedisce sleep e spegnimento schermo tramite SetThreadExecutionState Win32 API
$code = @"
using System;
using System.Runtime.InteropServices;
public class SleepBlocker {
    [DllImport("kernel32.dll")]
    public static extern uint SetThreadExecutionState(uint esFlags);
    public const uint ES_CONTINUOUS       = 0x80000000;
    public const uint ES_SYSTEM_REQUIRED  = 0x00000001;
    public const uint ES_DISPLAY_REQUIRED = 0x00000002;
    public static void Prevent() {
        SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED);
    }
    public static void Allow() {
        SetThreadExecutionState(ES_CONTINUOUS);
    }
}
"@
Add-Type -TypeDefinition $code

[SleepBlocker]::Prevent()
Write-Host "Sleep disabilitato. Il PC resterà acceso per tutta la pipeline." -ForegroundColor Green

New-Item -ItemType Directory -Force logs | Out-Null

function Run-Phase {
    param([string]$Fase, [string[]]$ExtraArgs)
    $logFile = "logs\classify_$Fase.log"
    Write-Host ""
    Write-Host "=== FASE $Fase ===" -ForegroundColor Cyan
    Write-Host "Log: $logFile"
    $cmd = @("scripts/classify_knowledge_base.py", "--fase", $Fase) + $ExtraArgs
    python @cmd 2>&1 | Tee-Object -FilePath $logFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ATTENZIONE: Fase $Fase terminata con errore (exit $LASTEXITCODE)" -ForegroundColor Yellow
    }
}

try {
    Run-Phase "A" @("--model", $Model)
    Run-Phase "B" @("--model", $Model)
    Run-Phase "C" @()
    Run-Phase "D" @("--model", $Model)
    Run-Phase "E" @("--model", $Model)

    Write-Host ""
    Write-Host "=== REBUILD INDICI ===" -ForegroundColor Cyan
    python scripts/rebuild_knowledge_base.py --workspace $Workspace 2>&1 | Tee-Object -FilePath logs\rebuild.log

    Write-Host ""
    Write-Host "Pipeline completata." -ForegroundColor Green
}
finally {
    [SleepBlocker]::Allow()
    Write-Host "Sleep riabilitato." -ForegroundColor Gray
}
