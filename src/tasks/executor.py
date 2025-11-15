"""
작업 실행 관리

작업 실행 및 타임아웃 관리, TaskManager 싱글톤 제공
"""
import asyncio
from typing import Optional, Callable, Any
from src.models.task import Task, TaskStatus


class TaskManager:
    """
    작업 관리 싱글톤

    현재 실행 중인 작업을 추적하고 관리합니다.
    한 번에 하나의 작업만 실행되도록 보장합니다.
    """

    _current_task: Optional[Task] = None

    @classmethod
    def get_current_task(cls) -> Optional[Task]:
        """현재 실행 중인 작업을 반환합니다."""
        return cls._current_task

    @classmethod
    def set_current_task(cls, task: Task):
        """
        현재 작업을 설정합니다.

        Args:
            task: 설정할 작업

        Raises:
            RuntimeError: 이미 실행 중인 작업이 있는 경우
        """
        if cls._current_task and cls._current_task.is_running():
            raise RuntimeError(
                f"작업이 이미 진행 중입니다.\n"
                f"현재 작업: {cls._current_task.description}\n"
                f"작업 ID: {cls._current_task.id}"
            )

        cls._current_task = task

    @classmethod
    def clear_current_task(cls):
        """현재 작업을 클리어합니다."""
        cls._current_task = None

    @classmethod
    def has_running_task(cls) -> bool:
        """실행 중인 작업이 있는지 확인합니다."""
        return cls._current_task is not None and cls._current_task.is_running()


async def execute_task_with_timeout(
    task_func: Callable[[], Any], timeout_minutes: int = 30
) -> Any:
    """
    타임아웃이 설정된 작업을 실행합니다.

    Args:
        task_func: 실행할 비동기 함수
        timeout_minutes: 타임아웃 (분, 기본: 30)

    Returns:
        작업 실행 결과

    Raises:
        asyncio.TimeoutError: 타임아웃 발생 시
    """
    timeout_seconds = timeout_minutes * 60

    try:
        result = await asyncio.wait_for(task_func(), timeout=timeout_seconds)
        return result

    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(
            f"작업이 {timeout_minutes}분 타임아웃으로 종료되었습니다."
        )


async def handle_task_interruption():
    """
    서버 재시작 시 진행 중이던 작업을 처리합니다.

    현재 작업이 있으면 INTERRUPTED 상태로 변경하고 로그를 저장합니다.
    """
    current_task = TaskManager.get_current_task()

    if current_task and current_task.is_running():
        # 작업 중단 처리
        current_task.interrupt()

        # 로그 저장 (향후 구현)
        # await log_interrupted_task(current_task)

        # 클리어
        TaskManager.clear_current_task()
