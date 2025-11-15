# 연구 문서: 텔레그램 기반 원격 Claude 워커 시스템

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-08
**상태**: Phase 0 완료

## 개요

이 문서는 텔레그램 기반 원격 Claude 워커 시스템 구축에 필요한 기술 스택, 아키텍처 결정, 모범 사례에 대한 연구 결과를 정리합니다.

## 기술 스택 결정

### 1. Python 3.13 선택

**결정**: Python 3.13을 프로젝트 언어로 사용

**근거**:
- Claude Agent SDK가 Python을 공식 지원
- python-telegram-bot 라이브러리의 성숙도와 안정성
- asyncio 기반 비동기 프로그래밍 지원
- PyGitHub를 통한 GitHub API 통합 용이

**검토한 대안**:
- Node.js: Claude SDK의 TypeScript 지원은 있지만, Telegram 봇 라이브러리가 Python보다 덜 성숙
- Go: 성능은 우수하나 Claude SDK 공식 지원 부족

### 2. python-telegram-bot 라이브러리

**결정**: python-telegram-bot v20.x (최신 안정 버전) 사용

**근거**:
- Telegram Bot API의 모든 기능 지원
- asyncio 기반 비동기 처리 완벽 지원
- 풍부한 문서화 및 커뮤니티
- 명령어 핸들러 패턴 내장 (CommandHandler, MessageHandler)

**모범 사례**:
- Application 클래스를 사용한 봇 초기화
- ConversationHandler를 사용한 다단계 대화 관리
- 에러 핸들러를 통한 예외 처리 및 사용자 알림

**검토한 대안**:
- aiogram: 더 현대적이지만 커뮤니티 규모가 작음
- telebot: 동기식 API 위주로 asyncio 지원 제한적

### 3. Claude Agent SDK

**결정**: Anthropic의 공식 Claude Agent SDK 사용

**근거**:
- 공식 지원 및 지속적인 업데이트 보장
- Agent 패턴 내장 (도구 사용, 컨텍스트 관리)
- 스트리밍 응답 지원
- 토큰 사용량 추적 및 비용 관리

**모범 사례**:
- 에이전트별로 독립된 시스템 프롬프트 정의
- 컨텍스트 윈도우 관리 (마지막 2개 로그만 로드)
- 응답 스트리밍을 통한 실시간 피드백
- 타임아웃 및 재시도 로직 구현

**통합 방법**:
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 에이전트별 시스템 프롬프트
CODING_AGENT_PROMPT = "당신은 Python 코딩 전문가입니다..."
LOG_AGENT_PROMPT = "당신은 작업 로그 작성 전문가입니다..."
```

### 4. PyGitHub

**결정**: PyGitHub 라이브러리를 사용한 GitHub API 연동

**근거**:
- GitHub API v3/v4 완전 지원
- 풍부한 문서화
- 커밋, 브랜치, Pull Request 생성 API 제공
- GitHub Actions 상태 조회 가능

**모범 사례**:
- Personal Access Token (PAT) 사용
- API 레이트 리미트 모니터링
- 예외 처리 (인증 실패, 네트워크 오류)

**검토한 대안**:
- GitPython: 로컬 Git 작업에는 유용하나 GitHub API 통합 제한적
- 직접 REST API 호출: 구현 복잡도 증가

### 5. uv 패키지 관리자

**결정**: uv를 사용한 가상환경 및 의존성 관리

**근거**:
- pip, virtualenv보다 빠른 설치 속도
- pyproject.toml 기반 현대적 의존성 관리
- lock 파일을 통한 재현 가능한 빌드
- Python 3.13 완벽 지원

**설정 예시**:
```toml
[project]
name = "ccw"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "python-telegram-bot>=20.0",
    "anthropic>=0.8.0",
    "PyGithub>=2.0",
    "pytest>=7.0",
]
```

## 아키텍처 패턴

### 1. 에이전트 기반 설계

**결정**: 4가지 전문 에이전트를 독립된 모듈로 구현

**에이전트 역할**:

1. **코딩 전문가 (CodingAgent)**
   - 코드 작성, 수정, 리팩토링
   - 버그 수정 및 기능 추가
   - 코드 리뷰 및 제안

2. **작업 로그 작성 전문가 (LogAgent)**
   - 작업 완료 후 마크다운 로그 생성
   - 결정사항, 이슈, 논의 내용 문서화
   - 이슈별 로그 그룹화 및 업데이트

3. **서버 명령어 수행 전문가 (ServerAgent)**
   - 안전한 서버 명령어 실행
   - 명령어 검증 및 차단 (파괴적 명령)
   - 콘솔 출력 포맷팅

4. **Python 오류 분석 전문가 (ErrorAgent)**
   - 예외 스택 트레이스 분석
   - 오류 원인 및 해결 방법 제안
   - 텔레그램으로 오류 보고 포맷팅

**패턴**:
```python
class BaseAgent:
    def __init__(self, client: Anthropic):
        self.client = client
        self.system_prompt = ""

    async def execute(self, task: str, context: dict) -> str:
        # 공통 실행 로직
        pass

