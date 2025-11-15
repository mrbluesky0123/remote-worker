# 데이터 모델: 텔레그램 기반 원격 Claude 워커 시스템

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-08
**상태**: Phase 1 설계

## 개요

이 문서는 CCW(Claude Code Worker) 시스템의 주요 엔티티, 데이터 구조, 관계, 상태 전이를 정의합니다.

## 핵심 엔티티

### 1. Task (작업)

**설명**: 사용자가 텔레그램을 통해 요청한 개발 작업

**필드**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| id | str | ✓ | UUID 형식의 고유 식별자 |
| user_id | int | ✓ | 텔레그램 사용자 ID (화이트리스트 검증) |
| description | str | ✓ | 작업 내용 설명 |
| status | TaskStatus | ✓ | 작업 상태 (pending, running, completed, failed, timeout, interrupted) |
| created_at | datetime | ✓ | 작업 생성 시각 |
| started_at | datetime | - | 작업 시작 시각 |
| completed_at | datetime | - | 작업 완료 시각 |
| timeout_at | datetime | ✓ | 타임아웃 시각 (생성 시각 + 30분) |
| agent_type | AgentType | ✓ | 할당된 에이전트 타입 |
| context | dict | - | 작업 컨텍스트 (이전 로그, 환경 정보) |
| result | str | - | 작업 결과 메시지 |
| error | str | - | 오류 메시지 (실패 시) |

**상태 전이**:
```
pending → running → completed
               ↘ failed
               ↘ timeout
               ↘ interrupted (연결 끊김 시)
```

**검증 규칙**:
- `description`은 비어있을 수 없음
- `user_id`는 화이트리스트에 포함되어야 함
- `timeout_at`은 `created_at` + 30분
- `running` 상태인 작업은 시스템에 최대 1개만 존재

**Python 모델**:
```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INTERRUPTED = "interrupted"

class AgentType(Enum):
    CODING = "coding"
    LOG_WRITER = "log_writer"
    SERVER_COMMAND = "server_command"
    ERROR_ANALYZER = "error_analyzer"

@dataclass
class Task:
    user_id: int
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: datetime = field(init=False)
    agent_type: AgentType = AgentType.CODING
    context: dict = field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        self.timeout_at = self.created_at + timedelta(minutes=30)

    def start(self):
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, result: str):
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def fail(self, error: str):
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error

    def is_timed_out(self) -> bool:
        return datetime.now() >= self.timeout_at
```

### 2. TaskLog (작업 로그)

**설명**: 작업 완료 후 생성되는 마크다운 문서

**필드**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| id | str | ✓ | UUID 형식의 고유 식별자 |
| issue_id | str | ✓ | 이슈 식별자 (예: "feature-auth", "bug-123") |
| file_path | Path | ✓ | 로그 파일 경로 (.ccw/logs/{issue_id}.md) |
| task_id | str | ✓ | 연관된 작업 ID |
| created_at | datetime | ✓ | 최초 생성 시각 |
| updated_at | datetime | ✓ | 마지막 업데이트 시각 |
| summary | str | ✓ | 작업 요약 |
| decisions | list[str] | - | 내린 결정사항 목록 |
| issues | list[str] | - | 발생한 이슈 목록 |
| discussions | list[str] | - | 사용자와의 논의 내용 |
| token_count | int | - | 로그의 예상 토큰 수 (2000 토큰 목표) |

**검증 규칙**:
- `file_path`는 `.ccw/logs/` 디렉토리 내에 있어야 함
- `token_count`는 2000을 초과하지 않는 것을 권장
- 동일한 `issue_id`를 가진 로그는 하나만 존재 (업데이트)

**마크다운 구조**:
```markdown
# {issue_id}

**작업 ID**: {task_id}
**최초 생성**: {created_at}
**마지막 업데이트**: {updated_at}

## 요약

{summary}

## 수행한 작업

- 작업 1
- 작업 2
- ...

## 내린 결정

- 결정 1: 근거
- 결정 2: 근거
- ...

## 발생한 이슈

- 이슈 1: 해결 방법
- 이슈 2: 해결 방법
- ...

## 논의 내용

- Q: 질문 1
  A: 답변 1
- Q: 질문 2
  A: 답변 2
```

