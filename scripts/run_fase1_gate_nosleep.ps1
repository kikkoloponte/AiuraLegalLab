# run_fase1_gate_nosleep.ps1
# Gate di chiusura Fase 1 (PR #4) in una notte, impedendo lo sleep del PC:
#   A. Rebuild BM25 v2 (bm25s) sui workspace con pkl azzerati dalla migrazione
#   B. Avvio API (se non già attiva)
#   C. Query suite completa  -> eval/results/fase1_post/suite
#   D. Bench giurisprudenza  -> eval/results/fase1_post/bench
#   E. Cleanup-old in DRY-RUN (solo conteggio — l'eliminazione vera si fa
#      a mano dopo aver verificato l'eval)
#
# Prerequisiti: Qdrant server attivo (QDRANT_URL), LM Studio aperto col
# modello caricato (serve a suite e bench per la parte LLM).
#
# Uso: .\scripts\run_fase1_gate_nosleep.ps1

# ── Anti-sleep (Win32 SetThreadExecutionState) ─────────────────────────────
$code = @"
using System;
using System.Runtime.InteropServices;
public class SleepBlocker {
    [DllImport("kernel32.dll")]
    public static extern uint SetThreadExecutionState(uint esFlags);
    public const uint ES_CONTINUOUS       = 0x80000000;
    public const uint ES_SYSTEM_REQUIRED  = 0x00000001;
    public static void Prevent() {
        SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED);
    }
    public static void Allow() {
        SetThreadExecutionState(ES_CONTINUOUS);
    }
}
"@
Add-Type -TypeDefinition $code
[SleepBlocker]::Prevent()
Write-Host "Sleep disabilitato per tutta la durata del gate." -ForegroundColor Green

$root = Split-Path $PSScriptRoot
Set-Location $root
New-Item -ItemType Directory -Force logs | Out-Null
New-Item -ItemType Directory -Force eval\results\fase1_post | Out-Null

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (Test-Path $venvPython) { $py = $venvPython } else { $py = "python" }
Write-Host "Python: $py" -ForegroundColor DarkGray

$apiStarted = $false
$apiProc = $null

function Test-Url([string]$url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        return ($r.StatusCode -eq 200)
    } catch { return $false }
}

try {
    # ── Pre-flight ─────────────────────────────────────────────────────────
    if (Test-Url "http://localhost:6333/collections") {
        Write-Host "Qdrant: OK" -ForegroundColor Green
    } else {
        Write-Host "ERRORE: Qdrant non raggiungibile su :6333 — avvialo e rilancia." -ForegroundColor Red
        exit 1
    }
    if (Test-Url "http://127.0.0.1:1234/v1/models") {
        Write-Host "LM Studio: OK" -ForegroundColor Green
    } else {
        Write-Host "AVVISO: LM Studio non raggiungibile — suite e bench gireranno senza LLM (solo retrieval)." -ForegroundColor Yellow
    }

    # ── A. Rebuild BM25 (solo BM25, il vettoriale non si tocca) ────────────
    $workspaces = @("mio-studio", "normattiva", "normattiva_amministrativo",
                    "normattiva_civile", "normattiva_cross", "normattiva_penale",
                    "normattiva_tributario")
    foreach ($ws in $workspaces) {
        if (-not (Test-Path "workspaces\$ws")) {
            Write-Host "[A] workspace '$ws' assente — salto" -ForegroundColor DarkGray
            continue
        }
        Write-Host "=== [A] Rebuild BM25: $ws ===" -ForegroundColor Cyan
        & $py scripts/build_indexes.py --workspace $ws --skip-vector 2>&1 |
            Tee-Object -FilePath "logs\fase1_rebuild_$ws.log"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERRORE rebuild $ws (exit $LASTEXITCODE) — vedi logs\fase1_rebuild_$ws.log" -ForegroundColor Red
        }
    }

    # ── B. API su :8765 (riusa quella attiva, altrimenti avviala) ──────────
    if (Test-Url "http://127.0.0.1:8765/health") {
        Write-Host "[B] API già attiva — la riuso" -ForegroundColor Green
    } else {
        Write-Host "[B] Avvio API in background..." -ForegroundColor Cyan
        $apiProc = Start-Process -FilePath $py -ArgumentList "-m", "aiura_legal.api" `
            -RedirectStandardOutput "logs\fase1_api.out.log" `
            -RedirectStandardError  "logs\fase1_api.err.log" `
            -PassThru -WindowStyle Hidden
        $apiStarted = $true
        $up = $false
        foreach ($i in 1..36) {   # fino a 3 minuti (carica indici grossi)
            Start-Sleep -Seconds 5
            if (Test-Url "http://127.0.0.1:8765/health") { $up = $true; break }
        }
        if (-not $up) {
            Write-Host "ERRORE: API non risponde dopo 3 minuti — vedi logs\fase1_api.err.log" -ForegroundColor Red
            exit 1
        }
        Write-Host "[B] API pronta" -ForegroundColor Green
    }

    # ── C. Query suite completa ─────────────────────────────────────────────
    Write-Host "=== [C] Query suite (130 query, ~1-2h con LLM) ===" -ForegroundColor Cyan
    & $py scripts/run_query_suite.py --out-dir eval/results/fase1_post/suite 2>&1 |
        Tee-Object -FilePath "logs\fase1_suite.log"

    # ── D. Bench giurisprudenza ─────────────────────────────────────────────
    Write-Host "=== [D] Bench giurisprudenza (10 domande, ~30-90 min) ===" -ForegroundColor Cyan
    & $py eval/run_bench.py --workspace mio-studio --output-dir eval/results/fase1_post/bench 2>&1 |
        Tee-Object -FilePath "logs\fase1_bench.log"

    # ── E. Cleanup-old SOLO DRY-RUN (niente eliminazioni stanotte) ─────────
    Write-Host "=== [E] Cleanup punti monolitici — DRY RUN ===" -ForegroundColor Cyan
    & $py scripts/build_jurisprudence_indexes.py --workspace mio-studio --cleanup-old --dry-run 2>&1 |
        Tee-Object -FilePath "logs\fase1_cleanup_dryrun.log"

    Write-Host ""
    Write-Host "Gate Fase 1 completato. Risultati:" -ForegroundColor Green
    Write-Host "  eval\results\fase1_post\suite   (confronta con eval\results\baseline_pre_fase1)"
    Write-Host "  eval\results\fase1_post\bench"
    Write-Host "  logs\fase1_*.log"
    Write-Host "Se l'eval e' OK: lancia il cleanup vero con:" -ForegroundColor Yellow
    Write-Host "  $py scripts/build_jurisprudence_indexes.py --workspace mio-studio --cleanup-old"
}
finally {
    if ($apiStarted -and $apiProc -and -not $apiProc.HasExited) {
        Write-Host "Arresto API avviata dallo script..." -ForegroundColor DarkGray
        Stop-Process -Id $apiProc.Id -Force -ErrorAction SilentlyContinue
    }
    [SleepBlocker]::Allow()
    Write-Host "Sleep riabilitato." -ForegroundColor Green
}
