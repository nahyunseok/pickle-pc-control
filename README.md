# 🤖 피클(Pickle) AI ↔ Windows PC 완전 무인 원격 제어 오픈소스 가이드

> **모바일 피클(Pickle) AI 비서 앱에서 집/사무실의 Windows PC를 완벽하게 제어하는 5단계 실전 구축 매뉴얼**  
> 💸 **외부 LLM(Claude/OpenAI) API 토큰 소모 0원** | 🌐 **공유기 포트포워딩/고정IP 불필요** | 🪟 **터미널 창 없는 무창(Hidden) 백그라운드 무인 상주**

---

## 📑 목차 및 첨부 문서
- 📄 **[PDF 종합 가이드 다운로드](./피클_PC_원격연동_완전정복_가이드.pdf)** (인쇄 및 소장용 4페이지 벡터 PDF)
- [1. 전체 아키텍처 및 원리](#1-전체-아키텍처-및-원리)
- [2. 5단계 빠른 시작 (Quick Start)](#2-5단계-빠른-시작-quick-start)
  - [Step 1: 비공개 깃허브 저장소 및 러너 등록](#step-1-본인의-비공개-저장소-생성-및-러너-등록)
  - [Step 2: 피클 명령 수신 워크플로 등록](#step-2-피클-명령-수신-워크플로-등록)
  - [Step 3: 창 없는 백그라운드 무인 상주 세팅](#step-3-창-없는-백그라운드-무인-상주-세팅)
  - [Step 4: 피클의 눈(화면)과 손(마우스) 도구 세팅](#step-4-피클의-눈화면과-손마우스-도구-세팅)
  - [Step 5: 모바일 피클 앱에서 실전 활용](#step-5-모바일-피클-앱에서-실전-명령-내리기)
- [3. ⚠️ 필수 보안 수칙 (Security Notice)](#3-️-필수-보안-수칙-security-notice)

---

## 1. 전체 아키텍처 및 원리

```
[ 사용자 모바일 피클 앱 ] 
        │ (음성/채팅 명령: "PC 화면 찍어줘", "특정 프로그램 켜줘")
        ▼
[ 피클 AI 비서 (Pickle Agent) ]
        │ gh workflow run pc-commander.yml -f command="..."
        ▼
[ GitHub Actions (Private Repo) ]
        │ 아웃바운드 장기 연결 (포트포워딩 불필요)
        ▼
[ Windows PC (Self-hosted Runner) ] ── (무창 백그라운드 상주)
        ├── capture.py (초고속 화면 캡처 ➜ 스트림 반환)
        ├── click.py (PyAutoGUI 마우스 클릭/단축키)
        └── PowerShell / WMI / Python 실행
```

### 💡 왜 이 방식인가?
| 비교 항목 | 기존 원격 제어 (팀뷰어/애니데스크/디스코드봇) | 피클 ↔ GitHub 러너 연동 파이프라인 |
| :--- | :--- | :--- |
| **비용 (API 토큰)** | 디스코드봇 등은 명령당 비싼 LLM 토큰 소모 | **0원 (외부 LLM API 호출 완전 제로)** |
| **네트워크 환경** | 공유기 포트포워딩, DDNS, 고정 IP 설정 필요 | **100% 아웃바운드 연결 (방화벽/공유기 무관)** |
| **화면 상주 여부** | 검은색 파워셸/CMD 창이 하루 종일 떠 있어야 함 | **VBScript + 스케줄러로 무창(Hidden) 무인 상주** |
| **모바일 편의성** | 모바일에서 작은 마우스를 손가락으로 조작 | **피클 챗으로 한국어 말 한마디면 끝** |

---

## 2. 5단계 빠른 시작 (Quick Start)

### Step 1: 본인의 비공개 저장소 생성 및 러너 등록
> ⚠️ **주의:** 원격 제어용 저장소는 **반드시 비공개(Private)**로 생성하세요! (Public으로 생성 시 타인이 PR을 통해 PC를 조작할 수 있습니다)

1. [GitHub](https://github.com)에서 원격 제어용 개인 비공개 저장소를 하나 생성합니다. (예: `my-pc-control`)
2. 저장소 상단 메뉴 **Settings ➜ Actions ➜ Runners ➜ New self-hosted runner**를 클릭하고 OS로 **Windows**를 선택합니다.
3. 내 PC에서 **PowerShell(관리자 권한)**을 열고 안내된 명령어를 입력합니다:
   ```powershell
   # 러너 폴더 생성
   mkdir actions-runner; cd actions-runner

   # 최신 러너 다운로드 및 압축 해제 (v2.329.0 이상)
   Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v2.338.2/actions-runner-win-x64-2.338.2.zip" -OutFile "runner.zip"
   Expand-Archive -Path "runner.zip" -DestinationPath "." ; Remove-Item runner.zip

   # 내 저장소에 러너 등록 (화면에 뜬 본인 토큰 입력)
   ./config.cmd --url https://github.com/<본인아이디>/<저장소이름> --token <발급받은토큰>
   # (이후 설정 질문은 모두 Enter를 눌러 기본값으로 완료)
   ```

---

### Step 2: 피클 명령 수신 워크플로 등록
피클이 GitHub CLI(`gh`)를 통해 내 PC로 명령을 내릴 수 있도록 저장소에 워크플로를 추가합니다.

내 저장소에 `.github/workflows/pc-commander.yml` 파일을 만들고 아래 코드를 커밋합니다. (템플릿 파일: [`templates/pc-commander.yml`](./templates/pc-commander.yml))

```yaml
name: PC Remote Commander

on:
  workflow_dispatch:
    inputs:
      command:
        description: '실행할 명령어 (PowerShell)'
        required: true
        type: string
        default: 'python --version'

jobs:
  run-on-pc:
    runs-on: self-hosted
    steps:
      - name: Execute Command
        shell: powershell
        run: |
          ${{ github.event.inputs.command }}
```

---

### Step 3: 창 없는 백그라운드 무인 상주 세팅
화면에 검은 터미널 창을 띄워둘 필요 없이, 백그라운드에서 조용히 실행되도록 VBScript와 윈도우 작업 스케줄러를 등록합니다.

PowerShell에서 아래 명령어를 한 번만 실행하면 끝납니다:

```powershell
# 1. 무창 실행 VBScript 생성
$vbsContent = 'Set WshShell = CreateObject("WScript.Shell") : WshShell.Run chr(34) & "C:\Users\" & CreateObject("WScript.Network").UserName & "\actions-runner\run.cmd" & chr(34), 0 : Set WshShell = Nothing'
[System.IO.File]::WriteAllText("$env:USERPROFILE\actions-runner\run-hidden.vbs", $vbsContent, [System.Text.Encoding]::ASCII)

# 2. 윈도우 부팅(로그온) 시 자동 실행되는 작업 스케줄러 등록 (-RunLevel Highest 적용)
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$env:USERPROFILE\actions-runner\run-hidden.vbs`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName "GitHubRunner-Hidden" -Action $action -Trigger $trigger -Principal $principal -Force

# 3. 지금 즉시 백그라운드 실행!
Start-ScheduledTask -TaskName "GitHubRunner-Hidden"
```
*(이제 열려 있는 모든 파워셸 창을 닫아도 러너가 백그라운드에서 영구 상주합니다)*

---

### Step 4: 피클의 눈(화면)과 손(마우스) 도구 세팅
PC의 화면을 캡처하고 마우스를 조작할 수 있도록 필수 파이썬 라이브러리와 스크립트를 세팅합니다.

1. **라이브러리 설치:**
   ```bash
   pip install pillow mss pyautogui
   ```
2. **도구 스크립트 배치:**
   - 내 PC의 `C:\Users\<계정명>\pc-tools\` 폴더를 만들고 아래 2개 스크립트를 넣어둡니다:
     - [`tools/capture.py`](./tools/capture.py): 화면 전체를 초고속 캡처하여 스트림으로 피클에게 전송
     - [`tools/click.py`](./tools/click.py): 지정한 x, y 화면 좌표를 마우스로 자동 클릭

---

### Step 5: 모바일 피클 앱에서 실전 명령 내리기
피클 앱 설정에서 GitHub 계정을 연동해 두면, 밖에서 피클 챗으로 말 한마디만 하면 됩니다:

- 💬 *"지금 내 PC 켜져 있어? 화면 캡처해서 보여줘"*
- 💬 *"바탕화면에 있는 000 폴더 안에 무슨 파일이 있는지 분석해줘"*
- 💬 *"000 프로그램 실행하고 제대로 떴는지 화면 찍어줘"*
- 💬 *"화면 중앙에 뜬 팝업 [확인] 버튼 좀 눌러줘"*

---

## 3. ⚠️ 필수 보안 수칙 (Security Notice)

1. 🔒 **저장소는 무조건 Private(비공개):**
   - GitHub Actions Self-hosted Runner가 연결된 저장소는 **절대 Public(공개)으로 전환하지 마세요.**
   - 타인이 해당 저장소로 악의적인 Pull Request를 보낼 경우 내 PC에서 코드가 실행될 수 있습니다.
2. 🔑 **GitHub Personal Access Token(PAT) 노출 금지:**
   - 깃허브 토큰은 비밀번호와 같습니다. 타인에게 공유하거나 공개 저장소에 커밋하지 마세요.
3. 🛡️ **UAC 및 관리자 권한:**
   - 관리자 권한이 필요한 프로그램을 제어하려면 작업 스케줄러 등록 시 반드시 `-RunLevel Highest` 옵션을 적용하세요.

---

## 📄 라이선스
MIT License. 자유롭게 포크하고 커뮤니티에 공유하세요!
