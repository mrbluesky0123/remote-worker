# Quick Start Guide: CCW (Claude Code Worker)

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-08
**버전**: 1.0.0

## 개요

이 가이드는 CCW(Claude Code Worker) 텔레그램 봇을 로컬 및 원격 서버에 설정하고 실행하는 방법을 안내합니다.

---

## 사전 요구사항

### 시스템 요구사항

- **OS**: Ubuntu 20.04 LTS 이상 (권장) 또는 macOS
- **Python**: 3.13 이상
- **Git**: 2.30 이상
- **uv**: 최신 버전

### 계정 요구사항

1. **Telegram**: 봇 생성 및 사용자 ID 확인
2. **Anthropic**: Claude API 키
3. **GitHub**: Personal Access Token (PAT)

---

## 1단계: 사전 준비

### 1.1 Python 3.13 설치

**Ubuntu**:
```bash
# 패키지 업데이트
sudo apt update

# Python 3.13 설치 (deadsnakes PPA 사용)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# 버전 확인
python3.13 --version
```

**macOS**:
```bash
# Homebrew 사용
brew install python@3.13

# 버전 확인
python3.13 --version
```

### 1.2 uv 설치

```bash
# uv 설치 (공식 스크립트)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 버전 확인
uv --version
```

### 1.3 Git 설정

```bash
# Git 사용자 정보 설정
git config --global user.name "Randy"
git config --global user.email "randy@example.com"
```

---

## 2단계: 외부 서비스 설정

### 2.1 Telegram 봇 생성