**Python 모델**:
```python
from pathlib import Path

@dataclass
class TaskLog:
    issue_id: str
    task_id: str
    summary: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    decisions: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    discussions: list[str] = field(default_factory=list)
    token_count: int = 0

    @property
    def file_path(self) -> Path:
        return Path(f".ccw/logs/{self.issue_id}.md")

    def to_markdown(self) -> str:
        lines = [
            f"# {self.issue_id}",
            "",
            f"**작업 ID**: {self.task_id}",
            f"**최초 생성**: {self.created_at.isoformat()}",
            f"**마지막 업데이트**: {self.updated_at.isoformat()}",
            "",
            "## 요약",
            "",
            self.summary,
            ""
        ]

        if self.decisions:
            lines.extend(["## 내린 결정", ""])
            lines.extend([f"- {d}" for d in self.decisions])
            lines.append("")

        if self.issues:
            lines.extend(["## 발생한 이슈", ""])
            lines.extend([f"- {i}" for i in self.issues])
            lines.append("")

        if self.discussions:
            lines.extend(["## 논의 내용", ""])
            lines.extend([f"- {d}" for d in self.discussions])
            lines.append("")

        return "\n".join(lines)

    def save(self):
        self.updated_at = datetime.now()
        content = self.to_markdown()
        self.token_count = len(content) // 4  # 대략 추정
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def load(issue_id: str) -> Optional['TaskLog']:
        file_path = Path(f".ccw/logs/{issue_id}.md")
        if not file_path.exists():
            return None

        # 마크다운 파싱 로직 (간략화)
        content = file_path.read_text(encoding="utf-8")
        # TODO: 실제 파싱 구현
        return TaskLog(issue_id=issue_id, task_id="", summary=content)
```

### 3. AgentSession (에이전트 세션)

**설명**: 단일 작업을 처리하는 에이전트의 실행 컨텍스트

**필드**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| id | str | ✓ | UUID 형식의 고유 식별자 |
| task_id | str | ✓ | 처리 중인 작업 ID |
| agent_type | AgentType | ✓ | 에이전트 타입 |
| context_logs | list[str] | - | 로드된 컨텍스트 로그 (최대 2개) |
| started_at | datetime | ✓ | 세션 시작 시각 |
| ended_at | datetime | - | 세션 종료 시각 |
| messages | list[dict] | ✓ | Claude API 메시지 히스토리 |
| token_usage | dict | - | 토큰 사용량 (input, output) |

**관계**:
- AgentSession 1:1 Task
- AgentSession N:1 AgentType

**Python 모델**:
```python
@dataclass
class AgentSession:
    task_id: str
    agent_type: AgentType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_logs: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    messages: list[dict] = field(default_factory=list)
    token_usage: dict = field(default_factory=lambda: {"input": 0, "output": 0})

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def end(self):
        self.ended_at = datetime.now()
```

### 4. ServerCommand (서버 명령어)

**설명**: 텔레그램을 통해 요청된 서버 명령어 실행

**필드**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| id | str | ✓ | UUID 형식의 고유 식별자 |
| command | str | ✓ | 실행할 명령어 |
| user_id | int | ✓ | 요청한 사용자 ID |
| status | CommandStatus | ✓ | 명령어 상태 (pending, running, completed, blocked) |
| is_safe | bool | ✓ | 안전성 검증 결과 |
| block_reason | str | - | 차단 사유 (blocked 시) |
| stdout | str | - | 표준 출력 |
| stderr | str | - | 표준 에러 |
| exit_code | int | - | 종료 코드 |
| executed_at | datetime | - | 실행 시각 |

**상태 전이**:
```
pending → (검증) → running → completed
                 ↘ blocked
```

**검증 규칙**:
- 파괴적 명령 차단: `rm`, `rmdir`, `mkfs`, `dd`
- 대화형 명령 차단: `vi`, `vim`, `nano`, `emacs`
- 시스템 경로 쓰기 차단: `/etc/`, `/sys/`, `/proc/`, `/boot/`