class CodingAgent(BaseAgent):
    def __init__(self, client: Anthropic):
        super().__init__(client)
        self.system_prompt = CODING_AGENT_PROMPT
```

### 2. 비동기 처리 아키텍처

**결정**: asyncio 기반 완전 비동기 처리

**근거**:
- 텔레그램 봇과 Claude API 호출이 모두 I/O 바운드
- 동시성 향상 및 응답 시간 단축
- python-telegram-bot v20.x의 asyncio 지원

**패턴**:
```python
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

async def task_command(update: Update, context):
    # 작업 실행을 비동기로 처리
    task_text = ' '.join(context.args)

    # 즉시 확인 메시지
    await update.message.reply_text("작업을 시작합니다...")

    # 에이전트 실행 (비동기)
    result = await execute_agent_task(task_text)

    # 결과 전송
    await update.message.reply_text(f"완료: {result}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("task", task_command))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 작업 컨텍스트 관리

**결정**: 마지막 2개의 작업 로그를 자동으로 로드하여 컨텍스트 제공

**구현 방법**:
1. `.ccw/logs/` 디렉토리에서 최신 로그 2개 파일 읽기
2. 로그 내용을 에이전트 프롬프트에 포함
3. 토큰 제한 (로그당 최대 2000 토큰)

**패턴**:
```python
class TaskContext:
    @staticmethod
    async def load_recent_logs(count: int = 2) -> list[str]:
        log_dir = Path(".ccw/logs")
        log_files = sorted(log_dir.glob("*.md"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)

        logs = []
        for log_file in log_files[:count]:
            content = log_file.read_text()
            # 토큰 제한 체크
            if len(content) > 8000:  # 대략 2000 토큰
                content = content[:8000] + "\n...(생략)"
            logs.append(content)

        return logs
```

### 4. 타임아웃 및 작업 중단 처리

**결정**: asyncio.wait_for를 사용한 30분 타임아웃 구현

**패턴**:
```python
async def execute_task_with_timeout(task_func, timeout_minutes=30):
    try:
        result = await asyncio.wait_for(
            task_func(),
            timeout=timeout_minutes * 60
        )
        return result
    except asyncio.TimeoutError:
        # 타임아웃 처리
        await send_telegram_notification("작업이 30분 타임아웃으로 종료되었습니다.")
        # 부분 결과 로그 저장
        await save_partial_log()
        raise
```

**연결 끊김 감지**:
```python
class ConnectionMonitor:
    async def monitor_telegram_connection(self, on_disconnect):
        while True:
            if not self.is_connected():
                await on_disconnect()
                break
            await asyncio.sleep(5)  # 5초마다 체크

async def handle_disconnect():
    # 진행 중인 작업 중단
    await cancel_running_task()
    # 변경사항 롤백 (Git reset)
    await rollback_changes()
    # 중단 사실 로그 기록
    await log_task_interruption()
```

## 도구 구현 (Tool Implementation)

### 개요

코딩 에이전트가 실제 작업을 수행하려면 파일 읽기/쓰기, 코드 검색, 명령 실행 등의 도구가 필요합니다. Claude Agent SDK의 tool calling 기능을 활용하여 다음 도구들을 구현합니다.

### 도구 카테고리

#### 1. 파일 작업 도구

**Read (파일 읽기)**
- **기능**: 지정된 경로의 파일 내용을 읽어옴
- **입력**: 파일 경로 (절대 또는 상대)
- **출력**: 파일 내용 (텍스트)
- **제약**: 바이너리 파일은 제외, 최대 크기 제한 (예: 1MB)

```python
def read_file(path: str, offset: int = 0, limit: int = None) -> str:
    """
    파일 읽기 도구

    Args:
        path: 파일 경로
        offset: 시작 라인 (기본: 0)
        limit: 읽을 라인 수 (기본: 전체)

    Returns:
        파일 내용 (라인 번호 포함)
    """
    file_path = Path(path)
    if not file_path.exists():
        return f"오류: 파일을 찾을 수 없습니다: {path}"

    lines = file_path.read_text().splitlines()

    if limit:
        lines = lines[offset:offset + limit]
    else:
        lines = lines[offset:]

    # cat -n 형식으로 반환
    return "\n".join(f"{i+1+offset}\t{line}" for i, line in enumerate(lines))
```

**Write (파일 생성)**
- **기능**: 새 파일 생성
- **입력**: 파일 경로, 내용
- **출력**: 성공/실패 메시지
- **안전장치**: 기존 파일이 있으면 경고 후 사용자 확인 필요

```python
def write_file(path: str, content: str, overwrite: bool = False) -> str:
    """
    파일 생성 도구

    Args:
        path: 파일 경로
        content: 파일 내용
        overwrite: 기존 파일 덮어쓰기 허용 (기본: False)

    Returns:
        작업 결과 메시지
    """
    file_path = Path(path)

    if file_path.exists() and not overwrite:
        return f"경고: 파일이 이미 존재합니다. Edit 도구를 사용하거나 overwrite=True로 재시도하세요."

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)

    return f"파일 생성 완료: {path}"
```

**Edit (파일 수정)**
- **기능**: 기존 파일의 특정 문자열을 치환
- **입력**: 파일 경로, 찾을 문자열 (old_string), 바꿀 문자열 (new_string)
- **출력**: 수정된 내용 확인
- **안전장치**: old_string이 고유하지 않으면 오류 (replace_all 옵션 제공)

```python
def edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    """
    파일 수정 도구 (문자열 치환)

    Args:
        path: 파일 경로
        old_string: 찾을 문자열
        new_string: 바꿀 문자열
        replace_all: 모든 발생 치환 (기본: False, 고유해야 함)

    Returns:
        작업 결과 메시지
    """
    file_path = Path(path)
    content = file_path.read_text()

    count = content.count(old_string)

    if count == 0:
        return f"오류: '{old_string}'을 찾을 수 없습니다."

    if count > 1 and not replace_all:
        return f"오류: '{old_string}'이 {count}번 발견되었습니다. replace_all=True를 사용하거나 더 구체적인 문자열을 지정하세요."

    new_content = content.replace(old_string, new_string)
    file_path.write_text(new_content)

    return f"파일 수정 완료: {count}개 치환됨"
```

#### 2. 검색/탐색 도구

**Glob (파일 패턴 매칭)**
- **기능**: 파일 이름 패턴으로 파일 찾기
- **입력**: 패턴 (예: `**/*.py`, `src/**/*.ts`)
- **출력**: 매칭된 파일 경로 목록
- **특징**: 수정 시간 기준 정렬

```python
def glob_files(pattern: str, path: str = ".") -> list[str]:
    """
    파일 패턴 매칭 도구

    Args:
        pattern: Glob 패턴 (예: **/*.py)
        path: 검색 시작 디렉토리 (기본: 현재 디렉토리)

    Returns:
        매칭된 파일 경로 목록 (수정 시간 기준 정렬)
    """
    base_path = Path(path)
    files = sorted(
        base_path.glob(pattern),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    return [str(f) for f in files]
```

**Grep (코드 검색)**
- **기능**: 파일 내용에서 패턴 검색 (ripgrep 기반)
- **입력**: 패턴 (정규표현식), 경로, 옵션 (파일 타입, 출력 모드)
- **출력**: 매칭된 라인 또는 파일 목록
- **특징**: 빠른 속도, 여러 출력 모드 지원

```python
import subprocess

def grep(pattern: str, path: str = ".", output_mode: str = "files_with_matches",
         file_type: str = None, case_insensitive: bool = False) -> str:
    """
    코드 검색 도구 (ripgrep)

    Args:
        pattern: 검색 패턴 (정규표현식)
        path: 검색 경로
        output_mode: 출력 모드 (files_with_matches, content, count)
        file_type: 파일 타입 필터 (py, js, ts 등)
        case_insensitive: 대소문자 무시

    Returns:
        검색 결과
    """
    cmd = ["rg"]

    if output_mode == "files_with_matches":
        cmd.append("-l")
    elif output_mode == "count":
        cmd.append("-c")

    if case_insensitive:
        cmd.append("-i")

    if file_type:
        cmd.extend(["-t", file_type])

    cmd.extend([pattern, path])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

**Task (Explore 에이전트)**
- **기능**: 코드베이스를 체계적으로 탐색하는 전문 에이전트
- **입력**: 탐색 목적 (예: "인증 로직 찾기", "API 엔드포인트 구조 이해")
- **출력**: 탐색 결과 요약
- **특징**: 여러 검색을 조합하여 컨텍스트 파악

```python
async def explore_codebase(query: str, thoroughness: str = "medium") -> str:
    """
    코드베이스 탐색 도구 (Task 에이전트)

    Args:
        query: 탐색 목적 (자연어)
        thoroughness: 탐색 깊이 (quick, medium, very thorough)

    Returns:
        탐색 결과 요약
    """
    # Task 에이전트를 별도로 실행
    # 여러 Glob, Grep 조합하여 체계적 탐색
    pass
```

#### 3. 실행/명령 도구

**Bash (터미널 명령)**
- **기능**: 터미널 명령 실행 (git, npm, docker, pytest 등)
- **입력**: 명령어 문자열
- **출력**: stdout, stderr, exit_code
- **안전장치**: 파괴적 명령 차단, 타임아웃 (기본 2분)

```python
import asyncio

async def bash(command: str, timeout: int = 120, run_in_background: bool = False) -> dict:
    """
    터미널 명령 실행 도구

    Args:
        command: 실행할 명령어
        timeout: 타임아웃 (초, 기본 120)
        run_in_background: 백그라운드 실행 여부

    Returns:
        {
            "stdout": str,
            "stderr": str,
            "exit_code": int,
            "bash_id": str (백그라운드 실행 시)
        }
    """
    # 명령어 검증 (파괴적 명령 차단)
    if not is_safe_command(command):
        return {"error": "차단된 명령어입니다."}

    if run_in_background:
        # 백그라운드 프로세스 시작
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        bash_id = str(id(proc))
        # 프로세스 등록
        BACKGROUND_PROCESSES[bash_id] = proc
        return {"bash_id": bash_id, "status": "running"}

    # 동기 실행
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )
        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "exit_code": proc.returncode
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"error": f"명령어 타임아웃 ({timeout}초)"}
```

**BashOutput (백그라운드 출력 확인)**
- **기능**: 백그라운드 실행 중인 명령의 출력 확인
- **입력**: bash_id (백그라운드 프로세스 ID)
- **출력**: 새로 생성된 출력 (이전에 읽지 않은 부분만)
- **특징**: 로그 스트림 모니터링에 유용

```python
async def bash_output(bash_id: str, filter_regex: str = None) -> dict:
    """
    백그라운드 명령 출력 확인 도구

    Args:
        bash_id: 백그라운드 프로세스 ID
        filter_regex: 출력 필터 (정규표현식)

    Returns:
        {
            "stdout": str,
            "stderr": str,
            "status": str (running, completed, failed)
        }
    """
    if bash_id not in BACKGROUND_PROCESSES:
        return {"error": "프로세스를 찾을 수 없습니다."}

    proc = BACKGROUND_PROCESSES[bash_id]

    # 새 출력 읽기 (넌블로킹)
    # ... 구현

    return {
        "stdout": new_stdout,
        "stderr": new_stderr,
        "status": "running" if proc.returncode is None else "completed"
    }
