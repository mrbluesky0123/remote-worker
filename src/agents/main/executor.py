"""
메인 에이전트 실행 엔진

모든 핵심 작업(코딩, GitHub, 서버 명령, 오류 분석)을 수행하는 메인 에이전트입니다.
"""
import asyncio
from typing import Any, Dict, List, Optional
from anthropic import AsyncAnthropic

from src.agents.base import BaseAgent
from src.agents.main.prompts import MAIN_AGENT_SYSTEM_PROMPT
from src.constants import MAIN_AGENT_MODEL, MAX_TOKENS

# 코딩 도구 import
from src.tools.coding.file_io import read_file, write_file, edit_file
from src.tools.coding.search import glob_files, grep
from src.tools.bash.executor import bash, bash_output

# 도구 함수 매핑
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "glob_files": glob_files,
    "grep": grep,
    "bash": bash,
    "bash_output": bash_output,
}

# Claude API용 도구 스키마
from src.tools import TOOLS


class MainAgent(BaseAgent):
    """
    메인 에이전트 (Claude Sonnet 4)

    모든 핵심 작업을 수행합니다:
    - 코딩: 파일 읽기/쓰기, 검색, 편집
    - GitHub: 커밋, PR, 배포 모니터링
    - Bash: 안전한 명령 실행
    - 오류 분석: 예외 분석 및 해결 방법 제시
    """

    def __init__(self, client: AsyncAnthropic):
        """
        Args:
            client: Anthropic API 클라이언트 (Async)
        """
        super().__init__(client, MAIN_AGENT_MODEL)
        self.system_prompt = MAIN_AGENT_SYSTEM_PROMPT

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        작업을 실행합니다.

        Args:
            task: 수행할 작업 설명
            context: 추가 컨텍스트 (recent_logs, current_branch 등)

        Returns:
            작업 수행 결과

        Raises:
            Exception: 작업 실행 중 오류 발생 시
        """
        # 메시지 히스토리 초기화
        messages = self._build_messages_with_context(task, context)

        # 도구 사용 루프 (최대 10회 반복)
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Claude API 호출
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=TOOLS,
                messages=messages
            )

            # 응답 처리
            if response.stop_reason == "end_turn":
                # 작업 완료
                final_text = self._extract_text_from_response(response)
                return final_text

            elif response.stop_reason == "tool_use":
                # 도구 사용 요청
                # Assistant 메시지 추가
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # 도구 실행 및 결과 수집
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_id = content_block.id

                        # 도구 실행
                        try:
                            result = await self._execute_tool(tool_name, tool_input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": str(result)
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": f"도구 실행 오류: {str(e)}",
                                "is_error": True
                            })

                # 도구 결과를 user 메시지로 추가
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            elif response.stop_reason == "max_tokens":
                # 토큰 제한 도달
                return "오류: 응답이 너무 깁니다. 작업을 더 작은 단위로 나누어 주세요."

            else:
                # 기타 종료 사유
                return f"작업 중단: {response.stop_reason}"

        return "오류: 최대 반복 횟수에 도달했습니다. 작업이 너무 복잡합니다."

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        도구를 실행합니다.

        Args:
            tool_name: 도구 이름
            tool_input: 도구 입력 파라미터

        Returns:
            도구 실행 결과
        """
        if tool_name not in TOOL_FUNCTIONS:
            raise ValueError(f"알 수 없는 도구: {tool_name}")

        func = TOOL_FUNCTIONS[tool_name]

        # 비동기 함수인지 확인
        if asyncio.iscoroutinefunction(func):
            return await func(**tool_input)
        else:
            return func(**tool_input)

    def _build_messages_with_context(
        self,
        task: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        작업과 컨텍스트를 메시지 리스트로 변환합니다.

        Args:
            task: 작업 설명
            context: 컨텍스트 정보

        Returns:
            Claude API용 메시지 리스트
        """
        messages = []

        # 이전 로그 주입 (컨텍스트)
        if context and context.get("recent_logs"):
            log_context = "\n\n---\n\n".join(context["recent_logs"])
            messages.append({
                "role": "user",
                "content": f"## 이전 작업 로그\n\n{log_context}"
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

    def _extract_text_from_response(self, response) -> str:
        """
        Claude 응답에서 텍스트를 추출합니다.

        Args:
            response: Claude API 응답

        Returns:
            추출된 텍스트
        """
        text_parts = []
        for content_block in response.content:
            if content_block.type == "text":
                text_parts.append(content_block.text)

        return "\n".join(text_parts) if text_parts else ""
