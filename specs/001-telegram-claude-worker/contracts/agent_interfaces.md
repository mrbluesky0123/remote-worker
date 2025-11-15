# 에이전트 인터페이스 계약

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-08
**버전**: 1.0.0

## 개요

이 문서는 4가지 전문 에이전트(CodingAgent, LogAgent, ServerAgent, ErrorAgent)의 인터페이스 계약을 정의합니다.

## 기본 에이전트 인터페이스

### BaseAgent

모든 에이전트가 구현해야 하는 기본 인터페이스입니다.

```python
from abc import ABC, abstractmethod
from anthropic import Anthropic
from typing import Optional

class BaseAgent(ABC):
    """기본 에이전트 인터페이스"""

    def __init__(self, client: Anthropic):
        """
        Args:
            client: Anthropic Claude API 클라이언트
        """
        self.client = client
        self.system_prompt = self._get_system_prompt()

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        에이전트별 시스템 프롬프트 반환

        Returns:
            str: 에이전트의 역할과 행동 지침을 정의하는 시스템 프롬프트
        """
        pass

    @abstractmethod
    async def execute(
        self,
        task: str,
        context: Optional[dict] = None
    ) -> str:
        """
        작업 실행

        Args:
            task: 수행할 작업 설명
            context: 작업 컨텍스트 (이전 로그, 환경 정보 등)

        Returns:
            str: 작업 수행 결과

        Raises:
            AgentExecutionError: 작업 실행 실패 시
            TimeoutError: 작업 타임아웃 시
        """
        pass

    async def _call_claude(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        stream: bool = False
    ) -> str:
        """
        Claude API 호출 공통 로직

        Args:
            messages: 메시지 히스토리
            max_tokens: 최대 생성 토큰 수
            stream: 스트리밍 응답 여부

        Returns:
            str: Claude의 응답
        """
        pass
```

## 1. CodingAgent (코딩 전문가)

### 역할
- 코드 작성, 수정, 리팩토링
- 버그 수정 및 기능 추가
- 코드 리뷰 및 제안

### 인터페이스

```python
from src.agents.base import BaseAgent

class CodingAgent(BaseAgent):
    """코딩 전문가 에이전트"""

    def _get_system_prompt(self) -> str:
        return """당신은 Python 코딩 전문가입니다.

역할:
- 사용자의 요청에 따라 고품질 Python 코드를 작성합니다
- 기존 코드를 분석하고 개선 방안을 제시합니다
- PEP 8 스타일 가이드를 준수합니다
- 테스트 가능한 코드를 작성합니다
- 명확한 주석과 문서화를 제공합니다

제약사항:
- 30분 내에 완료 가능한 작업만 수행합니다
- 사용자의 명시적 요청 없이 Git 커밋을 하지 않습니다
- 파괴적 작업(파일 삭제 등)은 사용자 확인을 받습니다
"""

    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """
        코딩 작업 실행

        Args:
            task: 작업 설명 (예: "main.py에 로깅 기능 추가")
            context: {
                "recent_logs": list[str],  # 마지막 2개 작업 로그
                "current_branch": str,      # 현재 Git 브랜치
                "files": list[str]          # 관련 파일 목록
            }

        Returns:
            str: 작업 완료 메시지 및 변경 사항 요약

        Example:
            >>> agent = CodingAgent(client)
            >>> result = await agent.execute(
            ...     "main.py에 비동기 로깅 추가",
            ...     {"recent_logs": [...], "current_branch": "feature-logging"}
            ... )
            >>> print(result)
            "main.py에 asyncio 기반 로깅 기능을 추가했습니다.
            - logging.handlers.RotatingFileHandler 사용
            - 비동기 로그 쓰기 구현
            - 테스트 코드 추가: tests/unit/test_logging.py"
        """
        pass

    async def review_code(self, file_path: str) -> str:
        """
        코드 리뷰

        Args:
            file_path: 리뷰할 파일 경로

        Returns:
            str: 리뷰 결과 (개선 사항, 버그, 스타일 이슈)
        """
        pass

    async def generate_tests(self, file_path: str) -> str:
        """
        테스트 코드 생성

        Args:
            file_path: 테스트를 생성할 대상 파일

        Returns:
            str: 생성된 테스트 코드 경로 및 내용
        """
        pass
```

### 입출력 계약

**입력**:
```json
{
  "task": "src/telegram/bot.py에 에러 핸들러 추가",
  "context": {
    "recent_logs": [
      "# feature-auth\n\n## 요약\n사용자 인증 구현...",
      "# bug-123\n\n## 요약\n텔레그램 연결 오류 수정..."
    ],
    "current_branch": "feature-error-handling",
    "files": ["src/telegram/bot.py"]
  }
}
```

