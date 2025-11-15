# Implementation Plan: 텔레그램 기반 원격 Claude 워커 시스템

**Branch**: `001-telegram-claude-worker` | **Date**: 2025-11-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-telegram-claude-worker/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

랜디가 텔레그램을 통해 원격 Claude 에이전트에게 개발 작업을 위임할 수 있는 시스템을 구축합니다. 시스템은 **2개의 특화된 에이전트**로 구성됩니다:
- **메인 에이전트** (Claude Sonnet): 코딩, GitHub, 명령 실행 등 모든 핵심 작업 수행
- **로거 에이전트** (Claude Haiku): 작업 로그 생성 전용 (비용 효율적)

작업 로그를 통해 세션 간 컨텍스트를 유지하며, GitHub 통합을 통해 버전 관리를 지원합니다. 핵심 기술 스택은 Python 3.13 + uv, python-telegram-bot, Anthropic Claude API, PyGitHub, asyncio입니다.

## Technical Context

**Language/Version**: Python 3.13
**Package Manager**: uv (빠른 Python 패키지 및 프로젝트 관리)
**Primary Dependencies**:
- python-telegram-bot (텔레그램 봇 API)
- anthropic (Anthropic Claude API SDK - Sonnet 4 & Haiku 4)
- PyGithub (GitHub API 통합)
- asyncio (비동기 처리)

**Storage**:
- 작업 로그: `.ccw/logs/` 디렉토리에 마크다운 파일로 저장 (Git 추적)
- 환경 변수:
  - TELEGRAM_BOT_TOKEN (텔레그램 봇 토큰)
  - TELEGRAM_WHITELIST_USER_IDS (화이트리스트 사용자 ID, 쉼표 구분)
  - ANTHROPIC_API_KEY (Claude API 키)
  - GITHUB_TOKEN (GitHub Personal Access Token)

**Testing**: pytest (100% 커버리지 목표)

**Target Platform**: Linux 서버 (원격 개발 환경)

**Project Type**: 단일 프로젝트 (봇 서비스 + CLI 도구)

**Performance Goals**:
- 작업 시작 확인 응답: 10초 이내
- 서버 명령 실행 결과 반환: 30초 이내
- 배포 알림: 5분 이내

**Constraints**:
- 단일 작업 타임아웃: 30분
- 한 번에 하나의 작업만 실행
- 작업 로그 평균 크기: 2000 토큰 이하

**Scale/Scope**:
- 단일 사용자 (랜디)
- 단일 GitHub 리포지토리 (v1.0.0)
- 5개 사용자 스토리 (P1: 3개, P2: 1개, P3: 1개)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. 에이전트 커밋 금지 검증

**준수 여부**: ✅ **통과**

- **spec.md FR-013**: "시스템은 랜디의 명시적 명령이 있을 때만 완료된 작업을 버전 관리에 커밋해야 함"
- **spec.md FR-014**: "시스템은 랜디의 명시적 명령이 있을 때만 GitHub 머지 리퀘스트를 생성해야 함"
- **구현 계획**: 커밋 및 PR 생성은 랜디의 명시적 텔레그램 명령에 의해서만 트리거됩니다

**결론**: 이 원칙은 명세에 명시적으로 반영되어 있으며, 자동 커밋이 발생하지 않도록 설계되었습니다.

### II. 한글 기반 문서화 및 프롬프팅 검증

**준수 여부**: ✅ **통과**

- 모든 명세서, 계획서, 작업 로그는 한글로 작성됩니다
- CCW와 랜디 간의 텔레그램 대화는 한글로 이루어집니다
- 코드 주석도 가능한 한 한글로 작성합니다
- 변수명, 함수명 등은 영어 명명 규칙을 따릅니다 (표준 관행)

**결론**: 이 원칙이 프로젝트 전반에 걸쳐 적용됩니다.

### III. 100% 테스트 커버리지 목표 검증

**준수 여부**: ✅ **통과**

