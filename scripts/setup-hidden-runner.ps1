# 윈도우 부팅 시 터미널 창 없이 백그라운드로 실행되는 Self-hosted Runner 등록 스크립트

$runnerDir = "$env:USERPROFILE\actions-runner"
if (-not (Test-Path $runnerDir)) {
    Write-Error "actions-runner 폴더를 찾을 수 없습니다: $runnerDir"
    exit 1
}

# 1. VBScript 생성 (무창 실행)
# 설치 경로를 동적으로 참조하여 run.cmd를 0(숨김 창)으로 호출합니다.
$vbsContent = "Set WshShell = CreateObject(""WScript.Shell"") : WshShell.Run chr(34) & ""$runnerDir\run.cmd"" & chr(34), 0 : Set WshShell = Nothing"
[System.IO.File]::WriteAllText("$runnerDir\run-hidden.vbs", $vbsContent, [System.Text.Encoding]::ASCII)
Write-Host "1. run-hidden.vbs 생성 완료 ($runnerDir\run-hidden.vbs)" -ForegroundColor Green

# 2. 작업 스케줄러 등록 (-RunLevel Highest 권장)
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$runnerDir\run-hidden.vbs`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName "GitHubRunner-Hidden" -Action $action -Trigger $trigger -Principal $principal -Force
Write-Host "2. 작업 스케줄러(GitHubRunner-Hidden) 등록 완료" -ForegroundColor Green

# 3. 즉시 시작
Start-ScheduledTask -TaskName "GitHubRunner-Hidden"
Write-Host "3. 백그라운드 러너 즉시 실행 완료!" -ForegroundColor Cyan
