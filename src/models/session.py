"""
에이전트 세션 모델

AgentSession 정의
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
from src.models.task import AgentType


@dataclass
class AgentSession:
    """
    에이전트 세션 모델

    단일 작업을 처리하는 에이전트의 실행 컨텍스트를 나타냅니다.
    """

    task_id: str
    agent_type: AgentType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_logs: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    token_usage: Dict[str, int] = field(
        default_factory=lambda: {"input": 0, "output": 0}
    )

    def add_message(self, role: str, content: str):
        """
        메시지를 히스토리에 추가합니다.

        Args:
            role: 메시지 역할 (user, assistant, system)
            content: 메시지 내용
        """
        self.messages.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

    def update_token_usage(self, input_tokens: int, output_tokens: int):
        """
        토큰 사용량을 업데이트합니다.

        Args:
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수
        """
        self.token_usage["input"] += input_tokens
        self.token_usage["output"] += output_tokens

    def end(self):
        """세션을 종료합니다."""
        self.ended_at = datetime.now()

    def get_duration_seconds(self) -> Optional[float]:
        """
        세션 지속 시간을 초 단위로 반환합니다.

        Returns:
            세션 지속 시간 (초) 또는 None (진행 중)
        """
        if not self.ended_at:
            return None

        return (self.ended_at - self.started_at).total_seconds()

    def get_total_tokens(self) -> int:
        """
        총 토큰 사용량을 반환합니다.

        Returns:
            입력 + 출력 토큰 합계
        """
        return self.token_usage["input"] + self.token_usage["output"]