- **spec.md**: "Testing: pytest (100% 커버리지 목표)"
- **구현 계획**: 단위 테스트, 통합 테스트, 계약 테스트를 포함한 포괄적인 테스트 전략 수립 예정
- **작업 분해 시**: 각 기능별로 테스트 작성 작업을 포함할 예정

**결론**: 테스트 우선 접근법을 따르며, 100% 커버리지를 목표로 합니다.

### 복잡성 정당화

이 프로젝트는 헌법의 모든 핵심 원칙을 준수하므로 복잡성 정당화가 필요하지 않습니다.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── channels/                    # 다양한 통신 채널 (확장 가능)
│   ├── __init__.py
│   ├── base.py                 # 채널 기본 인터페이스
│   └── telegram/               # 텔레그램 채널 구현
│       ├── __init__.py
│       ├── bot.py             # 봇 초기화 및 설정
│       ├── handlers.py        # 메시지 핸들러
│       └── auth.py            # 사용자 인증 (화이트리스트)
│   # 향후 추가 가능: slack/, discord/, etc.
│
├── agents/                      # AI 에이전트 (역할별 분리)
│   ├── __init__.py
│   ├── base.py                 # 에이전트 기본 인터페이스
│   ├── main/                   # 메인 에이전트 (Claude Sonnet)
│   │   ├── __init__.py
│   │   ├── executor.py        # 작업 실행 엔진 (코딩, GitHub, 명령 등)
│   │   ├── context.py         # 컨텍스트 관리 (작업 로그 읽기)
│   │   ├── timeout.py         # 타임아웃 관리 (30분 제한)
│   │   └── prompts.py         # 메인 에이전트 프롬프트 템플릿
│   │
│   └── logger/                 # 로깅 에이전트 (Claude Haiku, 저비용)
│       ├── __init__.py
│       ├── executor.py        # 로그 생성 엔진
│       └── prompts.py         # 로깅 에이전트 프롬프트 (간결성 강조)
│
├── tools/                       # 에이전트가 사용하는 도구 모음
│   ├── __init__.py
│   ├── github/                 # GitHub 관련 도구
│   │   ├── __init__.py
│   │   ├── client.py          # PyGithub 클라이언트
│   │   ├── commit.py          # 커밋 생성 도구
│   │   ├── pr.py              # 머지 리퀘스트 생성 도구
│   │   └── deployment.py      # 배포 상태 모니터링 도구
│   │
│   ├── logging/                # 작업 로그 관리 도구
│   │   ├── __init__.py
│   │   ├── writer.py          # 로그 작성 도구
│   │   ├── reader.py          # 로그 읽기 도구 (마지막 2개)
│   │   └── parser.py          # 로그 파싱 도구 (컨텍스트 추출)
│   │
│   ├── bash/                   # Bash 명령 실행 도구
│   │   ├── __init__.py
│   │   ├── executor.py        # 명령 실행 도구
│   │   └── validator.py       # 명령 검증 도구 (파괴적 명령 차단)
│   │
│   └── coding/                 # 코딩 작업 도구 (메인 에이전트가 코딩할 때 사용)
│       ├── __init__.py
│       ├── file_io.py         # 파일 읽기/쓰기 도구
│       ├── search.py          # 코드 검색 도구 (grep, find)
│       ├── editor.py          # 코드 편집/변경 도구
│       └── navigator.py       # 디렉토리 탐색 도구
│
├── constants.py                 # 프로젝트 전역 상수
│                                # - 타임아웃: 30분
│                                # - 로그 토큰 제한: 2000
│                                # - LLM 모델: MAIN_AGENT_MODEL = "claude-sonnet-4"
│                                #            LOGGER_AGENT_MODEL = "claude-haiku-4"
│                                # - 파일 경로, 명령 블랙리스트 등
├── config.py                    # 환경 변수 관리
├── models.py                    # 데이터 모델 (TaskInstruction, TaskLog, etc.)
└── main.py                      # 애플리케이션 진입점

