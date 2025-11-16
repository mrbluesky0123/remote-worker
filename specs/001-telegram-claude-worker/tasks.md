# Tasks: 텔레그램 기반 원격 Claude 워커 시스템

**기능 브랜치**: `001-telegram-claude-worker`
**입력 문서**: plan.md, spec.md, data-model.md, research.md, contracts/, quickstart.md
**생성일**: 2025-11-10
**최종 업데이트**: 2025-11-15 (아키텍처 최적화: 2개 에이전트, 도구 세분화, 시간 기반 로그)

## 작업 형식: `[ID] [P?] [Story] 설명`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 사용자 스토리 레이블 (US1, US2, US3 등)
- 모든 작업에 정확한 파일 경로 포함

## 브랜치 전략

**메인 브랜치**: `001-telegram-claude-worker`

**Phase별 브랜치 전략**:
- **Phase 1 (Setup)**: 메인 브랜치에서 직접 작업
- **Phase 2 (Foundational)**: 메인 브랜치에서 직접 작업 (모든 스토리의 기반)
- **Phase 3+ (User Stories)**: 각 스토리별 서브 브랜치 생성 가능
  - `001-telegram-claude-worker-us1` (US1: 원격 작업 실행)
  - `001-telegram-claude-worker-us2` (US2: 컨텍스트 관리)
  - `001-telegram-claude-worker-us3` (US3: 작업 로그)
  - `001-telegram-claude-worker-us4` (US4: Git 통합)
  - `001-telegram-claude-worker-us5` (US5: 서버 명령)

**병렬 개발 전략**:
- Phase 2 완료 후, US1/US2/US3는 독립적으로 병렬 개발 가능
- US4는 US3 완료 필요 (커밋 메시지 생성에 로그 필요)
- US5는 독립적 (언제든지 개발 가능)

---

## Phase 1: Setup (프로젝트 초기화)

**목적**: 프로젝트 구조 및 기본 설정

- [X] T001 프로젝트 루트에 pyproject.toml 생성 (uv 기반 Python 3.13 프로젝트)
- [X] T002 프로젝트 루트에 .env.example 파일 생성 (환경 변수 템플릿)
- [X] T003 [P] 프로젝트 루트에 .gitignore 파일 생성 (.env, .ccw/app.log, __pycache__ 등)
- [X] T004 [P] 프로젝트 루트에 README.md 생성 (프로젝트 설명)
- [X] T005 src/ 디렉토리 구조 생성 (agents/, tools/, telegram/, git/, tasks/, commands/, models/, utils/)
- [X] T006 tests/ 디렉토리 구조 생성 (unit/, integration/, contract/)
- [X] T007 [P] .ccw/logs/ 디렉토리 생성 (작업 로그 저장소)
- [X] T008 [P] src/utils/config.py 생성 (환경 변수 로드 및 검증)
- [X] T009 [P] src/utils/errors.py 생성 (커스텀 예외 클래스 정의)

---

## Phase 2: Foundational (기반 인프라)

**목적**: 모든 사용자 스토리가 의존하는 핵심 인프라 구축

**⚠️ CRITICAL**: 이 Phase가 완료되어야 모든 사용자 스토리 작업을 시작할 수 있습니다

### 2.1 기본 에이전트 인프라

- [X] T010 src/agents/base.py 생성 (BaseAgent 추상 클래스 구현)
- [X] T011 src/agents/__init__.py 생성 (에이전트 모듈 초기화)

### 2.2 도구(Tools) 인프라

**코딩 도구 (4개 세분화)**:
- [X] T012 [P] src/tools/__init__.py 생성 (TOOLS, TOOL_FUNCTIONS 정의)
- [X] T013 [P] src/tools/coding/file_io.py 생성 (read_file, write_file, edit_file 도구 구현)
- [X] T014 [P] src/tools/coding/search.py 생성 (glob_files, grep 도구 구현)
- [X] T015 [P] src/tools/coding/editor.py 생성 (문자열 치환 기반 편집 도구)
- [X] T016 [P] src/tools/coding/navigator.py 생성 (디렉토리 탐색 도구)

