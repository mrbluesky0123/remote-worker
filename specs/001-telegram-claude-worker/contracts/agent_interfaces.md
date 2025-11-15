# 에이전트 인터페이스 계약

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-15 (최종 업데이트)
**버전**: 2.0.0

## 개요

이 문서는 2개의 특화된 에이전트(MainAgent, LoggerAgent)의 인터페이스 계약을 정의합니다.

**아키텍처 결정**:
- **MainAgent (Claude Sonnet 4)**: 모든 핵심 작업 수행 (코딩, GitHub, 서버 명령, 오류 분석)
- **LoggerAgent (Claude Haiku 4)**: 작업 로그 생성 전용 (비용 효율화)

## 기본 에이전트 인터페이스

### BaseAgent

모든 에이전트가 구현해야 하는 기본 인터페이스입니다.

```python
from abc import ABC, abstractmethod
from anthropic import Anthropic
from typing import Optional

class BaseAgent(ABC):
    """기본 에이전트 인터페이스"""

    def __init__(self, client: Anthropic, model: str):
        """
        Args:
            client: Anthropic Claude API 클라이언트
            model: 사용할 Claude 모델 (예: "claude-sonnet-4", "claude-haiku-4")
        """
        self.client = client
        self.model = model
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
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=messages,
            stream=stream
        )

        if stream:
            # 스트리밍 처리
            pass
        else:
            return response.content[0].text
```

## 1. MainAgent (메인 에이전트)

### 역할
- **코딩**: 코드 작성, 수정, 리팩토링, 버그 수정
- **GitHub 통합**: 커밋 생성, PR 생성, 배포 모니터링
- **서버 명령**: 안전한 명령어 실행, 파괴적 명령 차단
- **오류 분석**: 예외 분석 및 해결 방법 제시
- **요구사항 이해**: 랜디의 작업 요청을 정확히 이해하고 실행

### 사용 모델
- **Claude Sonnet 4**: 고품질 코드 작성 및 복잡한 문제 해결

### 인터페이스

```python
from src.agents.base import BaseAgent
from src.constants import MAIN_AGENT_MODEL  # "claude-sonnet-4"

class MainAgent(BaseAgent):
    """메인 에이전트 (Sonnet): 모든 핵심 작업 수행"""

    def __init__(self, client: Anthropic):
        super().__init__(client, MAIN_AGENT_MODEL)

    def _get_system_prompt(self) -> str:
        return """당신은 Python 개발 전문가이며, 다음 역할을 수행합니다:

**코딩**:
- 사용자의 요청에 따라 고품질 Python 코드를 작성합니다
- 기존 코드를 분석하고 개선 방안을 제시합니다
- PEP 8 스타일 가이드를 준수합니다
- 테스트 가능한 코드를 작성합니다

**GitHub 통합**:
- Git 커밋 메시지를 생성합니다
- Pull Request를 생성하고 요약합니다
- 배포 상태를 모니터링하고 보고합니다

**서버 관리**:
- 안전한 서버 명령어를 실행합니다
- 파괴적 명령(rm, mkfs 등)을 차단하고 대안을 제시합니다
- 대화형 명령(vi, nano 등)을 차단하고 대안을 제시합니다

**오류 분석**:
- Python 예외를 분석하고 원인을 파악합니다
- 구체적인 해결 방법을 제시합니다

**제약사항**:
- 30분 내에 완료 가능한 작업만 수행합니다
- 사용자의 명시적 요청 없이 Git 커밋을 하지 않습니다
- 파괴적 작업은 사용자 확인을 받습니다
- 모든 설명과 주석은 한글로 작성합니다
"""

    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """
        메인 작업 실행

        Args:
            task: 작업 설명 (예: "main.py에 로깅 기능 추가")
            context: {
                "recent_logs": list[str],  # 마지막 2개 작업 로그
                "current_branch": str,      # 현재 Git 브랜치
                "files": list[str],         # 관련 파일 목록
                "task_type": str            # "coding", "github", "bash", "error"
            }

        Returns:
            str: 작업 완료 메시지 및 변경 사항 요약

        Example:
            >>> agent = MainAgent(client)
            >>> result = await agent.execute(
            ...     "main.py에 비동기 로깅 추가",
            ...     {
            ...         "recent_logs": [...],
            ...         "current_branch": "feature-logging",
            ...         "task_type": "coding"
            ...     }
            ... )
            >>> print(result)
            "main.py에 asyncio 기반 로깅 기능을 추가했습니다.
            - logging.handlers.RotatingFileHandler 사용
            - 비동기 로그 쓰기 구현
            - 테스트 코드 추가: tests/unit/test_logging.py"
        """
        # 컨텍스트 주입
        messages = self._build_messages_with_context(task, context)

        # Claude 호출
        response = await self._call_claude(messages)

        return response

    def _build_messages_with_context(
        self,
        task: str,
        context: Optional[dict]
    ) -> list[dict]:
        """
        작업 로그를 컨텍스트로 주입하여 메시지 생성

        Args:
            task: 작업 설명
            context: 컨텍스트 정보

        Returns:
            list[dict]: Claude API용 메시지 리스트
        """
        messages = []

        # 이전 로그 주입
        if context and context.get("recent_logs"):
            log_context = "\n\n---\n\n".join(context["recent_logs"])
            messages.append({
                "role": "user",
                "content": f"이전 작업 로그:\n\n{log_context}"
            })
            messages.append({
                "role": "assistant",
                "content": "이전 작업 로그를 확인했습니다. 컨텍스트를 이해했습니다."
            })

        # 현재 작업
        messages.append({
            "role": "user",
            "content": task
        })

        return messages
```