tests/
├── unit/
│   ├── channels/
│   │   └── test_telegram_auth.py
│   ├── agents/
│   │   ├── test_main_agent_executor.py
│   │   └── test_logger_agent_executor.py
│   └── tools/
│       ├── test_coding_file_io.py
│       ├── test_coding_search.py
│       ├── test_coding_editor.py
│       ├── test_github_client.py
│       ├── test_log_writer.py
│       └── test_bash_validator.py
├── integration/
│   ├── test_telegram_channel_integration.py
│   ├── test_main_agent_integration.py
│   ├── test_logger_agent_integration.py
│   ├── test_coding_tool_integration.py
│   └── test_github_tool_integration.py
└── contract/
    ├── test_telegram_api_contract.py
    ├── test_claude_api_contract.py      # Anthropic API 호출 검증
    └── test_github_api_contract.py

.ccw/
└── logs/                        # 작업 로그 저장 위치 (Git 추적)
    └── issue-{number}-{slug}.md
```

**Structure Decision**:

확장 가능하면서도 실용적인 모듈형 아키텍처를 선택했습니다. 주요 설계 원칙:

1. **channels/**: 다양한 통신 채널을 지원할 수 있도록 설계 (현재: telegram, 향후: slack, discord 등)

2. **agents/**: **2개의 특화된 에이전트로 최적화**
   - **main/** (Claude Sonnet): 모든 핵심 작업 수행 (코딩, GitHub, 요구사항 이해 등)
   - **logger/** (Claude Haiku): 작업 로그 생성 전용 (비용 효율적)

   **왜 2개인가?**
   - 메인 작업과 로깅은 요구사항이 다름 (품질 vs 간결성)
   - Haiku를 로깅에 사용하면 토큰 비용을 크게 절감
   - 2개 이상 쪼개면 컨텍스트 전달 오버헤드와 레이턴시 증가
   - 각 에이전트의 프롬프트를 독립적으로 튜닝 가능 (prompts.py)

3. **tools/**: 에이전트가 사용하는 도구를 기능별로 분리하여 재사용성 및 테스트 가능성 향상
   - `github/`: 버전 관리 및 배포 관련 도구
   - `logging/`: 작업 로그 파일 I/O 도구
   - `bash/`: 서버 명령 실행 도구
   - `coding/`: 코딩 작업 도구 (파일 읽기/쓰기, 검색, 편집, 탐색, 분석)

4. **constants.py**: 모든 매직 넘버와 설정을 중앙 관리
   - 타임아웃(30분), 로그 토큰 제한(2000)
   - LLM 모델 지정 (Sonnet vs Haiku)
   - 파일 경로, 명령 블랙리스트 등

5. **base.py 패턴**: 각 확장 가능한 모듈(channels, agents)에 기본 인터페이스를 제공하여 일관성 유지

이 구조는 단일 프로젝트이지만 향후 확장성을 고려하여 명확히 계층화되었으며, 각 모듈은 독립적으로 테스트 가능합니다. 특히 에이전트는 "비용과 성능의 균형"을 고려하여 실용적으로 2개로 제한했습니다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

해당 사항 없음 - 모든 헌법 원칙을 준수합니다.

## Phase 0: Research & Technical Decisions

### 조사가 필요한 항목

1. **uv 패키지 관리자 베스트 프랙티스**
   - Python 3.13과의 호환성 확인
   - `pyproject.toml` vs `requirements.txt` 사용 전략
   - 가상 환경 관리 방법 (`uv venv`)
   - 의존성 잠금 파일 (`uv.lock`) 관리

2. **Anthropic Claude API 및 다중 에이전트 패턴**
   - Claude API (Sonnet 4, Haiku 4) Python SDK 사용법
   - Python 3.13 호환성 검증
   - 2개 에이전트 패턴 구현 방법 (메인 + 로거)
   - 작업 실행 및 타임아웃 관리 방법
   - 컨텍스트 주입 방법 (작업 로그를 메인 에이전트에 전달)
   - 에이전트 간 데이터 전달 (메인 에이전트 → 로거 에이전트)

3. **python-telegram-bot 라이브러리 베스트 프랙티스**
   - 비동기 처리 패턴 (asyncio 통합)
   - 메시지 핸들러 구조
   - 에러 처리 및 재시도 전략
   - 사용자 인증 패턴

4. **PyGithub를 통한 GitHub Actions 배포 모니터링**
   - Workflow 실행 상태 조회 방법
   - Webhook vs Polling 비교
   - 실패 원인 추출 방법

5. **작업 로그 설계**
   - 마크다운 템플릿 구조
   - 토큰 최적화 전략 (간결성 vs 충분한 세부사항)
   - 이슈별 로그 파일 명명 규칙
   - 로그 분할 기준 (합리적인 토큰 예산 초과 시)

6. **파괴적 명령 차단 로직**
   - 차단할 명령 패턴 목록 (rm, mv, chmod, systemctl 등)
   - 대화형 명령 감지 방법 (vi, nano, top 등)
   - 안전한 명령 화이트리스트 vs 위험 명령 블랙리스트 접근법 비교

7. **코딩 도구 구현 전략**
   - 파일 I/O: 안전한 읽기/쓰기 방법 (경로 검증, 권한 체크)
   - 코드 검색: ripgrep 기반 빠른 검색
   - 코드 편집: 문자열 치환 기반 (간단하고 예측 가능)
   - 디렉토리 탐색: glob 패턴, 재귀 탐색, gitignore 준수

### 조사 산출물

조사 결과는 `research.md` 파일에 다음 형식으로 문서화됩니다:

```markdown
## [조사 항목]