**기타 도구**:
- [X] T018 [P] src/tools/bash/executor.py 생성 (bash, bash_output 도구 구현)
- [X] T019 [P] src/tools/bash/validator.py 생성 (명령어 검증 도구)

### 2.3 텔레그램 봇 기반 인프라

- [X] T020 src/telegram/auth.py 생성 (화이트리스트 사용자 인증 구현)
- [X] T021 src/telegram/bot.py 생성 (텔레그램 봇 초기화 및 폴링 시작)
- [X] T022 src/telegram/handlers.py 생성 (명령어 핸들러 스켈레톤)
- [X] T023 src/telegram/__init__.py 생성 (텔레그램 모듈 초기화)

### 2.4 데이터 모델

- [X] T024 [P] src/models/task.py 생성 (Task, TaskStatus, AgentType 모델)
- [X] T025 [P] src/models/log.py 생성 (TaskLog 모델 및 시간 기반 마크다운 변환)
- [X] T026 [P] src/models/session.py 생성 (AgentSession 모델)
- [X] T027 [P] src/models/__init__.py 생성 (모델 모듈 초기화)

### 2.5 작업 관리 기반

- [X] T028 src/tasks/executor.py 생성 (작업 실행 및 타임아웃 관리 기본 구조)
- [X] T029 src/tasks/__init__.py 생성 (작업 모듈 초기화)

### 2.6 상수 및 설정

- [X] T030 [P] src/constants.py 생성 (MAIN_AGENT_MODEL, LOGGER_AGENT_MODEL, 타임아웃, 로그 토큰 제한 등)

### 2.7 메인 진입점

- [X] T031 src/main.py 생성 (애플리케이션 진입점, 봇 시작)

**Checkpoint**: 기반 인프라 완료 - 이제 사용자 스토리 구현을 병렬로 시작할 수 있습니다

---

## Phase 3: User Story 1 - 텔레그램을 통한 원격 작업 실행 (우선순위: P1) 🎯 MVP

**목표**: 텔레그램으로 개발 작업 지시를 보내고, CCW가 작업을 수행하고 결과를 보고

**독립 테스트**: 텔레그램으로 "/task main.py에 주석 추가"를 보내고, 에이전트가 작업을 완료하고 확인 응답을 보내는지 검증

**브랜치 옵션**: `001-telegram-claude-worker-us1` (선택사항, 메인에서 직접 작업 가능)

### 3.1 메인 에이전트 구현 (Sonnet 4)

- [X] T032 [P] [US1] src/agents/main/executor.py 생성 (MainAgent 클래스, execute 메서드, 모든 도구 통합)
- [X] T033 [US1] src/agents/main/executor.py에 도구 호출 루프 구현 (Claude API tool_use 처리)
- [X] T034 [US1] src/agents/main/prompts.py 생성 (메인 에이전트 시스템 프롬프트 정의: 한글, 30분 제약, 커밋 금지)
- [X] T035 [US1] src/agents/main/executor.py에 코딩 도구 통합 (file_io, search, editor, navigator)

### 3.2 텔레그램 /task 명령어 핸들러

- [X] T036 [US1] src/telegram/handlers.py에 task_command 핸들러 구현 (작업 수신, 검증, 실행 시작)
- [X] T037 [US1] src/telegram/handlers.py에 작업 진행 중 체크 로직 추가 (TaskManager 싱글톤 사용)
- [X] T038 [US1] src/telegram/handlers.py에 작업 완료 알림 전송 로직 추가

### 3.3 작업 실행 관리

- [X] T039 [US1] src/tasks/executor.py에 execute_task_with_timeout 함수 구현 (asyncio.wait_for 사용)
- [X] T040 [US1] src/tasks/executor.py에 TaskManager 싱글톤 클래스 구현 (현재 작업 추적)
- [X] T041 [US1] src/tasks/executor.py에 서버 재시작 감지 및 중단 작업 로깅 추가

### 3.4 통합 및 검증

- [X] T042 [US1] src/telegram/bot.py에 /task 명령어 핸들러 등록
- [X] T043 [US1] src/main.py에서 봇 시작 및 환경 변수 검증 추가