**출력**:
```json
{
  "status": "completed",
  "message": "에러 핸들러를 추가했습니다.",
  "changes": [
    {
      "file": "src/telegram/bot.py",
      "action": "modified",
      "summary": "error_handler 함수 추가 및 Application에 등록"
    },
    {
      "file": "tests/unit/test_telegram/test_bot.py",
      "action": "created",
      "summary": "에러 핸들러 테스트 추가"
    }
  ],
  "next_steps": [
    "테스트 실행하여 검증",
    "로그 파일 생성 확인"
  ]
}
```

## 2. LogAgent (작업 로그 작성 전문가)

### 역할
- 작업 완료 후 마크다운 로그 생성
- 결정사항, 이슈, 논의 내용 문서화
- 이슈별 로그 그룹화 및 업데이트

### 인터페이스

```python
class LogAgent(BaseAgent):
    """작업 로그 작성 전문가 에이전트"""

    def _get_system_prompt(self) -> str:
        return """당신은 작업 로그 작성 전문가입니다.

역할:
- 개발 작업 완료 후 명확하고 간결한 로그를 작성합니다
- 내린 결정과 그 근거를 문서화합니다
- 발생한 이슈와 해결 방법을 기록합니다
- 사용자와의 논의 내용을 요약합니다

작성 원칙:
- 간결함: 2000 토큰 이하로 작성합니다
- 명확함: 기술적 배경이 없는 사람도 이해할 수 있게 작성합니다
- 맥락: 다음 작업 세션에서 참고할 수 있도록 충분한 정보를 제공합니다
- 한글: 모든 내용을 한글로 작성합니다 (기술 용어는 원문 유지)
"""

    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """
        작업 로그 생성 또는 업데이트

        Args:
            task: "작업 로그 생성" (고정)
            context: {
                "task_id": str,              # 작업 ID
                "task_description": str,     # 작업 설명
                "task_result": str,          # 작업 결과
                "issue_id": str,             # 이슈 ID (기존 로그가 있으면 업데이트)
                "decisions": list[str],      # 내린 결정
                "issues": list[str],         # 발생한 이슈
                "discussions": list[str]     # 논의 내용
            }

        Returns:
            str: 생성/업데이트된 로그 파일 경로

        Example:
            >>> agent = LogAgent(client)
            >>> result = await agent.execute(
            ...     "작업 로그 생성",
            ...     {
            ...         "task_id": "abc-123",
            ...         "task_description": "텔레그램 봇 에러 핸들러 추가",
            ...         "task_result": "에러 핸들러 구현 완료",
            ...         "issue_id": "feature-error-handling",
            ...         "decisions": ["python-telegram-bot의 error_handler 사용"],
            ...         "issues": ["텔레그램 API 연결 오류 처리"],
            ...         "discussions": []
            ...     }
            ... )
            >>> print(result)
            "로그가 생성되었습니다: .ccw/logs/feature-error-handling.md"
        """
        pass

    async def summarize_task(self, task_description: str, task_result: str) -> str:
        """
        작업을 간결하게 요약

        Args:
            task_description: 작업 설명
            task_result: 작업 결과

        Returns:
            str: 요약된 작업 내용 (2-3 문장)
        """
        pass

    async def extract_decisions(self, task_result: str) -> list[str]:
        """
        작업 결과에서 결정사항 추출

        Args:
            task_result: 작업 결과 텍스트

        Returns:
            list[str]: 추출된 결정사항 목록
        """
        pass
```

### 입출력 계약

**입력**:
```json
{
  "task": "작업 로그 생성",
  "context": {
    "task_id": "abc-123",
    "task_description": "텔레그램 봇 에러 핸들러 추가",
    "task_result": "에러 핸들러를 추가했습니다. src/telegram/bot.py 수정, 테스트 추가",
    "issue_id": "feature-error-handling",
    "decisions": ["python-telegram-bot의 error_handler 사용"],
    "issues": ["텔레그램 API 연결 오류 처리 필요"],
    "discussions": ["Q: 모든 예외를 캐치할까요? A: 예, 모든 예외를 캐치하고 사용자에게 알립니다."]
  }
}
```

**출력**:
```json
{
  "status": "completed",
  "log_file": ".ccw/logs/feature-error-handling.md",
  "token_count": 1234,
  "summary": "텔레그램 봇에 포괄적인 에러 핸들러를 추가했습니다."
}
```

