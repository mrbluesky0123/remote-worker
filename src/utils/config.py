"""환경 변수 로드 및 검증 모듈"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .errors import ConfigurationError


class Config:
    """애플리케이션 설정 관리 클래스"""

    def __init__(self):
        """환경 변수를 로드하고 검증합니다."""
        # .env 파일 로드
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

        # 필수 환경 변수 검증
        self._validate_required_vars()

    def _validate_required_vars(self):
        """필수 환경 변수가 설정되어 있는지 검증합니다."""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_WHITELIST_USER_IDS",
            "ANTHROPIC_API_KEY",
            "GITHUB_TOKEN",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ConfigurationError(
                f"다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}\n"
                f".env 파일을 생성하고 필요한 값을 입력해주세요. "
                f"(.env.example 참조)"
            )

    @property
    def telegram_bot_token(self) -> str:
        """텔레그램 봇 토큰을 반환합니다."""
        return os.getenv("TELEGRAM_BOT_TOKEN", "")

    @property
    def telegram_whitelist_user_ids(self) -> list[int]:
        """화이트리스트 사용자 ID 목록을 반환합니다."""
        user_ids_str = os.getenv("TELEGRAM_WHITELIST_USER_IDS", "")
        if not user_ids_str:
            return []

        try:
            return [int(uid.strip()) for uid in user_ids_str.split(",")]
        except ValueError as e:
            raise ConfigurationError(
                f"TELEGRAM_WHITELIST_USER_IDS 형식이 올바르지 않습니다: {e}"
            )

    @property
    def anthropic_api_key(self) -> str:
        """Anthropic API 키를 반환합니다."""
        return os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def github_token(self) -> str:
        """GitHub Personal Access Token을 반환합니다."""
        return os.getenv("GITHUB_TOKEN", "")

    @property
    def task_timeout_minutes(self) -> int:
        """작업 타임아웃 시간(분)을 반환합니다. 기본값: 30분"""
        timeout_str = os.getenv("TASK_TIMEOUT_MINUTES", "30")
        try:
            return int(timeout_str)
        except ValueError:
            return 30

    @property
    def log_token_limit(self) -> int:
        """작업 로그 토큰 제한을 반환합니다. 기본값: 2000"""
        limit_str = os.getenv("LOG_TOKEN_LIMIT", "2000")
        try:
            return int(limit_str)
        except ValueError:
            return 2000


# 싱글톤 인스턴스
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """설정 인스턴스를 반환합니다 (싱글톤 패턴)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