### 입출력 계약

**입력**:
```json
{
  "task": "src/telegram/bot.py에 에러 핸들러 추가",
  "context": {
    "recent_logs": [
      "# 작업 로그\n\n**일시**: 2025-11-14 10:30:00\n**작업 요청**: \"사용자 인증 구현\"\n\n## 수행한 작업\n- 화이트리스트 검증 로직 추가\n\n## 결정 사항\n- 환경 변수 기반 사용자 ID 관리\n\n## 발생한 이슈\n- 없음\n\n## 다음 작업 참고사항\n- 모든 핸들러에 인증 데코레이터 적용 필요"
    ],
    "current_branch": "feature-error-handling",
    "files": ["src/telegram/bot.py"],
    "task_type": "coding"
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
      "file": "tests/unit/telegram/test_bot.py",
      "action": "created",
      "summary": "에러 핸들러 테스트 추가"
    }
  ],
  "next_steps": [
    "테스트 실행하여 검증",
    "로그 확인"
  ]
}
```

## 2. LoggerAgent (로거 에이전트)

### 역할
- 작업 완료 후 **간결한** 마크다운 로그 생성
- 결정사항, 이슈, 논의 내용 문서화
- 토큰 비용 최소화 (2000 토큰 이하)

### 사용 모델
- **Claude Haiku 4**: 빠르고 저렴한 로그 요약 생성

### 로그 파일 구조
- 파일명: `YYYY-MM-DD-HHmmss.md` (시간 기반)
- 위치: `.ccw/logs/`

### 인터페이스

```python
from src.agents.base import BaseAgent
from src.constants import LOGGER_AGENT_MODEL  # "claude-haiku-4"

class LoggerAgent(BaseAgent):
    """로거 에이전트 (Haiku): 로그 생성 전용"""

    def __init__(self, client: Anthropic):
        super().__init__(client, LOGGER_AGENT_MODEL)

    def _get_system_prompt(self) -> str:
        return """당신은 작업 로그 작성 전문가입니다.

**역할**:
- 개발 작업 완료 후 명확하고 간결한 로그를 작성합니다
- 내린 결정과 그 근거를 문서화합니다
- 발생한 이슈와 해결 방법을 기록합니다
- 다음 작업 세션을 위한 참고사항을 제공합니다

**작성 원칙**:
- **간결함**: 2000 토큰 이하로 작성합니다
- **명확함**: 비개발자도 이해할 수 있게 작성합니다
- **맥락**: 다음 작업 세션에서 참고할 수 있도록 충분한 정보를 제공합니다
- **한글**: 모든 내용을 한글로 작성합니다 (기술 용어는 원문 유지)

**마크다운 템플릿**:
```markdown
# 작업 로그

**일시**: YYYY-MM-DD HH:MM:SS
**작업 요청**: "작업 내용"

## 수행한 작업

- 항목1
- 항목2

## 결정 사항

- 결정1 및 근거

## 발생한 이슈

- 이슈1 및 해결 방법

## 다음 작업 참고사항