**생성된 로그 파일** (.ccw/logs/feature-error-handling.md):
```markdown
# feature-error-handling

**작업 ID**: abc-123
**최초 생성**: 2025-11-08T10:30:00
**마지막 업데이트**: 2025-11-08T10:30:00

## 요약

텔레그램 봇에 포괄적인 에러 핸들러를 추가했습니다. 모든 예외를 캐치하고 사용자에게 알림을 전송합니다.

## 수행한 작업

- src/telegram/bot.py에 error_handler 함수 추가
- Application에 에러 핸들러 등록
- tests/unit/test_telegram/test_bot.py에 테스트 추가

## 내린 결정

- python-telegram-bot의 error_handler 사용: 공식 라이브러리의 패턴을 따라 안정성 확보

## 발생한 이슈

- 텔레그램 API 연결 오류 처리 필요: 네트워크 오류 시 재시도 로직 추가 예정

## 논의 내용

- Q: 모든 예외를 캐치할까요?
  A: 예, 모든 예외를 캐치하고 사용자에게 알립니다.
```

## 3. ServerAgent (서버 명령어 수행 전문가)

### 역할
- 안전한 서버 명령어 실행
- 명령어 검증 및 차단 (파괴적 명령)
- 콘솔 출력 포맷팅

### 인터페이스

```python
class ServerAgent(BaseAgent):
    """서버 명령어 수행 전문가 에이전트"""

    def _get_system_prompt(self) -> str:
        return """당신은 우분투 서버 명령어 수행 전문가입니다.

역할:
- 사용자가 요청한 서버 명령어를 안전하게 실행합니다
- 명령어 실행 결과를 명확하게 포맷팅합니다
- 파괴적 명령어를 차단하고 대안을 제시합니다

안전 규칙:
- 파괴적 명령 차단: rm, rmdir, mkfs, dd, format
- 대화형 명령 차단: vi, vim, nano, emacs, less, more
- 시스템 경로 쓰기 차단: /etc/, /sys/, /proc/, /boot/
- 차단 시 명확한 사유와 대안을 제공합니다
"""

    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """
        서버 명령어 실행

        Args:
            task: 실행할 명령어
            context: {
                "working_dir": str  # 작업 디렉토리 (기본: 현재 디렉토리)
            }

        Returns:
            str: 명령어 실행 결과 (stdout, stderr, exit_code)

        Raises:
            CommandBlockedError: 명령어가 차단된 경우

        Example:
            >>> agent = ServerAgent(client)
            >>> result = await agent.execute("ls -la", {})
            >>> print(result)
            "명령어: ls -la
            종료 코드: 0

            출력:
            total 24
            drwxr-xr-x  5 randy randy 4096 Nov  8 10:30 .
            drwxr-xr-x 15 randy randy 4096 Nov  8 09:00 ..
            -rw-r--r--  1 randy randy  123 Nov  8 10:30 main.py"
        """
        pass

    async def suggest_alternative(self, blocked_command: str) -> str:
        """
        차단된 명령어의 대안 제시

        Args:
            blocked_command: 차단된 명령어

        Returns:
            str: 대안 제시 메시지

        Example:
            >>> result = await agent.suggest_alternative("vi config.txt")
            >>> print(result)
            "대화형 명령어 'vi'는 지원되지 않습니다.
            대안: 'cat config.txt'로 파일 내용을 확인하세요."
        """
        pass
```

### 입출력 계약

**입력**:
```json
{
  "task": "ls -la src/",
  "context": {
    "working_dir": "/home/randy/my-remote-worker"
  }
}
```

**출력 (성공)**:
```json
{
  "status": "completed",
  "command": "ls -la src/",
  "exit_code": 0,
  "stdout": "total 24\ndrwxr-xr-x 5 randy randy 4096 Nov  8 10:30 .\n...",
  "stderr": "",
  "execution_time_ms": 45
}
```

**출력 (차단)**:
```json
{
  "status": "blocked",
  "command": "rm -rf /tmp/test",
  "reason": "파괴적 명령어 'rm'는 실행할 수 없습니다.",
  "alternative": "파일을 안전하게 삭제하려면 먼저 'ls /tmp/test'로 내용을 확인하고, 사용자에게 명시적으로 삭제를 요청하세요."
}
```

## 4. ErrorAgent (Python 오류 분석 전문가)

### 역할
- 예외 스택 트레이스 분석
- 오류 원인 및 해결 방법 제안
- 텔레그램으로 오류 보고 포맷팅

### 인터페이스

