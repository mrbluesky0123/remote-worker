# 외부 API 계약 명세

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-15 (최종 업데이트)
**버전**: 2.0.0

## 개요

이 문서는 CCW가 통합하는 외부 API(Claude API, GitHub API)의 호출 계약을 정의합니다.

**사용 모델**:
- **MainAgent**: `claude-sonnet-4` (고품질 코드 작성)
- **LoggerAgent**: `claude-haiku-4` (저비용 로그 생성)

---

## Claude API 계약

### 1. Messages API (대화형 응답)

**엔드포인트**: `POST https://api.anthropic.com/v1/messages`

**인증**: API 키 (헤더: `x-api-key`)

**요청 스키마**:
```json
{
  "model": "claude-sonnet-4",
  "max_tokens": 4096,
  "system": "당신은 Python 코딩 전문가입니다...",
  "messages": [
    {
      "role": "user",
      "content": "main.py에 로깅 기능 추가"
    }
  ]
}
```

**Note**: LoggerAgent는 `claude-haiku-4`를 사용하여 비용을 절감합니다.

**응답 스키마** (성공):
```json
{
  "id": "msg_abc123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "main.py에 비동기 로깅 기능을 추가했습니다..."
    }
  ],
  "model": "claude-sonnet-4",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 320
  }
}
```

**응답 스키마** (오류):
```json
{
  "type": "error",
  "error": {
    "type": "rate_limit_error",
    "message": "You have exceeded the rate limit for this API."
  }
}
```

**Python 구현 예시**:
```python
from anthropic import Anthropic
import os

async def call_claude(prompt: str, system_prompt: str, model: str = "claude-sonnet-4") -> str:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    try:
        response = await client.messages.create(
            model=model,  # MainAgent: "claude-sonnet-4", LoggerAgent: "claude-haiku-4"
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    except anthropic.RateLimitError as e:
        # 레이트 리미트 처리
        raise
    except anthropic.APIConnectionError as e:
        # 연결 오류 처리
        raise
```

### 2. Streaming API (스트리밍 응답)

**엔드포인트**: `POST https://api.anthropic.com/v1/messages` (stream=true)

**요청 스키마**:
```json
{
  "model": "claude-sonnet-4",
  "max_tokens": 4096,
  "stream": true,
  "system": "...",
  "messages": [...]
}
```

**응답 스트림**:
```
event: message_start
data: {"type":"message_start","message":{"id":"msg_abc123",...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"main"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":".py에"}}

...

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":320}}

event: message_stop
data: {"type":"message_stop"}
```

**Python 구현 예시**:
```python
async def stream_claude(prompt: str, system_prompt: str, model: str = "claude-sonnet-4"):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    async with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)

        # 최종 메시지
        message = await stream.get_final_message()
        return message.content[0].text
```

### 3. 에러 처리

**에러 타입**:

| 에러 타입 | HTTP 상태 | 설명 | 처리 방법 |
|----------|-----------|------|-----------|
| invalid_request_error | 400 | 잘못된 요청 | 요청 파라미터 수정 |
| authentication_error | 401 | 인증 실패 | API 키 확인 |
| permission_error | 403 | 권한 없음 | API 키 권한 확인 |
| not_found_error | 404 | 리소스 없음 | 엔드포인트 확인 |
| rate_limit_error | 429 | 레이트 리미트 초과 | 재시도 (지수 백오프) |
| api_error | 500 | 서버 오류 | 재시도 |
| overloaded_error | 529 | 서버 과부하 | 재시도 |

**재시도 전략**:
```python
import asyncio
from anthropic import Anthropic, RateLimitError, APIConnectionError

async def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            # 지수 백오프: 2^attempt 초 대기
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
        except APIConnectionError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
```

### 4. 토큰 사용량 추적

**목적**: 비용 관리 및 컨텍스트 윈도우 제한 준수

```python
@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def cost_usd(self, model: str = "claude-sonnet-4") -> float:
        # Claude 모델별 가격 (예시 - 실제 가격은 Anthropic 공식 문서 참조)
        if model == "claude-sonnet-4":
            input_cost = self.input_tokens * 0.003 / 1000
            output_cost = self.output_tokens * 0.015 / 1000
        elif model == "claude-haiku-4":
            # Haiku는 약 10배 저렴
            input_cost = self.input_tokens * 0.0003 / 1000
            output_cost = self.output_tokens * 0.0015 / 1000
        else:
            raise ValueError(f"Unknown model: {model}")

        return input_cost + output_cost

class AgentSession:
    def __init__(self):
        self.token_usage = TokenUsage()

    async def execute(self, prompt: str):
        response = await client.messages.create(...)

        # 토큰 사용량 누적
        self.token_usage.input_tokens += response.usage.input_tokens
        self.token_usage.output_tokens += response.usage.output_tokens

        return response.content[0].text
```

---

## GitHub API 계약

### 1. 인증

**방법**: Personal Access Token (PAT)

**권한 필요**:
- `repo`: 리포지토리 읽기/쓰기
- `workflow`: GitHub Actions 조회

**헤더**:
```
Authorization: token ghp_xxxxxxxxxxxxx
Accept: application/vnd.github.v3+json
```

### 2. Git Commit API

**엔드포인트**: `POST /repos/{owner}/{repo}/git/commits`

**요청 스키마**:
```json
{
  "message": "feat: Add async logging functionality",
  "tree": "tree_sha",
  "parents": ["parent_commit_sha"]
}
```

