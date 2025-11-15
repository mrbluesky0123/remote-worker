"""
작업 로그 모델

TaskLog 모델 및 시간 기반 마크다운 변환
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import uuid


@dataclass
class TaskLog:
    """
    작업 로그 모델

    작업 완료 후 생성되는 마크다운 문서입니다.
    파일명: YYYY-MM-DD-HHmmss.md (예: 2025-11-15-143022.md)
    """

    task_id: str
    task_request: str
    work_summary: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    decisions: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    token_count: int = 0

    def get_file_path(self, log_dir: str = ".ccw/logs") -> Path:
        """
        로그 파일 경로를 반환합니다.

        파일명 형식: YYYY-MM-DD-HHmmss.md

        Args:
            log_dir: 로그 디렉토리 경로

        Returns:
            로그 파일 경로
        """
        filename = self.created_at.strftime("%Y-%m-%d-%H%M%S.md")
        return Path(log_dir) / filename

    def to_markdown(self) -> str:
        """
        마크다운 형식으로 변환합니다.

        Returns:
            마크다운 문자열
        """
        lines = ["# 작업 로그\n"]

        # 메타 정보
        lines.append(f"**일시**: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**작업 요청**: \"{self.task_request}\"")
        lines.append(f"**작업 ID**: `{self.task_id}`\n")

        # 수행한 작업
        lines.append("## 수행한 작업\n")
        lines.append(self.work_summary)
        lines.append("")

        # 결정 사항
        lines.append("## 결정 사항\n")
        if self.decisions:
            for decision in self.decisions:
                lines.append(f"- {decision}")
        else:
            lines.append("- 없음")
        lines.append("")

        # 발생한 이슈
        lines.append("## 발생한 이슈\n")
        if self.issues:
            for issue in self.issues:
                lines.append(f"- {issue}")
        else:
            lines.append("- 없음")
        lines.append("")

        # 다음 작업 참고사항
        lines.append("## 다음 작업 참고사항\n")
        if self.notes:
            for note in self.notes:
                lines.append(f"- {note}")
        else:
            lines.append("- 없음")

        return "\n".join(lines)

    def save(self, log_dir: str = ".ccw/logs"):
        """
        로그를 파일로 저장합니다.

        Args:
            log_dir: 로그 디렉토리 경로
        """
        file_path = self.get_file_path(log_dir)

        # 디렉토리 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 마크다운 생성
        content = self.to_markdown()

        # 토큰 수 추정 (대략 4글자 = 1토큰)
        self.token_count = len(content) // 4

        # 파일 쓰기
        file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def load(file_path: Path) -> Optional["TaskLog"]:
        """
        파일에서 로그를 읽어옵니다.

        Args:
            file_path: 로그 파일 경로

        Returns:
            TaskLog 객체 또는 None
        """
        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8")

        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        lines = content.split("\n")

        # 메타 정보 추출 (TODO: 정규표현식으로 개선)
        task_request = ""
        task_id = ""

        for line in lines:
            if line.startswith("**작업 요청**:"):
                task_request = line.split('": "')[1].rstrip('"')
            elif line.startswith("**작업 ID**:"):
                task_id = line.split(": `")[1].rstrip("`")

        return TaskLog(
            task_id=task_id,
            task_request=task_request,
            work_summary=content,  # 전체 내용을 요약으로 사용
        )

    @staticmethod
    def load_recent(log_dir: str = ".ccw/logs", count: int = 2) -> List[str]:
        """
        최근 N개의 로그 파일 내용을 읽어옵니다.

        Args:
            log_dir: 로그 디렉토리 경로
            count: 읽을 로그 개수

        Returns:
            로그 내용 문자열 목록
        """
        log_path = Path(log_dir)

        if not log_path.exists():
            return []

        # 수정 시간 기준 정렬 (최신 순)
        log_files = sorted(
            log_path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True
        )

        logs = []
        for log_file in log_files[:count]:
            content = log_file.read_text(encoding="utf-8")

            # 토큰 제한 (로그당 최대 2000토큰 = 약 8000글자)
            max_chars = 8000
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n...(생략)"

            logs.append(content)

        return logs