**결정**: [채택한 방법/기술]
**근거**: [왜 이 방법을 선택했는가]
**대안 검토**: [검토한 다른 옵션과 기각 이유]
**구현 고려사항**: [구현 시 주의할 점]
```

## Phase 1: Design & Contracts

### 데이터 모델 (`data-model.md`)

Phase 0 조사 완료 후, 다음 엔티티에 대한 상세 데이터 모델을 작성합니다:

1. **TaskInstruction (작업 지시)**
   - 필드: id, user_id, message, timestamp, status, timeout_at
   - 상태: pending, running, completed, failed, timeout

2. **TaskLog (작업 로그)**
   - 필드: issue_id, issue_slug, entries[], created_at, updated_at, token_count
   - entry: timestamp, type (discussion/decision/issue/action), content
   - 생성 주체: logger 에이전트 (Haiku)

3. **ServerCommand (서버 명령)**
   - 필드: command_text, is_safe, blocked_reason, output, exit_code

4. **DeploymentStatus (배포 상태)**
   - 필드: workflow_id, status, started_at, completed_at, failure_reason

5. **AgentResponse (에이전트 응답)**
   - 필드: agent_type (main/logger), model_used, input_tokens, output_tokens, response_data
   - 용도: 비용 추적 및 디버깅

### API 계약 (`contracts/`)

1. **텔레그램 봇 명령어 계약** (`telegram-commands.md`)
   - 작업 지시 메시지 형식
   - 커밋 명령어 형식
   - 머지 리퀘스트 명령어 형식
   - 서버 명령 실행 형식

2. **Claude API 호출 계약** (`claude-api-interface.md`)
   - 메인 에이전트 (Sonnet) 호출 인터페이스
   - 로거 에이전트 (Haiku) 호출 인터페이스
   - 컨텍스트 주입 형식 (시스템 프롬프트 + 작업 로그)
   - 타임아웃 설정 방법
   - 토큰 사용량 추적

3. **GitHub API 사용 계약** (`github-api-usage.md`)
   - 커밋 생성 API
   - PR 생성 API
   - Workflow 상태 조회 API

### 빠른 시작 가이드 (`quickstart.md`)

Phase 1 완료 후, 다음 내용을 포함하는 빠른 시작 가이드를 작성합니다:

1. **환경 설정**
   - Python 3.13 설치
   - uv 설치 (`curl -LsSf https://astral.sh/uv/install.sh | sh` 또는 `pip install uv`)
   - 프로젝트 초기화 (`uv init` - 이미 존재하는 경우 생략)
   - 의존성 설치 (`uv sync` 또는 `uv pip install -r requirements.txt`)
   - 환경 변수 설정 (`.env` 파일 생성):
     ```
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     TELEGRAM_WHITELIST_USER_IDS=123456789,987654321
     ANTHROPIC_API_KEY=your_anthropic_api_key
     GITHUB_TOKEN=your_github_token
     ```

