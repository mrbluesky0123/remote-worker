"""
텔레그램 명령어 핸들러

사용자 명령을 처리하고 에이전트를 실행합니다.
"""
import asyncio
import os
from telegram import Update
from telegram.ext import ContextTypes
from anthropic import Anthropic

from src.telegram.auth import verify_user
from src.models.task import Task, TaskStatus
from src.tasks.executor import TaskManager, execute_task_with_timeout
from src.agents.main.executor import MainAgent


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
    user_id = update.effective_user.id

    # T037: 작업 진행 중 체크
    if TaskManager.has_running_task():
        current_task = TaskManager.get_current_task()
        await update.message.reply_text(
            f"⚠️ 작업이 이미 진행 중입니다.\n\n"
            f"**현재 작업**: {current_task.description}\n"
            f"**작업 ID**: {current_task.id}\n"
            f"**시작 시각**: {current_task.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"현재 작업이 완료될 때까지 기다려주세요."
        )
        return

    # Task 생성
    task = Task(user_id=user_id, description=task_description)

    # 즉시 확인 메시지
    await update.message.reply_text(
        f"✅ 작업을 시작합니다.\n\n"
        f"**작업 ID**: {task.id}\n"
        f"**설명**: {task_description}\n"
        f"**예상 완료**: 30분 이내\n\n"
        f"⏳ 처리 중..."
    )

    # TaskManager에 등록
    try:
        TaskManager.set_current_task(task)
        task.start()
    except RuntimeError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        return

    # 메인 에이전트 실행
    try:
        # Anthropic 클라이언트 생성
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")

        client = Anthropic(api_key=api_key)
        agent = MainAgent(client)

        # 작업 컨텍스트 준비 (추후 로그 로딩 추가)
        task_context = {
            "recent_logs": [],  # TODO: Phase 4에서 로그 로딩 구현
        }

        # 타임아웃이 설정된 작업 실행
        async def run_agent():
            return await agent.execute(task_description, task_context)

        result = await execute_task_with_timeout(run_agent, timeout_minutes=30)

        # 작업 완료 처리
        task.complete(result)

        # T038: 작업 완료 알림
        await update.message.reply_text(
            f"✅ 작업이 완료되었습니다!\n\n"
            f"**작업 ID**: {task.id}\n"
            f"**소요 시간**: {(task.completed_at - task.started_at).total_seconds() / 60:.1f}분\n\n"
            f"**결과**:\n{result}"
        )

    except asyncio.TimeoutError:
        # 타임아웃 처리
        task.timeout()
        await update.message.reply_text(
            f"⏱️ 작업이 타임아웃되었습니다.\n\n"
            f"**작업 ID**: {task.id}\n"
            f"**경과 시간**: 30분\n\n"
            f"작업이 복잡하여 30분 내에 완료되지 않았습니다.\n"
            f"작업을 더 작은 단위로 나누어 다시 시도해주세요."
        )

    except Exception as e:
        # 오류 처리
        task.fail(str(e))
        await update.message.reply_text(
            f"❌ 작업 실행 중 오류가 발생했습니다.\n\n"
            f"**작업 ID**: {task.id}\n"
            f"**오류**: {str(e)}\n\n"
            f"문제 해결 후 다시 시도해주세요."
        )

    finally:
        # TaskManager 클리어
        TaskManager.clear_current_task()