**Python 모델**:
```python
class CommandStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class ServerCommand:
    command: str
    user_id: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: CommandStatus = CommandStatus.PENDING
    is_safe: bool = False
    block_reason: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    executed_at: Optional[datetime] = None

    def validate(self) -> bool:
        from src.commands.validator import CommandValidator
        self.is_safe, reason = CommandValidator.is_safe(self.command)
        if not self.is_safe:
            self.status = CommandStatus.BLOCKED
            self.block_reason = reason
        return self.is_safe
```

### 5. GitOperation (Git 작업)

**설명**: Git 커밋, 브랜치 생성, MR 생성 등의 버전 관리 작업

**필드**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| id | str | ✓ | UUID 형식의 고유 식별자 |
| operation_type | GitOperationType | ✓ | 작업 타입 (commit, branch, merge_request, diff) |
| user_id | int | ✓ | 요청한 사용자 ID |
| params | dict | ✓ | 작업 파라미터 (메시지, 브랜치명 등) |
| status | OperationStatus | ✓ | 작업 상태 |
| result | dict | - | 작업 결과 (커밋 SHA, MR URL 등) |
| error | str | - | 오류 메시지 |
| executed_at | datetime | - | 실행 시각 |

**작업 타입별 파라미터**:

**commit**:
```python
{
    "message": str,  # 커밋 메시지
    "files": list[str]  # 커밋할 파일 목록 (생략 시 전체)
}
```

**branch**:
```python
{
    "base_branch": str,  # 기준 브랜치
    "new_branch": str    # 새 브랜치명
}
```

**merge_request**:
```python
{
    "source_branch": str,  # 소스 브랜치
    "target_branch": str,  # 타겟 브랜치 (기본: main)
    "title": str,          # MR 제목
    "description": str     # MR 설명
}
```

**diff**:
```python
{
    "from_ref": str,  # 비교 시작 (기본: HEAD~1)
    "to_ref": str     # 비교 끝 (기본: HEAD)
}
```

**Python 모델**:
```python
class GitOperationType(Enum):
    COMMIT = "commit"
    BRANCH = "branch"
    MERGE_REQUEST = "merge_request"
    DIFF = "diff"

class OperationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class GitOperation:
    operation_type: GitOperationType
    user_id: int
    params: dict
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: OperationStatus = OperationStatus.PENDING
    result: dict = field(default_factory=dict)
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
```

## 엔티티 관계도

```
┌─────────────┐
│    User     │ (텔레그램 사용자)
│  (int ID)   │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────────┐      1:1      ┌────────────────┐
│      Task       │◄───────────────┤ AgentSession   │
│   (작업 지시)    │                │ (에이전트 세션)  │
└────────┬────────┘                └────────────────┘
         │ 1:1
         │
┌────────▼────────┐
│    TaskLog      │
│  (작업 로그)     │
└─────────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────────┐
│ ServerCommand   │
│ (서버 명령어)    │
└─────────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────────┐
│ GitOperation    │
│  (Git 작업)     │
└─────────────────┘
```

## 저장소 구조

### 파일 기반 저장

**작업 로그**:
- 위치: `.ccw/logs/{issue_id}.md`
- 형식: 마크다운
- Git 추적: ✓

**환경 변수**:
- 위치: `.env`
- Git 추적: ✗ (`.gitignore`에 추가)
- 예시: `.env.example`

**애플리케이션 로그**:
- 위치: `.ccw/app.log`
- 형식: 텍스트 (로그 레벨, 타임스탬프)
- Git 추적: ✗

### 메모리 기반 저장 (런타임)

**현재 실행 중인 작업**:
- Task 객체 1개 (전역 상태)
- AgentSession 객체 1개

**명령어 큐**:
- 대기 중인 ServerCommand, GitOperation

## 데이터 플로우

### 1. 작업 실행 플로우

```
[텔레그램 /task]
   ↓
[Task 생성 (status=pending)]
   ↓
[TaskContext.load_recent_logs()] → [마지막 2개 로그 로드]
   ↓
[AgentSession 생성]
   ↓
[Task.start()] → status=running
   ↓
[Agent.execute()] ← [Claude API]
   ↓
[Task.complete(result)] → status=completed
   ↓
[LogAgent.create_log()] → [TaskLog 생성/업데이트]
   ↓
[TaskLog.save()] → [.ccw/logs/{issue_id}.md]
   ↓
[텔레그램 알림: 완료]
```

