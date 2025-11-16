"""
작업 컨텍스트 관리 모듈

새 작업 시작 전 마지막 2개 작업 로그를 읽어 컨텍스트를 유지합니다.
"""

from pathlib import Path
from typing import List

from src.constants import LOG_DIRECTORY, MAX_CONTEXT_LOGS, LOG_TOKEN_LIMIT


class TaskContext:
    """작업 세션 컨텍스트 관리 클래스"""

    @staticmethod
    async def load_recent_logs(count: int = MAX_CONTEXT_LOGS) -> List[str]:
        """
        최신 N개의 작업 로그를 로드합니다.

        Args:
            count: 로드할 로그 개수 (기본값: 2)

        Returns:
            로그 내용 리스트 (최신순)
        """
        log_dir = Path(LOG_DIRECTORY)

        if not log_dir.exists():
            return []

        # 시간 기반 로그 파일 패턴: YYYY-MM-DD-HHmmss.md
        log_files = sorted(
            log_dir.glob("*.md"),
            key=lambda x: x.stat().st_mtime,
            reverse=True  # 최신순
        )

        logs = []
        for log_file in log_files[:count]:
            content = log_file.read_text(encoding="utf-8")

            # 토큰 제한 적용 (로그당 LOG_TOKEN_LIMIT)
            content = TaskContext._truncate_to_token_limit(content, LOG_TOKEN_LIMIT)

            logs.append(content)

        return logs

    @staticmethod
    def _truncate_to_token_limit(content: str, max_tokens: int) -> str:
        """
        로그 내용을 토큰 제한에 맞게 자릅니다.

        Args:
            content: 원본 로그 내용
            max_tokens: 최대 토큰 수

        Returns:
            잘린 로그 내용
        """
        # 대략적인 토큰 추정: 4글자 = 1토큰
        max_chars = max_tokens * 4

        if len(content) <= max_chars:
            return content

        # 토큰 제한 초과 시 잘라내고 표시
        truncated = content[:max_chars]
        return f"{truncated}\n\n...(로그가 {max_tokens} 토큰 제한으로 잘렸습니다)"

    @staticmethod
    def format_context_for_prompt(logs: List[str]) -> str:
        """
        로그 리스트를 프롬프트용 컨텍스트 문자열로 변환합니다.

        Args:
            logs: 작업 로그 리스트

        Returns:
            프롬프트에 삽입할 컨텍스트 문자열
        """
        if not logs:
            return ""

        context_parts = [
            "# 이전 작업 컨텍스트",
            "",
            "다음은 최근 작업 세션 로그입니다. 이 정보를 참고하여 작업을 수행하세요:",
            ""
        ]

        for i, log in enumerate(logs, 1):
            context_parts.append(f"## 이전 작업 {i}")
            context_parts.append("")
            context_parts.append(log)
            context_parts.append("")
            context_parts.append("---")
            context_parts.append("")

        return "\n".join(context_parts)
