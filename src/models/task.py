"""
작업 모델

Task, TaskStatus, AgentType 정의
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


class TaskStatus(Enum):
    """작업 상태"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INTERRUPTED = "interrupted"


class AgentType(Enum):
    """에이전트 타입"""

    MAIN = "main"  # 메인 에이전트 (Sonnet): 모든 핵심 작업
    LOGGER = "logger"  # 로거 에이전트 (Haiku): 로그 생성


@dataclass
class Task:
    """
    작업 모델

    사용자가 텔레그램을 통해 요청한 개발 작업을 나타냅니다.
    """

    user_id: int
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: datetime = field(init=False)
    agent_type: AgentType = AgentType.MAIN
    context: dict = field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        """초기화 후 타임아웃 시각 설정 (생성 시각 + 30분)"""
        self.timeout_at = self.created_at + timedelta(minutes=30)

    def start(self):
        """작업을 시작합니다."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, result: str):
        """작업을 완료합니다."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def fail(self, error: str):
        """작업을 실패 처리합니다."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error

    def timeout(self):
        """작업을 타임아웃 처리합니다."""
        self.status = TaskStatus.TIMEOUT
        self.completed_at = datetime.now()
        self.error = "작업이 30분 타임아웃으로 종료되었습니다."

    def interrupt(self):
        """작업을 중단 처리합니다 (서버 재시작 등)."""
        self.status = TaskStatus.INTERRUPTED
        self.completed_at = datetime.now()
        self.error = "작업이 서버 재시작으로 중단되었습니다."

    def is_timed_out(self) -> bool:
        """타임아웃 여부를 확인합니다."""
        return datetime.now() >= self.timeout_at

    def is_running(self) -> bool:
        """실행 중 여부를 확인합니다."""
        return self.status == TaskStatus.RUNNING

    def is_completed(self) -> bool:
        """완료 여부를 확인합니다."""
        return self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.TIMEOUT,
            TaskStatus.INTERRUPTED,
        )