**Python 구현 (PyGitHub)**:
```python
from github import Github
import os

def create_commit(message: str, files: list[str]):
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPO"])

    # 현재 브랜치 가져오기
    branch = repo.get_branch("feature-logging")
    commit = repo.get_commit(branch.commit.sha)

    # 파일 변경사항 추가
    # (PyGitHub는 로컬 Git 작업 후 push 권장)
    # 실제 구현은 GitPython 사용

    return commit.sha
```

### 3. Pull Request API

**엔드포인트**: `POST /repos/{owner}/{repo}/pulls`

**요청 스키마**:
```json
{
  "title": "feat: Add async logging functionality",
  "head": "feature-logging",
  "base": "main",
  "body": "## 요약\n- 비동기 로깅 기능 구현\n\n## 변경사항\n- src/utils/logger.py (신규)\n- src/main.py (수정)"
}
```

**응답 스키마**:
```json
{
  "id": 123456,
  "number": 123,
  "state": "open",
  "title": "feat: Add async logging functionality",
  "html_url": "https://github.com/owner/repo/pull/123",
  "user": {...},
  "created_at": "2025-11-08T10:30:00Z"
}
```

**Python 구현**:
```python
def create_pull_request(title: str, head: str, base: str, body: str):
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPO"])

    pr = repo.create_pull(
        title=title,
        head=head,
        base=base,
        body=body
    )

    return pr.html_url
```

### 4. Branch API

**엔드포인트**: `POST /repos/{owner}/{repo}/git/refs`

**요청 스키마**:
```json
{
  "ref": "refs/heads/feature-logging",
  "sha": "base_commit_sha"
}
```

**Python 구현**:
```python
def create_branch(base_branch: str, new_branch: str):
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPO"])

    # 기준 브랜치의 최신 커밋 가져오기
    base = repo.get_branch(base_branch)
    base_sha = base.commit.sha

    # 새 브랜치 생성
    ref = repo.create_git_ref(
        ref=f"refs/heads/{new_branch}",
        sha=base_sha
    )

    return new_branch
```

### 5. GitHub Actions 상태 조회

**엔드포인트**: `GET /repos/{owner}/{repo}/actions/runs`

**응답 스키마**:
```json
{
  "total_count": 5,
  "workflow_runs": [
    {
      "id": 789012,
      "name": "Deploy CCW",
      "status": "completed",
      "conclusion": "success",
      "created_at": "2025-11-08T10:35:00Z",
      "updated_at": "2025-11-08T10:40:00Z",
      "html_url": "https://github.com/owner/repo/actions/runs/789012"
    }
  ]
}
```

**Python 구현**:
```python
import asyncio

async def monitor_deployment(workflow_run_id: int, telegram_bot):
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPO"])

    while True:
        run = repo.get_workflow_run(workflow_run_id)

        if run.status == "completed":
            if run.conclusion == "success":
                await telegram_bot.send_message(
                    "✅ 배포 성공\n\n"
                    f"워크플로우: {run.name}\n"
                    f"링크: {run.html_url}"
                )
            else:
                await telegram_bot.send_message(
                    "❌ 배포 실패\n\n"
                    f"워크플로우: {run.name}\n"
                    f"원인: {run.conclusion}\n"
                    f"링크: {run.html_url}"
                )
            break

        await asyncio.sleep(30)  # 30초마다 체크
```

### 6. 에러 처리

**에러 타입**:

| HTTP 상태 | 설명 | 처리 방법 |
|-----------|------|-----------|
| 401 | 인증 실패 | GitHub Token 확인 |
| 403 | 권한 없음 또는 레이트 리미트 | Token 권한 확인 또는 대기 |
| 404 | 리소스 없음 | 리포지토리/브랜치 확인 |
| 422 | 검증 실패 | 요청 파라미터 수정 |
| 500 | 서버 오류 | 재시도 |

**레이트 리미트**:
- 인증된 요청: 5,000 req/hour
- 확인: `X-RateLimit-Remaining` 헤더

```python
def check_rate_limit(g: Github):
    rate_limit = g.get_rate_limit()

    if rate_limit.core.remaining < 100:
        reset_time = rate_limit.core.reset
        wait_seconds = (reset_time - datetime.now()).total_seconds()

        raise RateLimitError(
            f"GitHub API 레이트 리미트 임박. "
            f"{wait_seconds}초 후 재시도"
        )
```

---

## API 호출 베스트 프랙티스

### 1. 타임아웃 설정

```python
import httpx

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    timeout=httpx.Timeout(60.0, connect=5.0)
)
```

### 2. 연결 풀 재사용

```python
# 글로벌 클라이언트 인스턴스 재사용
ANTHROPIC_CLIENT = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
GITHUB_CLIENT = Github(os.environ["GITHUB_TOKEN"])
```

### 3. 로깅

```python
import logging

logger = logging.getLogger(__name__)

async def call_claude(prompt: str):
    logger.info(f"Claude API 호출: {prompt[:50]}...")

    try:
        response = await client.messages.create(...)
        logger.info(
            f"Claude API 응답: {response.usage.input_tokens} 입력, "
            f"{response.usage.output_tokens} 출력 토큰"
        )
        return response.content[0].text

    except Exception as e:
        logger.error(f"Claude API 오류: {e}")
        raise
```

### 4. 캐싱 (선택적)

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_github_repo():
    g = Github(os.environ["GITHUB_TOKEN"])
    return g.get_repo(os.environ["GITHUB_REPO"])
```

---

## 다음 단계

외부 API 계약이 정의되었습니다. 다음 작업:

1. **quickstart.md** 생성: 개발 환경 설정 가이드
2. **agent context 업데이트**: 기술 스택 정보를 에이전트 컨텍스트에 추가
3. **Constitution Check 재평가**: Phase 1 설계 완료 후 재검토