**Checkpoint**: US1 완료 - 텔레그램으로 작업 지시를 보내고 결과를 받을 수 있습니다 (MVP!)

---

## Phase 4: User Story 2 - 작업 세션 컨텍스트 관리 (우선순위: P1)

**목표**: 새 작업 시작 전 마지막 2개 작업 로그를 읽어 컨텍스트 유지

**독립 테스트**: 세션 1에서 작업 A 수행, 세션 2에서 작업 B 수행 시 CCW가 작업 A의 컨텍스트를 참조하는지 검증

**브랜치 옵션**: `001-telegram-claude-worker-us2` (US1과 병렬 개발 가능)

### 4.1 컨텍스트 로딩 구현

- [ ] T038 [P] [US2] src/tasks/context.py 생성 (TaskContext 클래스)
- [ ] T039 [US2] src/tasks/context.py에 load_recent_logs 메서드 구현 (최신 2개 로그 파일 읽기)
- [ ] T040 [US2] src/tasks/context.py에 토큰 제한 로직 추가 (로그당 2000 토큰)

### 4.2 에이전트 통합

- [ ] T041 [US2] src/agents/coding_agent.py의 execute 메서드에 컨텍스트 로드 통합
- [ ] T042 [US2] src/tasks/executor.py에서 작업 시작 시 컨텍스트 로드 호출

**Checkpoint**: US2 완료 - 멀티 세션 프로젝트에서 컨텍스트가 유지됩니다

---

## Phase 5: User Story 3 - 작업 로그 문서화 (우선순위: P1)

**목표**: 작업 완료 후 마크다운 작업 로그 자동 생성 (시간 기반)

**독립 테스트**: 단일 작업 완료 후 .ccw/logs/에 시간 기반 마크다운 로그 파일이 생성되는지 검증

**브랜치 옵션**: `001-telegram-claude-worker-us3` (US1, US2와 병렬 개발 가능)

### 5.1 로거 에이전트 구현 (Haiku 4 - 비용 최적화)

- [ ] T051 [P] [US3] src/agents/logger/executor.py 생성 (LoggerAgent 클래스)
- [ ] T052 [US3] src/agents/logger/executor.py에 execute 메서드 구현 (시간 기반 로그 생성)
- [ ] T053 [US3] src/agents/logger/prompts.py 생성 (간결한 로그 작성 프롬프트 정의)
- [ ] T054 [US3] src/agents/logger/executor.py에 작업 요약 및 결정사항 추출 로직 추가

### 5.2 로그 도구 구현

- [ ] T055 [P] [US3] src/tools/logging/writer.py 생성 (write_log 함수: 시간 기반 파일명, 마크다운 템플릿)
- [ ] T056 [P] [US3] src/tools/logging/reader.py 생성 (read_recent_logs 함수: 최신 N개 읽기, 토큰 제한)
- [ ] T057 [P] [US3] src/tools/logging/parser.py 생성 (parse_log 함수: 로그에서 주요 정보 추출)

### 5.3 로그 생성 통합

- [ ] T058 [US3] src/tasks/executor.py에서 작업 완료 시 LoggerAgent 호출 추가
- [ ] T059 [US3] src/models/log.py에 시간 기반 로그 파일 로드 메서드 구현 (TaskLog.load_recent)

**Checkpoint**: US3 완료 - 모든 작업이 자동으로 문서화됩니다

---

## Phase 6: User Story 4 - 버전 관리 통합 (우선순위: P2)

**목표**: 랜디의 명시적 명령으로 커밋 및 GitHub MR 생성

**독립 테스트**: 작업 완료 후 /commit 명령으로 커밋, /mr 명령으로 GitHub PR 생성 검증

**브랜치 옵션**: `001-telegram-claude-worker-us4`

**의존성**: US3 (로거 에이전트)가 완료되어야 커밋 메시지 생성 가능

### 6.1 GitHub 도구 구현

- [ ] T060 [P] [US4] src/tools/github/client.py 생성 (GitHubClient 클래스: PyGithub 래핑)
- [ ] T061 [P] [US4] src/tools/github/commit.py 생성 (create_commit 함수: GitPython 사용)
- [ ] T062 [P] [US4] src/tools/github/pr.py 생성 (create_pull_request 함수: PyGithub 사용)
- [ ] T063 [P] [US4] src/tools/github/deployment.py 생성 (monitor_deployment 함수: Polling 방식)