```python
class ErrorAgent(BaseAgent):
    """Python 오류 분석 전문가 에이전트"""

    def _get_system_prompt(self) -> str:
        return """당신은 Python 오류 분석 전문가입니다.

역할:
- Python 예외 스택 트레이스를 분석합니다
- 오류의 근본 원인을 파악합니다
- 구체적인 해결 방법을 제시합니다
- 비개발자도 이해할 수 있도록 명확하게 설명합니다

분석 방법:
- 스택 트레이스를 역순으로 분석 (최상위 호출부터)
- 오류 타입과 메시지를 기반으로 원인 추론
- 관련 코드 라인 검토
- 일반적인 해결 패턴 적용
"""

    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """
        오류 분석 (execute는 task가 문자열이므로 analyze로 대체 권장)
        """
        pass

    async def analyze(
        self,
        exception: Exception,
        traceback_str: str,
        context: Optional[dict] = None
    ) -> str:
        """
        예외 분석

        Args:
            exception: 발생한 예외 객체
            traceback_str: 스택 트레이스 문자열
            context: {
                "task_description": str,  # 수행 중이던 작업
                "environment": dict       # 환경 정보 (Python 버전, OS 등)
            }

        Returns:
            str: 분석 결과 (원인, 해결 방법, 예방책)

        Example:
            >>> agent = ErrorAgent(client)
            >>> try:
            ...     result = await some_async_function()
            ... except Exception as e:
            ...     tb = traceback.format_exc()
            ...     analysis = await agent.analyze(e, tb)
            ...     print(analysis)
            "오류 분석:

            **오류 타입**: asyncio.TimeoutError

            **원인**:
            작업이 30분 타임아웃 시간을 초과했습니다.
            Claude API 호출이 응답하지 않았을 가능성이 있습니다.

            **해결 방법**:
            1. 네트워크 연결 확인
            2. Anthropic API 상태 페이지 확인
            3. 타임아웃 시간 증가 고려 (환경 변수 TASK_TIMEOUT_MINUTES)

            **예방책**:
            - 작업을 더 작은 단위로 분해
            - API 호출 시 재시도 로직 추가
            - 진행 상황을 주기적으로 저장"
        """
        pass

    async def format_for_telegram(self, analysis: str) -> str:
        """
        텔레그램 메시지 형식으로 포맷팅

        Args:
            analysis: 오류 분석 결과

        Returns:
            str: 텔레그램 마크다운 형식의 메시지
        """
        pass
```

### 입출력 계약

**입력**:
```json
{
  "exception": {
    "type": "anthropic.APIConnectionError",
    "message": "Connection timeout"
  },
  "traceback": "Traceback (most recent call last):\n  File \"src/agents/coding_agent.py\", line 45, in execute\n    response = await self.client.messages.create(...)\n...",
  "context": {
    "task_description": "main.py에 로깅 추가",
    "environment": {
      "python_version": "3.13.0",
      "os": "Linux 5.15.0-58-generic"
    }
  }
}
```

**출력**:
```json
{
  "status": "completed",
  "analysis": {
    "error_type": "anthropic.APIConnectionError",
    "root_cause": "Claude API 연결 타임아웃",
    "immediate_cause": "네트워크 지연 또는 API 서버 응답 없음",
    "solution": [
      "네트워크 연결 확인",
      "Anthropic API 상태 페이지 확인 (https://status.anthropic.com)",
      "재시도 로직 추가 (최대 3회, 지수 백오프)"
    ],
    "prevention": [
      "API 호출 시 타임아웃 설정 (기본 60초)",
      "연결 풀 사용하여 재사용"
    ]
  },
  "telegram_message": "🚨 **오류 발생**\n\n**타입**: API 연결 오류\n\n**원인**: Claude API 서버 연결 타임아웃\n\n**해결 방법**:\n1. 네트워크 연결 확인\n2. API 상태 확인\n3. 잠시 후 재시도\n\n작업이 중단되었습니다. 문제 해결 후 다시 시도해주세요."
}
```

## 에이전트 간 협업 패턴

### 패턴 1: Task → CodingAgent → LogAgent

```
1. User: /task "main.py에 로깅 추가"
2. CodingAgent.execute() → 코드 작성
3. LogAgent.execute() → 작업 로그 생성
4. User: 텔레그램 알림 "작업 완료"
```

### 패턴 2: Task → CodingAgent → ErrorAgent → User

```
1. User: /task "복잡한 기능 구현"
2. CodingAgent.execute() → 예외 발생
3. ErrorAgent.analyze() → 오류 분석
4. User: 텔레그램 알림 "오류 분석 결과"
```

### 패턴 3: /exec → ServerAgent → User

```
1. User: /exec "ls -la"
2. ServerAgent.execute() → 명령 실행
3. User: 텔레그램 알림 "실행 결과"
```

## 다음 단계

에이전트 인터페이스 계약이 정의되었습니다. 다음 작업:

1. **telegram_api_schema.json** 생성: 텔레그램 명령어 스키마
2. **claude_api_schema.json** 생성: Claude API 호출 계약
3. **github_api_schema.json** 생성: GitHub API 호출 계약
