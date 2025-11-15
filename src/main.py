"""
애플리케이션 메인 진입점

텔레그램 봇을 시작하고 환경 변수를 검증합니다.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def validate_environment():
    """
    필수 환경 변수를 검증합니다.

    Raises:
        SystemExit: 필수 환경 변수가 누락된 경우
    """
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_WHITELIST_USER_IDS",
        "ANTHROPIC_API_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("❌ 필수 환경 변수가 누락되었습니다:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n.env 파일을 확인하세요. 예시는 .env.example을 참고하세요.")
        sys.exit(1)

    # 화이트리스트 사용자 ID 검증
    whitelist = os.environ.get("TELEGRAM_WHITELIST_USER_IDS", "")
    try:
        user_ids = [int(uid.strip()) for uid in whitelist.split(",") if uid.strip()]
        if not user_ids:
            print("⚠️  경고: TELEGRAM_WHITELIST_USER_IDS가 비어있습니다.")
            print("   모든 사용자가 차단됩니다.")
    except ValueError:
        print("❌ TELEGRAM_WHITELIST_USER_IDS 형식이 올바르지 않습니다.")
        print("   쉼표로 구분된 숫자 목록이어야 합니다 (예: 123456789,987654321)")
        sys.exit(1)


def setup_logging():
    """
    로깅을 설정합니다.
    """
    import logging
    from src.constants import APP_LOG_FILE

    # 로그 디렉토리 생성
    log_file = Path(APP_LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(APP_LOG_FILE),
            logging.StreamHandler(),
        ],
    )


async def main():
    """
    메인 함수

    환경 변수를 로드하고 텔레그램 봇을 시작합니다.
    """
    # 환경 변수 로드
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✅ .env 파일을 로드했습니다.")
    else:
        print("⚠️  .env 파일이 없습니다. 환경 변수가 설정되어 있는지 확인하세요.")

    # 환경 변수 검증
    validate_environment()

    # 로깅 설정
    setup_logging()

    # 서버 재시작 시 중단된 작업 처리
    from src.tasks import handle_task_interruption

    await handle_task_interruption()

    # 텔레그램 봇 시작
    from src.telegram import run_bot

    print("\n" + "=" * 60)
    print(" Claude Code Worker (CCW)")
    print("=" * 60)
    print()

    try:
        await run_bot()
    except KeyboardInterrupt:
        print("\n\n⏸️  봇을 종료합니다...")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