1. **BotFather와 대화 시작**:
   - Telegram에서 [@BotFather](https://t.me/botfather) 검색
   - `/start` 명령 전송

2. **새 봇 생성**:
   ```
   /newbot
   ```
   - 봇 이름 입력: `CCW Bot`
   - 봇 사용자명 입력: `ccw_bot` (고유해야 함)

3. **API 토큰 저장**:
   - BotFather가 제공하는 토큰 복사
   - 예시: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

4. **사용자 ID 확인**:
   - [@userinfobot](https://t.me/userinfobot)에게 메시지 전송
   - 표시된 사용자 ID 복사
   - 예시: `123456789`

### 2.2 Anthropic API 키 발급

1. [Anthropic Console](https://console.anthropic.com/) 접속
2. 로그인 또는 계정 생성
3. **API Keys** 메뉴 선택
4. **Create Key** 클릭
5. API 키 복사 (예시: `sk-ant-xxxxxxxxxxxxx`)

### 2.3 GitHub Personal Access Token 생성

1. [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens) 접속
2. **Generate new token (classic)** 클릭
3. **Note**: `CCW Bot`
4. **Expiration**: 90 days (또는 원하는 기간)
5. **Scopes** 선택:
   - ✓ `repo` (전체)
   - ✓ `workflow`
6. **Generate token** 클릭
7. 토큰 복사 (예시: `ghp_xxxxxxxxxxxxx`)
   - ⚠️ 이 토큰은 다시 표시되지 않으므로 안전하게 보관

---

## 3단계: 프로젝트 설정

### 3.1 리포지토리 클론

```bash
# 홈 디렉토리로 이동
cd ~

# 리포지토리 클론
git clone https://github.com/your-username/my-remote-worker.git
cd my-remote-worker

# 기능 브랜치로 전환
git checkout 001-telegram-claude-worker
```

### 3.2 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**.env 파일 내용**:
```bash
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWED_USERS=123456789

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_REPO=your-username/my-remote-worker

# Application
TASK_TIMEOUT_MINUTES=30
MAX_LOG_COUNT=2
LOG_DIRECTORY=.ccw/logs
```

**주의**:
- `TELEGRAM_ALLOWED_USERS`: 여러 사용자는 쉼표로 구분 (예: `123,456,789`)
- `GITHUB_REPO`: `owner/repo` 형식

### 3.3 의존성 설치

```bash
# uv를 사용한 가상환경 생성 및 의존성 설치
uv sync

# 가상환경 활성화
source .venv/bin/activate

# 설치 확인
python --version
pip list
```

**예상 출력**:
```
Python 3.13.0
Package           Version
----------------- -------
python-telegram-bot 20.x.x
anthropic         0.8.x
PyGithub          2.x.x
pytest            7.x.x
...
```

### 3.4 디렉토리 생성

```bash
# 작업 로그 디렉토리 생성
mkdir -p .ccw/logs

# 소스 디렉토리 구조 확인
tree src/
```

---

## 4단계: 로컬 테스트

### 4.1 환경 변수 검증

```bash
# 환경 변수 로드 테스트
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
for var in required:
    value = os.environ.get(var)
    if value:
        print(f'✓ {var}: {value[:10]}...')
    else:
        print(f'✗ {var}: NOT SET')
"
```

**예상 출력**:
```
✓ TELEGRAM_BOT_TOKEN: 123456789:...
✓ ANTHROPIC_API_KEY: sk-ant-xxx...
✓ GITHUB_TOKEN: ghp_xxxxxx...
```

### 4.2 단위 테스트 실행

```bash
# pytest 실행
pytest tests/unit/ -v

# 커버리지 포함
pytest tests/unit/ --cov=src --cov-report=term-missing
```

### 4.3 봇 시작 (개발 모드)

```bash
# 봇 실행
python src/main.py
```

**예상 출력**:
```
2025-11-08 10:30:00 - INFO - CCW Bot 시작
2025-11-08 10:30:00 - INFO - 허용된 사용자: [123456789]
2025-11-08 10:30:00 - INFO - 텔레그램 폴링 시작...
```

### 4.4 텔레그램에서 테스트

1. Telegram 앱 열기
2. 생성한 봇 검색 (예: `@ccw_bot`)
3. 대화 시작: `/start`
4. 테스트 명령어:
   ```
   /task src/test.py에 "Hello World" 출력 추가
   ```

5. 응답 확인:
   ```
   ✅ 작업을 시작합니다.

   작업 ID: abc-123
   설명: src/test.py에 "Hello World" 출력 추가
   예상 완료: 30분 이내
   ```

---

## 5단계: 원격 서버 배포

### 5.1 서버 접속

```bash
# SSH 접속
ssh randy@your-server-ip

# 작업 디렉토리 생성
mkdir -p ~/my-remote-worker
cd ~/my-remote-worker
```

### 5.2 배포 스크립트 실행

**deploy.sh** 생성:
```bash
#!/bin/bash

# 리포지토리 클론 또는 업데이트
if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/your-username/my-remote-worker.git .
fi

# 브랜치 전환
git checkout 001-telegram-claude-worker

# 의존성 설치
uv sync

# 로그 디렉토리 생성
mkdir -p .ccw/logs

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 설정하세요."
    exit 1
fi

echo "✅ 배포 완료"
```

실행:
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5.3 systemd 서비스 설정

**/etc/systemd/system/ccw.service** 생성:
```ini
[Unit]
Description=Claude Code Worker Telegram Bot
After=network.target

[Service]
Type=simple
User=randy
WorkingDirectory=/home/randy/my-remote-worker
Environment="PATH=/home/randy/.local/bin:/usr/local/bin:/usr/bin"
EnvironmentFile=/home/randy/my-remote-worker/.env
ExecStart=/home/randy/.local/bin/uv run python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 등록 및 시작:
```bash
# 서비스 파일 복사 (sudo 필요)
sudo cp ccw.service /etc/systemd/system/

# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable ccw

# 서비스 시작
sudo systemctl start ccw

# 상태 확인
sudo systemctl status ccw
```

**예상 출력**:
```
● ccw.service - Claude Code Worker Telegram Bot
   Loaded: loaded (/etc/systemd/system/ccw.service; enabled)
   Active: active (running) since Fri 2025-11-08 10:30:00 UTC; 5s ago
 Main PID: 12345 (python)
   CGroup: /system.slice/ccw.service
           └─12345 python src/main.py

Nov 08 10:30:00 server systemd[1]: Started Claude Code Worker Telegram Bot.
Nov 08 10:30:00 server python[12345]: INFO - CCW Bot 시작
```

### 5.4 로그 확인

```bash
# systemd 로그 (실시간)
sudo journalctl -u ccw -f

# 애플리케이션 로그
tail -f .ccw/app.log
```

---

## 6단계: GitHub Actions 설정 (선택)

### 6.1 워크플로우 파일 생성

**.github/workflows/deploy.yml**:
```yaml
name: Deploy CCW

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: randy
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/randy/my-remote-worker
            git pull
            uv sync
            sudo systemctl restart ccw
```

### 6.2 GitHub Secrets 설정

1. GitHub 리포지토리 > **Settings** > **Secrets and variables** > **Actions**
2. **New repository secret** 클릭
3. 다음 시크릿 추가:
   - `SERVER_HOST`: 서버 IP 주소
   - `SSH_PRIVATE_KEY`: SSH 프라이빗 키

---

## 7단계: 사용 예시

### 예시 1: 간단한 작업

```
User: /task main.py에 "Hello, CCW!" 출력 추가

Bot: ✅ 작업을 시작합니다.
     작업 ID: abc-123
     ...

(15초 후)

Bot: ✅ 작업이 완료되었습니다!

     **수행한 작업**:
     - main.py에 print("Hello, CCW!") 추가

     **변경된 파일**:
     - main.py (수정)
```

### 예시 2: 변경사항 커밋

```
User: /diff

Bot: 📊 변경사항 요약

     **변경된 파일**: 1개

     **수정**:
     - main.py (+1, -0 lines)

     **제안 커밋 메시지**:
     feat: Add greeting message

     이 메시지로 커밋하려면: /commit feat: Add greeting message

User: /commit feat: Add greeting message

Bot: ✅ 커밋이 완료되었습니다.

     커밋 SHA: a1b2c3d
     브랜치: 001-telegram-claude-worker
```

### 예시 3: Merge Request 생성

```
User: /mr

Bot: ✅ Merge Request가 생성되었습니다.

     **제목**: feat: Add greeting message
     **소스 브랜치**: 001-telegram-claude-worker
     **타겟 브랜치**: main

     **링크**: https://github.com/owner/repo/pull/123
```

---

## 트러블슈팅

### 문제 1: 봇이 응답하지 않음

**원인**: Telegram 봇 토큰 오류 또는 네트워크 문제

**해결 방법**:
```bash
# 토큰 확인
echo $TELEGRAM_BOT_TOKEN

# 네트워크 연결 확인
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe

# 로그 확인
sudo journalctl -u ccw -n 50
```

### 문제 2: Claude API 오류

**원인**: API 키 만료 또는 레이트 리미트

**해결 방법**:
```bash
# API 키 확인
echo $ANTHROPIC_API_KEY

# 로그에서 오류 확인
grep "anthropic" .ccw/app.log

# 재시도 대기
```

### 문제 3: GitHub 인증 실패

**원인**: PAT 만료 또는 권한 부족

**해결 방법**:
```bash
# PAT 권한 확인 (GitHub 웹사이트)
# 새 PAT 생성
# .env 파일 업데이트
nano .env

# 서비스 재시작
sudo systemctl restart ccw
```

### 문제 4: 작업 로그 생성 실패

**원인**: 디렉토리 권한 오류

**해결 방법**:
```bash
# 디렉토리 생성 및 권한 설정
mkdir -p .ccw/logs
chmod 755 .ccw
chmod 755 .ccw/logs

# 소유자 확인
ls -la .ccw/
```

---

## 다음 단계

Quick Start 가이드 완료! 다음 작업:

1. ✅ 로컬 환경에서 테스트
2. ✅ 원격 서버에 배포
3. ✅ GitHub Actions 설정 (선택)
4. 📖 [사용자 가이드](../README.md) 읽기
5. 🔧 [개발 가이드](./development.md) 참고 (개발 참여 시)

---

## 참고 자료

- [python-telegram-bot 문서](https://docs.python-telegram-bot.org/)
- [Anthropic Claude API 문서](https://docs.anthropic.com/)
- [PyGitHub 문서](https://pygithub.readthedocs.io/)
- [uv 문서](https://docs.astral.sh/uv/)

## 지원

문제가 발생하면:
1. 로그 확인 (`sudo journalctl -u ccw -f`)
2. GitHub Issues에 보고
3. Telegram으로 관리자에게 문의