### 6.2 텔레그램 명령어 핸들러

- [ ] T064 [P] [US4] src/telegram/handlers.py에 diff_command 핸들러 구현 (/diff 명령)
- [ ] T065 [P] [US4] src/telegram/handlers.py에 commit_command 핸들러 구현 (/commit 명령)
- [ ] T066 [P] [US4] src/telegram/handlers.py에 branch_command 핸들러 구현 (/branch 명령)
- [ ] T067 [P] [US4] src/telegram/handlers.py에 mr_command 핸들러 구현 (/mr 명령)

### 6.3 메인 에이전트 GitHub 도구 통합

- [ ] T068 [US4] src/agents/main/executor.py에 GitHub 도구 통합 (commit, pr, deployment)
- [ ] T069 [US4] src/agents/main/executor.py에 커밋 메시지 생성 로직 추가 (로거 에이전트 사용)

### 6.4 배포 모니터링 및 알림

- [ ] T070 [US4] src/telegram/handlers.py에 배포 알림 로직 추가 (성공/실패)
- [ ] T071 [US4] src/telegram/bot.py에 /diff, /commit, /branch, /mr 핸들러 등록

**Checkpoint**: US4 완료 - 텔레그램으로 Git 작업을 수행하고 GitHub MR을 생성할 수 있습니다

---

## Phase 7: User Story 5 - 안전한 원격 서버 명령 실행 (우선순위: P3)

**목표**: 텔레그램으로 안전한 서버 명령 실행, 파괴적 명령 차단

**독립 테스트**: /exec ls 명령은 성공, /exec rm 명령은 차단되는지 검증

**브랜치 옵션**: `001-telegram-claude-worker-us5` (언제든지 독립적으로 개발 가능)

### 7.1 메인 에이전트 Bash 도구 통합

- [ ] T072 [US5] src/agents/main/executor.py에 Bash 도구 통합 (bash, bash_output, validator)
- [ ] T073 [US5] src/agents/main/prompts.py에 안전한 명령 실행 가이드라인 추가

### 7.2 텔레그램 명령어 핸들러

- [ ] T074 [US5] src/telegram/handlers.py에 exec_command 핸들러 구현 (/exec 명령)
- [ ] T075 [US5] src/telegram/bot.py에 /exec 핸들러 등록

**Checkpoint**: US5 완료 - 텔레그램으로 안전하게 서버 명령을 실행할 수 있습니다

---

## Phase 8: 추가 기능

**목적**: 오류 처리 및 부가 기능 구현

### 8.1 오류 처리 통합 (메인 에이전트 사용)

- [ ] T076 src/tasks/executor.py에 전역 예외 핸들러 추가 (메인 에이전트가 오류 분석)
- [ ] T077 src/telegram/handlers.py에 에러 핸들러 추가 (텔레그램 오류 알림)
- [ ] T078 src/telegram/bot.py에 에러 핸들러 등록

### 8.2 로그 조회 기능

- [ ] T079 [P] src/telegram/handlers.py에 logs_command 핸들러 구현 (/logs 명령)
- [ ] T080 src/telegram/bot.py에 /logs 핸들러 등록

---

## Phase 9: 테스트 (선택적 - 명세서에서 100% 커버리지 목표)

**목적**: 단위 테스트, 통합 테스트, 계약 테스트 작성

### 9.1 단위 테스트 - 에이전트

- [ ] T081 [P] tests/unit/agents/test_main_agent.py 생성 (메인 에이전트 테스트)
- [ ] T082 [P] tests/unit/agents/test_logger_agent.py 생성 (로거 에이전트 테스트)

### 9.2 단위 테스트 - 도구

