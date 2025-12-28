"""
에이전트 기본 인터페이스

모든 에이전트가 상속받는 추상 클래스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from anthropic import AsyncAnthropic


class BaseAgent(ABC):
    """
    모든 에이전트의 기본 클래스

    Attributes:
        client: Anthropic Claude API 클라이언트 (Async)
        model: 사용할 LLM 모델 (예: claude-sonnet-4, claude-haiku-4)
        system_prompt: 에이전트의 시스템 프롬프트
    """

    def __init__(self, client: AsyncAnthropic, model: str):
        """
        Args:
            client: Anthropic API 클라이언트 (Async)
            model: LLM 모델 이름
        """
        self.client = client
        self.model = model
        self.system_prompt = ""

    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        작업을 실행하는 메서드 (각 에이전트가 구현해야 함)

        Args:
            task: 수행할 작업 설명
            context: 추가 컨텍스트 정보 (선택적)

        Returns:
            작업 실행 결과
        """
        pass

    def _build_context_message(self, context: Optional[Dict[str, Any]]) -> str:
        """
        컨텍스트 딕셔너리를 메시지 문자열로 변환

        Args:
            context: 컨텍스트 딕셔너리

        Returns:
            포맷팅된 컨텍스트 메시지
        """
        if not context:
            return ""

        lines = ["## 컨텍스트 정보\n"]

        if "recent_logs" in context:
            lines.append("### 최근 작업 로그")
            for i, log in enumerate(context["recent_logs"], 1):
                lines.append(f"\n#### 작업 {i}\n")
                lines.append(log)

        if "environment" in context:
            lines.append("\n### 환경 정보")
            for key, value in context["environment"].items():
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)
