"""
텔레그램 명령어 핸들러

사용자 명령을 처리하고 에이전트를 실행합니다.
"""
from telegram import Update
from telegram.ext import ContextTypes
from src.telegram.auth import verify_user


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start 명령 핸들러

    봇 사용법을 안내합니다.
    """
    if not await verify_user(update):
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    await update.message.reply_text(
        f"👋 안녕하세요! Claude Code Worker입니다.\n\n"
        f"**사용자 ID**: `{user_id}`\n\n"
        f"**사용 가능한 명령어**:\n"
        f"/help - 도움말 보기\n"
        f"/task [작업 설명] - 개발 작업 실행\n\n"
        f"예: /task main.py에 주석 추가"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help 명령 핸들러

    상세한 도움말을 제공합니다.
    """
    if not await verify_user(update):
        return

    if not update.message:
        return

    help_text = """
📖 **Claude Code Worker 도움말**

**핵심 명령어**:
• `/task [작업]` - 개발 작업 실행
  예: /task main.py에 로깅 추가

**버전 관리** (Phase 6):
• `/diff` - 변경사항 확인
• `/commit [메시지]` - Git 커밋
• `/branch [이름]` - 새 브랜치 생성
• `/mr [제목]` - GitHub Pull Request 생성

**서버 관리** (Phase 7):
• `/exec [명령]` - 서버 명령 실행
  예: /exec ls -la

**로그 조회** (Phase 8):
• `/logs` - 최근 작업 로그 조회

**참고사항**:
• 한 번에 하나의 작업만 실행 가능
• 작업 타임아웃: 30분
• 모든 작업은 자동으로 로그 기록

문의: GitHub Issues
    """

    await update.message.reply_text(help_text)


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /task 명령 핸들러

    개발 작업을 실행합니다.

    사용법: /task [작업 설명]
    """
    if not await verify_user(update):
        return

    if not update.message:
        return

    # 작업 설명 추출
    if not context.args:
        await update.message.reply_text(
            "❌ 작업 설명이 필요합니다.\n\n"
            "사용법: /task [작업 설명]\n"
            "예: /task main.py에 주석 추가"
        )
        return

    task_description = " ".join(context.args)

    # 즉시 확인 메시지
    await update.message.reply_text(
        f"✅ 작업을 시작합니다...\n\n"
        f"**작업**: {task_description}\n\n"
        f"⏳ 처리 중... (최대 30분)"
    )

    # TODO: 메인 에이전트 실행 (Phase 3에서 구현)
    # result = await execute_main_agent(task_description)
    # await update.message.reply_text(f"✅ 완료:\n\n{result}")

    # 임시 응답
    await update.message.reply_text(
        "⚠️ 메인 에이전트가 아직 구현되지 않았습니다.\n"
        "Phase 3에서 구현될 예정입니다."
    )
