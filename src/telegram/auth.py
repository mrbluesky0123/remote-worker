"""
텔레그램 사용자 인증

환경 변수 기반 화이트리스트 검증을 제공합니다.
"""
import os
from typing import Set
from telegram import Update


def get_allowed_user_ids() -> Set[int]:
    """
    환경 변수에서 허용된 사용자 ID 목록을 가져옵니다.

    Returns:
        허용된 사용자 ID 집합
    """
    whitelist_str = os.environ.get("TELEGRAM_WHITELIST_USER_IDS", "")

    if not whitelist_str:
        return set()

    try:
        user_ids = [int(uid.strip()) for uid in whitelist_str.split(",") if uid.strip()]
        return set(user_ids)
    except ValueError as e:
        print(f"경고: TELEGRAM_WHITELIST_USER_IDS 파싱 실패: {e}")
        return set()


# 전역 화이트리스트 (애플리케이션 시작 시 로드)
ALLOWED_USER_IDS: Set[int] = get_allowed_user_ids()


async def verify_user(update: Update) -> bool:
    """
    사용자가 화이트리스트에 포함되어 있는지 확인합니다.

    Args:
        update: 텔레그램 업데이트 객체

    Returns:
        인증 성공 여부
    """
    if not update.effective_user:
        return False

    user_id = update.effective_user.id

    if user_id not in ALLOWED_USER_IDS:
        if update.message:
            await update.message.reply_text(
                "⛔ 권한이 없습니다.\n\n"
                f"사용자 ID: {user_id}\n"
                "이 ID를 TELEGRAM_WHITELIST_USER_IDS에 추가하세요."
            )
        return False

    return True


def is_authorized(user_id: int) -> bool:
    """
    사용자 ID가 화이트리스트에 포함되어 있는지 확인합니다.

    Args:
        user_id: 텔레그램 사용자 ID

    Returns:
        인증 여부
    """
    return user_id in ALLOWED_USER_IDS