- 참고사항1
```
"""

    async def execute(self, task: str, context: Optional[dict] = None) -> str:
        """
        작업 로그 생성

        Args:
            task: "작업 로그 생성" (고정)
            context: {
                "task_request": str,         # 작업 요청 내용
                "task_result": str,          # 메인 에이전트의 작업 결과
                "decisions": list[str],      # 내린 결정
                "issues": list[str],         # 발생한 이슈
                "notes": list[str]           # 다음 작업 참고사항
            }

        Returns:
            str: 생성된 로그 파일 경로

        Example:
            >>> agent = LoggerAgent(client)
            >>> result = await agent.execute(
            ...     "작업 로그 생성",
            ...     {
            ...         "task_request": "텔레그램 봇 에러 핸들러 추가",
            ...         "task_result": "에러 핸들러 구현 완료. src/telegram/bot.py 수정...",
            ...         "decisions": ["python-telegram-bot의 error_handler 사용"],
            ...         "issues": [],
            ...         "notes": ["모든 핸들러에 에러 처리 적용됨"]
            ...     }
            ... )
            >>> print(result)
            "로그가 생성되었습니다: .ccw/logs/2025-11-15-143022.md"
        """
        # 로그 생성 요청 메시지 구성
        prompt = self._build_log_prompt(context)

        # Claude Haiku 호출 (저비용)
        log_content = await self._call_claude([
            {"role": "user", "content": prompt}
        ])

        # 로그 파일 저장
        from src.tools.logging.writer import write_log
        log_path = write_log(
            task_request=context["task_request"],
            work_summary=log_content
        )

        return f"로그가 생성되었습니다: {log_path}"

    def _build_log_prompt(self, context: dict) -> str:
        """로그 생성 프롬프트 작성"""
        return f"""다음 작업에 대한 간결한 로그를 작성해주세요.

**작업 요청**: {context["task_request"]}

**작업 결과**:
{context["task_result"]}

**결정 사항**:
{chr(10).join(f"- {d}" for d in context.get("decisions", []))}

**발생한 이슈**:
{chr(10).join(f"- {i}" for i in context.get("issues", []))}

**다음 작업 참고사항**:
{chr(10).join(f"- {n}" for n in context.get("notes", []))}

위 정보를 바탕으로 마크다운 형식의 작업 로그를 작성하되, 2000 토큰 이하로 간결하게 작성해주세요.
"""
```

### 입출력 계약

**입력**:
```json
{
  "task": "작업 로그 생성",
  "context": {
    "task_request": "텔레그램 봇 에러 핸들러 추가",
    "task_result": "에러 핸들러를 추가했습니다. src/telegram/bot.py 수정, 테스트 추가",
    "decisions": ["python-telegram-bot의 error_handler 사용"],
    "issues": [],
    "notes": ["모든 핸들러에 에러 처리가 적용되었습니다"]
  }
}
```

**출력**:
```json
{
  "status": "completed",
  "log_file": ".ccw/logs/2025-11-15-143022.md",
  "token_count": 456,
  "summary": "텔레그램 봇에 포괄적인 에러 핸들러를 추가했습니다."
}
```

**생성된 로그 파일** (`.ccw/logs/2025-11-15-143022.md`):
```markdown
# 작업 로그

**일시**: 2025-11-15 14:30:22
**작업 요청**: "텔레그램 봇 에러 핸들러 추가"

## 수행한 작업

- src/telegram/bot.py에 error_handler 함수 추가
- Application에 에러 핸들러 등록
- tests/unit/telegram/test_bot.py에 테스트 추가

## 결정 사항

- python-telegram-bot의 error_handler 사용: 공식 라이브러리의 패턴을 따라 안정성 확보

## 발생한 이슈

- 없음

## 다음 작업 참고사항

- 모든 핸들러에 에러 처리가 적용되었습니다
```

## 에이전트 간 협업 패턴

### 패턴 1: Task → MainAgent → LoggerAgent

```
1. User: /task "main.py에 로깅 추가"
2. MainAgent.execute() → 코딩 작업 수행
3. LoggerAgent.execute() → 작업 로그 생성
4. User: 텔레그램 알림 "작업 완료"
```

### 패턴 2: Task → MainAgent → ErrorAnalysis → LoggerAgent

```
1. User: /task "복잡한 기능 구현"
2. MainAgent.execute() → 예외 발생
3. MainAgent (자체 오류 분석) → 오류 분석 및 텔레그램 전송
4. LoggerAgent.execute() → 오류 로그 생성
```

### 패턴 3: /exec → MainAgent (Bash 도구 사용)

```
1. User: /exec "ls -la"
2. MainAgent.execute() → Bash 도구로 명령 실행
3. User: 텔레그램 알림 "실행 결과"
```

### 패턴 4: GitHub Operations → MainAgent

```
1. User: /commit "feat: Add logging"
2. MainAgent.execute() → GitHub 도구로 커밋 생성
3. LoggerAgent.execute() → 커밋 로그 생성
```

## 다음 단계

에이전트 인터페이스 계약이 업데이트되었습니다. 다음 작업:

1. **api_contracts.md** 업데이트: Claude 모델 버전 (Sonnet 4, Haiku 4)
2. **telegram_commands.md** 업데이트: 로그 구조 변경 반영
3. **quickstart.md** 생성: 개발 환경 설정 가이드