- [ ] T083 [P] tests/unit/tools/test_coding_file_io.py 생성 (파일 I/O 도구 테스트)
- [ ] T084 [P] tests/unit/tools/test_coding_search.py 생성 (검색 도구 테스트)
- [ ] T085 [P] tests/unit/tools/test_coding_editor.py 생성 (편집 도구 테스트)
- [ ] T086 [P] tests/unit/tools/test_github_client.py 생성 (GitHub 클라이언트 테스트)
- [ ] T087 [P] tests/unit/tools/test_log_writer.py 생성 (로그 작성 도구 테스트)
- [ ] T088 [P] tests/unit/tools/test_bash_validator.py 생성 (Bash 검증 도구 테스트)

### 9.3 단위 테스트 - 기타

- [ ] T089 [P] tests/unit/telegram/test_auth.py 생성 (인증 테스트)
- [ ] T090 [P] tests/unit/telegram/test_handlers.py 생성 (핸들러 테스트)
- [ ] T091 [P] tests/unit/tasks/test_executor.py 생성 (작업 실행 테스트)
- [ ] T092 [P] tests/unit/tasks/test_context.py 생성 (컨텍스트 테스트)
- [ ] T093 [P] tests/unit/models/test_task.py 생성 (Task 모델 테스트)
- [ ] T094 [P] tests/unit/models/test_log.py 생성 (TaskLog 모델 테스트)

### 9.4 통합 테스트

- [ ] T095 [P] tests/integration/test_telegram_channel_integration.py 생성 (텔레그램 채널 통합)
- [ ] T096 [P] tests/integration/test_main_agent_integration.py 생성 (메인 에이전트 통합)
- [ ] T097 [P] tests/integration/test_logger_agent_integration.py 생성 (로거 에이전트 통합)
- [ ] T098 [P] tests/integration/test_coding_tool_integration.py 생성 (코딩 도구 통합)
- [ ] T099 [P] tests/integration/test_github_tool_integration.py 생성 (GitHub 도구 통합)

### 9.5 계약 테스트

- [ ] T100 [P] tests/contract/test_telegram_api_contract.py 생성 (Telegram API 계약 테스트)
- [ ] T101 [P] tests/contract/test_claude_api_contract.py 생성 (Claude API 계약 테스트)
- [ ] T102 [P] tests/contract/test_github_api_contract.py 생성 (GitHub API 계약 테스트)

---

## Phase 10: Polish & Cross-Cutting Concerns

**목적**: 마무리 작업 및 배포 준비

- [ ] T103 [P] 프로젝트 루트에 pytest.ini 생성 (pytest 설정)
- [ ] T104 [P] 프로젝트 루트에 ruff.toml 생성 (린팅 설정)
- [ ] T105 [P] .github/workflows/deploy.yml 생성 (GitHub Actions 배포 워크플로우)
- [ ] T106 [P] .github/workflows/test.yml 생성 (GitHub Actions 테스트 워크플로우)
- [ ] T107 코드 정리 및 리팩토링 (중복 제거, 명명 규칙 통일)
- [ ] T108 [P] 모든 모듈에 docstring 추가 (한글)
- [ ] T109 [P] README.md 업데이트 (사용 방법, 설치 가이드)
- [ ] T110 quickstart.md 검증 (단계별 실행 테스트)
- [ ] T111 전체 테스트 실행 및 커버리지 확인 (pytest --cov=src)
- [ ] T112 보안 검토 (API 키 노출, 명령어 인젝션 체크)
- [ ] T113 성능 최적화 (불필요한 API 호출 제거, 캐싱 추가)

---

## 의존성 및 실행 순서

### Phase 의존성

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← 모든 US의 blocking prerequisite
    ↓
    ├─→ Phase 3 (US1: 원격 작업 실행) 🎯 MVP
    ├─→ Phase 4 (US2: 컨텍스트 관리) ← US1과 병렬 가능
    ├─→ Phase 5 (US3: 작업 로그) ← US1, US2와 병렬 가능
    ├─→ Phase 7 (US5: 서버 명령) ← 완전 독립적
    │
    └─→ Phase 5 (US3) 완료 후
         ↓
        Phase 6 (US4: Git 통합) ← US3의 LogAgent 필요

    모든 US 완료 후
    ↓
Phase 8 (추가 기능)
    ↓
Phase 9 (테스트) ← 언제든지 작성 가능
    ↓
