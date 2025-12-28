"""
텔레그램 봇 초기화 및 관리

봇 애플리케이션 생성, 핸들러 등록, 폴링 시작을 담당합니다.
"""
import os
import telegram.ext as tg_ext
from src.bot.handlers import (
    start_command,
    hello_command,
    help_command,
    task_command,
)


def create_application() -> tg_ext.Application:
    """
    텔레그램 봇 애플리케이션을 생성하고 핸들러를 등록합니다.

    Returns:
        설정된 Application 객체
    """
    # 봇 토큰 가져오기
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다.\n"
            ".env 파일을 확인하세요."
        )

    # Application 생성
    app = tg_ext.Application.builder().token(token).build()

    # 명령어 핸들러 등록
    app.add_handler(tg_ext.CommandHandler("start", start_command))
    app.add_handler(tg_ext.CommandHandler("hello", hello_command))
    app.add_handler(tg_ext.CommandHandler("help", help_command))
    app.add_handler(tg_ext.CommandHandler("task", task_command))

    # 향후 추가할 핸들러:
    # app.add_handler(CommandHandler("diff", diff_command))
    # app.add_handler(CommandHandler("commit", commit_command))
    # app.add_handler(CommandHandler("branch", branch_command))
    # app.add_handler(CommandHandler("mr", mr_command))
    # app.add_handler(CommandHandler("exec", exec_command))
    # app.add_handler(CommandHandler("logs", logs_command))

    return app


async def run_bot():
    """
    봇을 시작하고 폴링을 실행합니다.
    """
    app = create_application()

    print("🤖 텔레그램 봇을 시작합니다...")
    print(f"✅ 핸들러 등록 완료: {len(app.handlers[0])}개")

    # 수동으로 초기화 및 폴링 시작
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=["message", "edited_message"])

    # 종료 대기 (Ctrl+C까지)
    try:
        import asyncio
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
