# my-remote-worker

텔레그램 기반 원격 Claude 워커 시스템 - 텔레그램으로 개발 작업을 지시하고 Claude 에이전트가 수행하는 시스템

## 개요

CCW(Claude Code Worker)는 랜디가 텔레그램을 통해 원격 Claude 에이전트에게 개발 작업을 위임할 수 있는 시스템입니다. 시스템은 2개의 특화된 에이전트로 구성됩니다:

- **메인 에이전트** (Claude Sonnet): 코딩, GitHub, 명령 실행 등 모든 핵심 작업 수행
- **로거 에이전트** (Claude Haiku): 작업 로그 생성 전용 (비용 효율적)

## 주요 기능

- 텔레그램을 통한 원격 작업 실행
- 세션 간 컨텍스트 유지 (최근 2개 작업 로그 자동 로드)
- 자동 작업 로그 문서화 (마크다운)
- GitHub 통합 (커밋, PR 생성, 배포 모니터링)
- 안전한 서버 명령 실행 (파괴적 명령 차단)

## 기술 스택

- **언어**: Python 3.13
- **패키지 관리**: uv
- **주요 의존성**:
  - python-telegram-bot (텔레그램 봇 API)
  - anthropic (Claude API SDK)
  - PyGithub (GitHub API)
  - asyncio (비동기 처리)

## 빠른 시작

### 1. 환경 설정

```bash
# Python 3.13 설치 확인
python --version

# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh
# 또는
pip install uv

# 프로젝트 의존성 설치
uv sync
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 값을 입력합니다:

```bash
cp .env.example .env
```

필요한 환경 변수:
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰 (BotFather에서 발급)
- `TELEGRAM_WHITELIST_USER_IDS`: 허용된 사용자 ID (쉼표 구분)
- `ANTHROPIC_API_KEY`: Anthropic API 키
- `GITHUB_TOKEN`: GitHub Personal Access Token (권한: repo, workflow)

### 3. 실행

```bash
# 봇 실행
uv run python src/main.py
```

### 4. 테스트

```bash
# 전체 테스트 실행
uv run pytest

# 커버리지 포함
uv run pytest --cov=src --cov-report=html
```

## 텔레그램 명령어

- `/task [작업 내용]` - 개발 작업 요청
- `/diff` - 현재 변경 사항 확인
- `/commit [메시지]` - Git 커밋 생성
- `/branch [브랜치명]` - 새 브랜치 생성
- `/mr` - GitHub 머지 리퀘스트 생성
- `/exec [명령어]` - 서버 명령 실행
- `/logs` - 최근 작업 로그 조회

## 프로젝트 구조

```
src/
├── agents/          # AI 에이전트 (main, logger)
├── tools/           # 에이전트 도구 (coding, github, bash, logging)
├── telegram/        # 텔레그램 봇 및 핸들러
├── models/          # 데이터 모델
├── tasks/           # 작업 실행 관리
├── utils/           # 유틸리티 (config, errors)
├── constants.py     # 전역 상수
└── main.py          # 진입점

tests/
├── unit/            # 단위 테스트
├── integration/     # 통합 테스트
└── contract/        # 계약 테스트

.ccw/
└── logs/            # 작업 로그 (Git 추적)
```

## 개발

### 코드 스타일

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

### 테스트 작성

- 단위 테스트: `tests/unit/`
- 통합 테스트: `tests/integration/`
- 계약 테스트: `tests/contract/`
- 커버리지 목표: 100%

## 라이선스

MIT

## 작성자

Randy