2. **텔레그램 봇 생성**
   - BotFather를 통한 봇 생성
   - 토큰 발급
   - 화이트리스트 사용자 ID 확인 방법 (텔레그램에서 `/start` 보내면 봇이 user_id 반환)

3. **Anthropic API 키 발급**
   - Anthropic Console에서 API 키 생성
   - Sonnet 4와 Haiku 4 모델 액세스 권한 확인

4. **GitHub 토큰 발급**
   - Personal Access Token 생성
   - 필요한 권한 (repo, workflow)

5. **로컬 실행**
   - `uv run python src/main.py` 실행
   - 텔레그램으로 테스트 메시지 전송

6. **테스트 실행**
   - `uv run pytest` 실행
   - 커버리지 확인 (`uv run pytest --cov`)

## Phase 2: Task Breakdown

Phase 1 완료 후, `/speckit.tasks` 명령을 사용하여 `tasks.md`를 생성합니다.

작업은 다음 우선순위에 따라 분해됩니다:

1. **P1 작업** (핵심 기능):
   - 텔레그램 채널 구현 (bot, handlers, auth)
   - 사용자 인증 (화이트리스트)
   - 메인 에이전트 구현 (Sonnet, 작업 실행)
   - 로거 에이전트 구현 (Haiku, 로그 생성)
   - 코딩 도구 구현 (file_io, search, editor, navigator)
   - 메인 에이전트 - 코딩 도구 통합
   - 컨텍스트 관리 (작업 로그 읽기 → 메인 에이전트 주입)
   - 에이전트 간 데이터 흐름 (메인 → 로거)
   - 타임아웃 관리 (30분)

2. **P2 작업** (버전 관리):
   - GitHub 도구 구현 (커밋, PR, 배포)
   - 메인 에이전트 - GitHub 도구 통합
   - 배포 상태 모니터링

3. **P3 작업** (서버 명령):
   - Bash 도구 구현 (명령 검증, 실행)
   - 메인 에이전트 - Bash 도구 통합
   - 파괴적 명령 블랙리스트

각 작업은 독립적으로 테스트 가능하며, 테스트 작성을 포함합니다.

**핵심 작업 흐름**:
1. 랜디 → 텔레그램 → 채널 → 메인 에이전트 (작업 실행)
2. 메인 에이전트 → 도구들 사용:
   - **coding**: 파일 읽기/쓰기, 코드 검색, 편집, 탐색, 분석
   - **github**: 커밋, PR, 배포 모니터링
   - **bash**: 서버 명령 실행
3. 메인 에이전트 → 로거 에이전트 → 작업 로그 생성 → `.ccw/logs/`
4. 다음 작업 시 → 마지막 2개 로그 읽기 → 메인 에이전트 컨텍스트로 주입

## 성공 기준

이 구현 계획은 다음 조건이 충족되면 완료됩니다:

- ✅ Constitution Check 통과 (모든 헌법 원칙 준수)
- ⏳ Phase 0: `research.md` 생성 (모든 NEEDS CLARIFICATION 해결)
- ⏳ Phase 1: `data-model.md`, `contracts/`, `quickstart.md` 생성
- ⏳ Phase 1: CLAUDE.md 업데이트 (기술 스택 추가)
- ⏳ Phase 2: `/speckit.tasks` 실행 준비 완료

다음 단계: Phase 0 조사 시작