```

### Claude Agent SDK 통합

```python
from anthropic import Anthropic

# 도구 정의
TOOLS = [
    {
        "name": "read_file",
        "description": "파일 내용 읽기",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "파일 경로"},
                "offset": {"type": "integer", "description": "시작 라인 (선택)"},
                "limit": {"type": "integer", "description": "읽을 라인 수 (선택)"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "새 파일 생성",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "overwrite": {"type": "boolean", "default": False}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "기존 파일 수정 (문자열 치환)",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
                "replace_all": {"type": "boolean", "default": False}
            },
            "required": ["path", "old_string", "new_string"]
        }
    },
    {
        "name": "glob_files",
        "description": "파일 패턴 매칭",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob 패턴 (예: **/*.py)"},
                "path": {"type": "string", "default": "."}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "grep",
        "description": "코드 검색 (ripgrep)",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string", "default": "."},
                "output_mode": {"type": "string", "enum": ["files_with_matches", "content", "count"]},
                "file_type": {"type": "string"},
                "case_insensitive": {"type": "boolean", "default": False}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "bash",
        "description": "터미널 명령 실행",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer", "default": 120},
                "run_in_background": {"type": "boolean", "default": False}
            },
            "required": ["command"]
        }
    },
    {
        "name": "bash_output",
        "description": "백그라운드 명령 출력 확인",
        "input_schema": {
            "type": "object",
            "properties": {
                "bash_id": {"type": "string"},
                "filter_regex": {"type": "string"}
            },
            "required": ["bash_id"]
        }
    }
]

# 도구 실행 함수 매핑
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "glob_files": glob_files,
    "grep": grep,
    "bash": bash,
    "bash_output": bash_output
}

async def execute_with_tools(prompt: str, system_prompt: str) -> str:
    """
    도구를 사용하는 에이전트 실행
    """
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            # 도구 사용
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    # 도구 실행
                    func = TOOL_FUNCTIONS[tool_name]
                    if asyncio.iscoroutinefunction(func):
                        result = await func(**tool_input)
                    else:
                        result = func(**tool_input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            # 결과를 Claude에게 전달
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # 작업 완료
            return response.content[0].text

        else:
            # 기타 종료 사유
            return f"작업 중단: {response.stop_reason}"
```

### 추가 고려사항

#### 보안
- **파일 접근 제한**: 프로젝트 디렉토리 밖의 파일 접근 차단
- **명령어 검증**: 파괴적 명령 차단 (rm, mkfs 등)
- **샌드박스**: 가능하면 컨테이너 환경에서 실행

#### 성능
- **파일 크기 제한**: 대용량 파일은 부분 읽기
- **타임아웃**: 모든 명령에 타임아웃 설정
- **병렬 처리**: 독립적인 도구 호출은 병렬 실행

#### 오류 처리
- **명확한 오류 메시지**: 사용자가 이해할 수 있는 오류 설명
- **재시도 로직**: 일시적 오류는 자동 재시도
- **폴백**: 도구 실패 시 대안 제시

## 보안 및 인증

### 1. 텔레그램 사용자 인증

**결정**: 환경 변수 기반 화이트리스트 검증

**구현**:
```python
import os

ALLOWED_USER_IDS = set(
    int(uid) for uid in os.environ.get("TELEGRAM_ALLOWED_USERS", "").split(",")
)

async def verify_user(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("권한이 없습니다.")
        return False
    return True
```

### 2. 서버 명령어 검증

**결정**: 화이트리스트/블랙리스트 기반 명령어 필터링

**차단 대상**:
- 파괴적 명령: `rm`, `rmdir`, `mkfs`, `dd`, `> /dev/`
- 시스템 쓰기: `/etc/`, `/sys/`, `/proc/` 경로 쓰기
- 대화형 명령: `vi`, `vim`, `nano`, `emacs`, `less`, `more`

**구현**:
```python
class CommandValidator:
    DESTRUCTIVE_COMMANDS = ["rm", "rmdir", "mkfs", "dd", "format"]
    INTERACTIVE_COMMANDS = ["vi", "vim", "nano", "emacs", "less", "more"]
    PROTECTED_PATHS = ["/etc/", "/sys/", "/proc/", "/boot/"]

    @staticmethod
    def is_safe(command: str) -> tuple[bool, str]:
        # 명령어 파싱
        parts = command.split()
        if not parts:
            return False, "빈 명령어"

        cmd = parts[0]

        # 파괴적 명령 체크
        if cmd in CommandValidator.DESTRUCTIVE_COMMANDS:
            return False, f"파괴적 명령어 '{cmd}'는 실행할 수 없습니다."

        # 대화형 명령 체크
        if cmd in CommandValidator.INTERACTIVE_COMMANDS:
            return False, f"대화형 명령어 '{cmd}'는 지원되지 않습니다. 'cat' 사용을 권장합니다."

        # 시스템 경로 쓰기 체크
        for path in CommandValidator.PROTECTED_PATHS:
            if path in command and (">" in command or "tee" in command):
                return False, f"시스템 경로 '{path}'에 쓰기를 시도할 수 없습니다."

        return True, ""
```

## 테스트 전략

### 1. 단위 테스트 (pytest)

**커버리지 목표**: 100%

**테스트 대상**:
- 각 에이전트 모듈 (mocking Claude API)
- 명령어 검증 로직
- Git 작업 관리
- 작업 로그 생성/읽기
- 인증 로직

**예시**:
```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.commands.validator import CommandValidator

def test_destructive_command_blocked():
    is_safe, reason = CommandValidator.is_safe("rm -rf /")
    assert not is_safe
    assert "파괴적" in reason

def test_safe_command_allowed():
    is_safe, reason = CommandValidator.is_safe("ls -la")
    assert is_safe

@pytest.mark.asyncio
async def test_coding_agent_execution():
    mock_client = Mock()
    mock_client.messages.create = AsyncMock(return_value=Mock(
        content=[Mock(text="코드 작성 완료")]
    ))

    agent = CodingAgent(mock_client)
    result = await agent.execute("main.py에 주석 추가", {})

    assert "완료" in result
```

### 2. 통합 테스트

**테스트 대상**:
- 텔레그램 봇 → 에이전트 → 작업 로그 전체 플로우
- Git 커밋 → GitHub MR 생성 플로우
- 텔레그램 명령어 → 서버 실행 플로우

**예시**:
```python
@pytest.mark.asyncio
async def test_task_workflow_integration(telegram_bot, temp_git_repo):
    # /task 명령 전송
    update = create_mock_update("/task main.py에 함수 추가")
    await task_command(update, create_mock_context())

    # 에이전트 실행 대기
    await asyncio.sleep(5)

    # 로그 파일 생성 확인
    logs = list(Path(".ccw/logs").glob("*.md"))
    assert len(logs) > 0

    # 로그 내용 검증
    log_content = logs[0].read_text()
    assert "main.py" in log_content
```

### 3. 계약 테스트 (Contract Tests)

**테스트 대상**:
- Claude API 응답 형식
- Telegram Bot API 응답 형식
- GitHub API 응답 형식

**예시**:
```python
@pytest.mark.contract
async def test_claude_api_contract():
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = await client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello"}]
    )

    # 응답 스키마 검증
    assert hasattr(response, 'content')
    assert isinstance(response.content, list)
    assert len(response.content) > 0
```

## 오류 처리 및 로깅

### 1. 예외 처리 전략

**원칙**: 모든 예외는 캡처하여 분석 후 텔레그램으로 전송

**구현**:
```python
import traceback
from src.agents.error_agent import ErrorAgent

async def execute_with_error_handling(task_func, telegram_update):
    try:
        return await task_func()
    except Exception as e:
        # 스택 트레이스 캡처
        tb = traceback.format_exc()

        # ErrorAgent로 분석
        error_agent = ErrorAgent(anthropic_client)
        analysis = await error_agent.analyze(e, tb)

        # 텔레그램 전송
        await telegram_update.message.reply_text(
            f"오류 발생:\n\n{analysis}"
        )

        # 로그 파일에 기록
        await log_error(e, tb, analysis)

        raise
```

### 2. 로깅 구조

**로그 레벨**:
- DEBUG: 개발 시 상세 정보
- INFO: 작업 시작/완료, 명령 실행
- WARNING: 타임아웃 임박, API 레이트 리미트
- ERROR: 예외 발생, 작업 실패

**구현**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.ccw/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## 배포 및 운영

### 1. 환경 변수 관리

**.env.example**:
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Anthropic Claude
ANTHROPIC_API_KEY=your_api_key_here

# GitHub
GITHUB_TOKEN=your_personal_access_token
GITHUB_REPO=owner/repo

# Application
TASK_TIMEOUT_MINUTES=30
MAX_LOG_COUNT=2
LOG_DIRECTORY=.ccw/logs
```

### 2. 프로세스 관리

**권장 도구**: systemd (우분투 서버)

**서비스 파일 예시** (`/etc/systemd/system/ccw.service`):
```ini
[Unit]
Description=Claude Code Worker Telegram Bot
After=network.target

[Service]
Type=simple
User=randy
WorkingDirectory=/home/randy/my-remote-worker
Environment="PATH=/home/randy/.local/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/randy/.local/bin/uv run python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. GitHub Actions 통합

**배포 워크플로우** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy CCW

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

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

## 마일스톤 및 작업 분해

### Phase 1: 기본 인프라 (P1 - 필수)

1. 프로젝트 초기화 (uv, pyproject.toml)
2. 텔레그램 봇 기본 구조 (인증, 명령어 핸들러)
3. Claude Agent SDK 통합
4. 4가지 에이전트 모듈 스켈레톤

### Phase 2: 핵심 기능 (P1 - 필수)

1. `/task` 명령어 및 작업 실행
2. 작업 로그 생성/읽기
3. 컨텍스트 관리 (마지막 2개 로그)
4. 타임아웃 및 중단 처리

### Phase 3: Git 통합 (P2 - 중요)

1. `/diff` 명령어 및 커밋 메시지 생성
2. `/commit` 명령어
3. `/branch` 명령어
4. `/mr` 명령어 및 GitHub Actions 통합

### Phase 4: 서버 명령 (P3 - 부가)

1. `/exec` 명령어
2. 명령어 검증 및 차단
3. 콘솔 출력 포맷팅

### Phase 5: 로그 조회 (P3 - 부가)

1. `/logs` 명령어
2. 로그 파일 읽기 및 포맷팅

## 리스크 및 완화 방안

| 리스크 | 영향 | 완화 방안 |
|--------|------|----------|
| Claude API 레이트 리미트 | 높음 | 요청 큐잉, 재시도 로직, 사용량 모니터링 |
| 텔레그램 연결 불안정 | 중간 | 연결 모니터링, 자동 재연결, 작업 중단 처리 |
| GitHub API 인증 실패 | 중간 | 토큰 갱신 자동화, 예외 처리 및 알림 |
| 작업 로그 파일 손상 | 낮음 | 백업 전략, Git 추적, 파일 검증 |
| 30분 타임아웃 부족 | 낮음 | 사용자 설정 가능하도록 환경 변수화 |

## 참고 자료

### 공식 문서
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [PyGitHub Documentation](https://pygithub.readthedocs.io/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

### 모범 사례
- [Telegram Bot Best Practices](https://core.telegram.org/bots/best-practices)
- [Python Async Best Practices](https://docs.python.org/3/library/asyncio-dev.html)
- [GitHub API Best Practices](https://docs.github.com/en/rest/guides/best-practices-for-integrators)

## 다음 단계

Phase 0 연구가 완료되었습니다. 다음 Phase 1에서 진행할 작업:

1. **data-model.md 생성**: 주요 엔티티 및 데이터 모델 설계
2. **contracts/ 생성**: 에이전트 간 인터페이스, API 스키마 정의
3. **quickstart.md 생성**: 개발 환경 설정 및 빠른 시작 가이드
4. **agent context 업데이트**: 기술 스택 정보를 Claude Code 에이전트 컨텍스트에 추가

모든 NEEDS CLARIFICATION 항목이 해결되었으며, 구체적인 기술 스택과 구현 방법이 결정되었습니다.