### 2. Git 커밋 플로우

```
[텔레그램 /diff]
   ↓
[GitOperation(type=diff)] → [git diff 실행]
   ↓
[CodingAgent.generate_commit_message()] ← [Claude API]
   ↓
[텔레그램 알림: 제안된 커밋 메시지]
   ↓
[텔레그램 /commit {message}]
   ↓
[GitOperation(type=commit)] → [git commit 실행]
   ↓
[텔레그램 알림: 커밋 완료 (SHA)]
```

### 3. 서버 명령 실행 플로우

```
[텔레그램 /exec {command}]
   ↓
[ServerCommand 생성]
   ↓
[CommandValidator.is_safe()] → [안전성 검증]
   ↓
[차단?] ─ Yes → [텔레그램 알림: 차단 사유]
   │
   No
   ↓
[subprocess 실행]
   ↓
[stdout, stderr 캡처]
   ↓
[텔레그램 알림: 실행 결과]
```

## 상태 관리

### 전역 상태

**현재 실행 중인 작업** (싱글톤):
```python
class TaskManager:
    _current_task: Optional[Task] = None

    @classmethod
    def get_current_task(cls) -> Optional[Task]:
        return cls._current_task

    @classmethod
    def set_current_task(cls, task: Task):
        if cls._current_task and cls._current_task.status == TaskStatus.RUNNING:
            raise RuntimeError("작업이 이미 진행 중입니다.")
        cls._current_task = task

    @classmethod
    def clear_current_task(cls):
        cls._current_task = None
```

### 세션 상태

**에이전트 세션 컨텍스트**:
- 메시지 히스토리 (Claude API)
- 로드된 로그 (마지막 2개)
- 토큰 사용량

### 영속 상태

**작업 로그** (파일 시스템):
- `.ccw/logs/` 디렉토리
- Git으로 추적
- 이슈별로 그룹화

## 검증 및 제약 조건

### 비즈니스 규칙

1. **단일 작업 실행**: 시스템에 `status=running`인 Task는 최대 1개
2. **타임아웃**: 모든 Task는 30분 후 자동 종료
3. **컨텍스트 로드**: 새 Task 시작 시 마지막 2개 TaskLog만 로드
4. **로그 토큰 제한**: TaskLog는 2000 토큰을 초과하지 않도록 권장
5. **사용자 인증**: 모든 요청은 화이트리스트 검증 필수

### 데이터 무결성

1. **Task.user_id**: 환경 변수 `TELEGRAM_ALLOWED_USERS`에 포함되어야 함
2. **TaskLog.issue_id**: 고유해야 함 (동일 이슈는 업데이트)
3. **ServerCommand.command**: 안전성 검증 통과 필수
4. **GitOperation.params**: 작업 타입별 필수 파라미터 포함

## 마이그레이션 및 버전 관리

### v1.0.0 데이터 스키마

현재 버전에서는 파일 기반 저장만 사용합니다. 향후 데이터베이스 마이그레이션이 필요한 경우:

1. TaskLog는 이미 마크다운 파일로 Git 추적됨 → 마이그레이션 불필요
2. Task, AgentSession은 런타임 메모리만 사용 → 영속화 시 SQLite/PostgreSQL 검토
3. 환경 변수는 `.env` 파일 유지

### 향후 확장 고려사항

1. **멀티 사용자 지원**: User 엔티티 추가, DB 도입
2. **작업 히스토리**: 완료된 Task를 DB에 저장
3. **로그 검색**: TaskLog의 전문 검색 기능
4. **배포 이력**: GitHub Actions 배포 상태 추적

## 다음 단계

Phase 1 데이터 모델 설계가 완료되었습니다. 다음 작업:

1. **contracts/ 생성**: 에이전트 간 인터페이스, API 스키마 정의
2. **quickstart.md 생성**: 개발 환경 설정 가이드
3. **agent context 업데이트**: 기술 스택 정보를 에이전트 컨텍스트에 추가