Phase 10 (Polish)
```

### 사용자 스토리 의존성

- **US1 (P1)**: Phase 2 완료 후 시작 가능 - 다른 스토리 의존성 없음
- **US2 (P1)**: Phase 2 완료 후 시작 가능 - US1과 병렬 가능
- **US3 (P1)**: Phase 2 완료 후 시작 가능 - US1, US2와 병렬 가능
- **US4 (P2)**: US3 완료 필요 (LogAgent가 커밋 메시지 생성에 필요)
- **US5 (P3)**: Phase 2 완료 후 언제든지 시작 가능 - 완전 독립적

### 각 Phase 내 작업 순서

**Phase 2 (Foundational)** - 순차적 그룹:
1. T010-T011 (BaseAgent) 먼저
2. T012-T015 (Tools) 병렬 가능
3. T016-T019 (Telegram) 병렬 가능
4. T020-T023 (Models) 병렬 가능
5. T024-T025 (Tasks) 는 T010 이후
6. T026 (Main) 마지막

**Phase 3 (US1)** - 순차적:
1. T027-T029 (CodingAgent)
2. T030-T032 (Handlers)
3. T033-T035 (Executor)
4. T036-T037 (통합)

**Phase 4 (US2)** - 순차적:
1. T038-T040 (Context)
2. T041-T042 (통합)

**Phase 5 (US3)** - 순차적:
1. T043-T046 (LogAgent)
2. T047-T048 (통합)
3. T049-T050 (로그 파일 관리)

**Phase 6 (US4)** - 병렬 그룹:
1. T051-T055 (Git 모듈) 병렬 가능
2. T056-T059 (Handlers) 병렬 가능
3. T060-T061 (커밋 메시지)
4. T062-T063 (GitHub Actions)
5. T064 (통합)

**Phase 7 (US5)** - 병렬 그룹:
1. T065-T067, T068-T070 병렬 가능
2. T071-T073 (ServerAgent)
3. T074-T075 (통합)

### 병렬 실행 기회

**Setup Phase (Phase 1)**: T003, T004, T007, T008, T009 모두 병렬 실행 가능

**Foundational Phase (Phase 2)**:
- 그룹 1: T012, T013, T014, T015 (Tools) 병렬
- 그룹 2: T016, T017, T018, T019 (Telegram) 병렬
- 그룹 3: T020, T021, T022, T023 (Models) 병렬

**User Story Phase (Phase 2 완료 후)**:
- US1, US2, US3, US5는 완전히 병렬로 개발 가능
- 4명의 개발자가 있다면 각각 다른 스토리 담당 가능

**Test Phase (Phase 9)**: T084-T104 모두 병렬 실행 가능

**Polish Phase (Phase 10)**: T105-T108, T110-T111 병렬 가능

---

## 병렬 실행 예시

### 예시 1: Setup Phase 병렬 실행

```bash
# 동시에 5개 작업 시작
Task: "프로젝트 루트에 .gitignore 파일 생성"
Task: "프로젝트 루트에 README.md 생성"
Task: ".ccw/logs/ 디렉토리 생성"
Task: "src/utils/config.py 생성"
Task: "src/utils/errors.py 생성"
```

### 예시 2: Foundational Phase - Tools 병렬 실행

```bash
# Tools 그룹 병렬 실행
Task: "src/tools/file_tools.py 생성 (Read, Write, Edit)"
Task: "src/tools/search_tools.py 생성 (Glob, Grep)"
Task: "src/tools/exec_tools.py 생성 (Bash, BashOutput)"
```

### 예시 3: User Stories 병렬 개발 (4명 팀)

```bash
# Phase 2 완료 후
Developer 1 → Branch: 001-telegram-claude-worker-us1 (US1: 원격 작업 실행) 🎯
Developer 2 → Branch: 001-telegram-claude-worker-us2 (US2: 컨텍스트 관리)
Developer 3 → Branch: 001-telegram-claude-worker-us3 (US3: 작업 로그)
Developer 4 → Branch: 001-telegram-claude-worker-us5 (US5: 서버 명령)

# 각자 독립적으로 작업 후 메인 브랜치에 순차적으로 머지
```

### 예시 4: US4 Git 모듈 병렬 실행

```bash
Task: "src/git/manager.py 생성 (GitManager)"
Task: "src/git/diff.py 생성 (diff 분석)"
```

### 예시 5: 테스트 병렬 실행

```bash
# 모든 단위 테스트 동시 작성
Task: "tests/unit/test_agents/test_coding_agent.py"
Task: "tests/unit/test_agents/test_log_agent.py"
Task: "tests/unit/test_agents/test_server_agent.py"
Task: "tests/unit/test_tools/test_file_tools.py"
# ... (총 15개 테스트 파일 병렬 작성 가능)
```

---

## 구현 전략

### MVP First (US1만 구현)

1. **Phase 1 완료**: Setup (T001-T009)
2. **Phase 2 완료**: Foundational (T010-T026) ⚠️ CRITICAL
3. **Phase 3 완료**: US1 (T027-T037)
4. **검증 및 테스트**: 텔레그램으로 "/task" 명령 실행
5. **배포/데모**: 기본 기능 시연

**MVP 범위**: 총 37개 작업 (T001-T037)

### 점진적 전달

1. **Foundation 구축** → Phase 1 + Phase 2 완료
2. **US1 추가** → 텔레그램으로 작업 실행 (MVP!) → 배포/데모
3. **US2 추가** → 컨텍스트 유지 → 배포/데모
4. **US3 추가** → 자동 문서화 → 배포/데모
5. **US4 추가** → Git 통합 → 배포/데모
6. **US5 추가** → 서버 명령 실행 → 배포/데모
7. **Polish** → 테스트 및 최적화 → 프로덕션 배포

### 병렬 팀 전략 (4명 개발자)

**Week 1**: 모두 함께 Foundation 구축
- Phase 1 (Setup): 1일
- Phase 2 (Foundational): 2-3일
- **Checkpoint**: 기반 인프라 완성

**Week 2**: 병렬 개발 시작
- Developer A → US1 (원격 작업 실행) 🎯 MVP
- Developer B → US2 (컨텍스트 관리)
- Developer C → US3 (작업 로그)
- Developer D → US5 (서버 명령)

**Week 3**: 통합 및 추가 기능
- US1 → 메인 머지 → MVP 배포
- US2, US3 → 메인 머지
- US4 (Git 통합) 시작 (US3 완료 필요)
- Developer D → US5 완료

**Week 4**: 마무리
- US4, US5 → 메인 머지
- Phase 8 (추가 기능)
- Phase 9 (테스트)
- Phase 10 (Polish)
- 프로덕션 배포

---

## 작업 완료 기준

각 작업은 다음 기준을 충족해야 완료로 간주됩니다:

1. **코드 작성**: 명시된 파일에 기능 구현
2. **린팅 통과**: `ruff check .` 통과
3. **타입 체크**: Python 3.13 호환성 확인
4. **수동 테스트**: 해당 기능 동작 확인
5. **문서화**: 함수/클래스에 docstring 추가 (한글)
6. **커밋**: 작업 단위로 커밋 (선택적)

**Phase 완료 기준**:
- Phase의 모든 작업 완료
- Checkpoint 검증 통과
- 다음 Phase로 진행 가능

---

## 리스크 및 대응

| 리스크 | 영향 | 대응 방안 |
|--------|------|-----------|
| Claude API 레이트 리미트 | 높음 | Phase 2에서 재시도 로직 구현, 토큰 사용량 모니터링 |
| 텔레그램 연결 불안정 | 중간 | US1에서 연결 끊김 감지 및 롤백 구현 |
| 병렬 개발 시 충돌 | 중간 | 브랜치 전략 준수, 정기적 메인 머지 |
| US4가 US3 대기 | 낮음 | US3 우선 완료, US4는 나중에 시작 |
| 30분 타임아웃 부족 | 낮음 | 환경 변수로 조정 가능하도록 설계 |

---

## 요약

**총 작업 수**: 112개 작업 (T001-T113, T017 제외)

**Phase별 작업 수**:
- Phase 1 (Setup): 9개
- Phase 2 (Foundational): 21개 ⚠️ BLOCKING (코딩 도구 4개 추가, 상수 관리 추가)
- Phase 3 (US1 - P1): 12개 🎯 MVP (메인 에이전트 Sonnet 4 + 코딩 도구 통합)
- Phase 4 (US2 - P1): 5개
- Phase 5 (US3 - P1): 9개 (로거 에이전트 Haiku 4 + 로그 도구 3개)
- Phase 6 (US4 - P2): 12개 (GitHub 도구 4개 + 메인 에이전트 통합)
- Phase 7 (US5 - P3): 4개 (메인 에이전트가 Bash 도구 사용)
- Phase 8 (추가 기능): 5개 (메인 에이전트 기반 오류 처리)
- Phase 9 (테스트): 22개 (2개 에이전트 + 도구별 테스트)
- Phase 10 (Polish): 11개

**아키텍처 변경사항** (2025-11-15):
- **에이전트 최적화**: 4개 → **2개** (메인 Sonnet + 로거 Haiku)
  - 메인 에이전트: 모든 핵심 작업 수행 (코딩, GitHub, Bash, 오류 분석)
  - 로거 에이전트: 작업 로그 생성 전용 (비용 절감)
- **도구 세분화**: 코딩 도구를 4개로 분리 (file_io, search, editor, navigator)
- **로그 구조 변경**: 이슈 기반 → 시간 기반 (`YYYY-MM-DD-HHmmss.md`)
- **상수 관리**: constants.py 추가 (MAIN_AGENT_MODEL, LOGGER_AGENT_MODEL 등)

**병렬 실행 기회**:
- Setup: 5개 작업 병렬 가능
- Foundational: 코딩 도구 4개, Bash 도구 2개, 로그 도구 3개 병렬 가능
- User Stories: US1, US2, US3, US5 완전 병렬 가능
- Tests: 22개 테스트 모두 병렬 가능
- Polish: 4개 작업 병렬 가능

**독립 테스트 기준**:
- US1: 텔레그램으로 작업 지시 → 메인 에이전트 완료 응답
- US2: 이전 작업 컨텍스트 참조 확인
- US3: 시간 기반 작업 로그 파일 생성 확인 (로거 에이전트)
- US4: 커밋 및 GitHub PR 생성 확인
- US5: 안전한 명령 실행, 위험 명령 차단 확인

**MVP 범위**: Phase 1 + Phase 2 + Phase 3 (총 42개 작업, US1만 포함)

**권장 순서** (1명 개발 시):
1. Phase 1 → Phase 2 (Foundation + 코딩/Bash 도구)
2. Phase 3 (US1) → MVP 배포 🎯 (메인 에이전트 + 코딩 도구 통합)
3. Phase 5 (US3) → 로거 에이전트 + 로그 도구 추가
4. Phase 4 (US2) → 컨텍스트 관리
5. Phase 6 (US4) → GitHub 도구 + 메인 에이전트 통합
6. Phase 7 (US5) → 메인 에이전트 Bash 통합
7. Phase 8 + Phase 9 + Phase 10

**형식 검증**: ✅ 모든 작업이 체크박스 형식 준수 (`- [ ] [ID] [P?] [Story?] 설명`)

---

## 다음 단계

tasks.md 생성이 완료되었습니다! 이제 다음을 진행하세요:

1. ✅ **이 파일 검토**: 작업 분해가 적절한지 확인
2. 📋 **MVP 시작**: Phase 1 (Setup) 부터 시작
3. 🔄 **병렬 개발 계획**: 팀이 있다면 Phase 2 완료 후 US 분담
4. 🎯 **첫 목표**: Phase 3 (US1) 완료로 MVP 달성

**브랜치 생성 예시**:
```bash
# 현재 브랜치 확인
git branch

# US별 브랜치 생성 (Phase 2 완료 후)
git checkout -b 001-telegram-claude-worker-us1
git checkout -b 001-telegram-claude-worker-us2
git checkout -b 001-telegram-claude-worker-us3
```

**작업 시작**:
```bash
# 의존성 설치
uv sync

# 첫 작업 시작
# T001: pyproject.toml 생성
```

화이팅! 🚀
