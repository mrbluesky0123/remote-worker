"""
Bash 명령 실행 도구

터미널 명령 실행 및 백그라운드 프로세스 관리를 제공합니다.
"""
import asyncio
from typing import Dict, Any, Optional

# 백그라운드 프로세스 저장소
BACKGROUND_PROCESSES: Dict[str, asyncio.subprocess.Process] = {}


async def bash(
    command: str, timeout: int = 120, run_in_background: bool = False
) -> str:
    """
    터미널 명령을 실행합니다.

    Args:
        command: 실행할 명령어
        timeout: 타임아웃 (초, 기본: 120)
        run_in_background: 백그라운드 실행 여부

    Returns:
        실행 결과 (stdout, stderr, exit_code) 또는 bash_id
    """
    from src.tools.bash.validator import is_safe_command

    # 명령어 검증
    is_safe, reason = is_safe_command(command)
    if not is_safe:
        return f"오류: 차단된 명령어입니다.\n사유: {reason}"

    try:
        if run_in_background:
            # 백그라운드 프로세스 시작
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            bash_id = str(id(proc))
            BACKGROUND_PROCESSES[bash_id] = proc

            return (
                f"백그라운드 프로세스 시작\n"
                f"bash_id: {bash_id}\n"
                f"bash_output 도구로 출력을 확인하세요."
            )

        # 동기 실행
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )

        result_lines = [f"명령어: {command}"]

        if stdout:
            result_lines.append(f"\n[stdout]\n{stdout.decode()}")

        if stderr:
            result_lines.append(f"\n[stderr]\n{stderr.decode()}")

        result_lines.append(f"\nexit_code: {proc.returncode}")

        return "\n".join(result_lines)

    except asyncio.TimeoutError:
        if proc:
            proc.kill()
        return f"오류: 명령어 타임아웃 ({timeout}초 초과)"

    except Exception as e:
        return f"오류: 명령 실행 실패: {e}"


async def bash_output(
    bash_id: str, filter_regex: Optional[str] = None
) -> str:
    """
    백그라운드 실행 중인 명령의 출력을 확인합니다.

    Args:
        bash_id: 백그라운드 프로세스 ID
        filter_regex: 출력 필터 (정규표현식, 선택적)

    Returns:
        새로운 출력 내용 및 프로세스 상태
    """
    if bash_id not in BACKGROUND_PROCESSES:
        return f"오류: 프로세스를 찾을 수 없습니다: {bash_id}"

    proc = BACKGROUND_PROCESSES[bash_id]

    try:
        # 프로세스 상태 확인
        if proc.returncode is not None:
            status = "completed"
        else:
            status = "running"

        # 출력 읽기 (넌블로킹)
        stdout_data = ""
        stderr_data = ""

        if proc.stdout:
            try:
                stdout_bytes = await asyncio.wait_for(
                    proc.stdout.read(8192), timeout=0.1
                )
                stdout_data = stdout_bytes.decode()
            except asyncio.TimeoutError:
                pass

        if proc.stderr:
            try:
                stderr_bytes = await asyncio.wait_for(
                    proc.stderr.read(8192), timeout=0.1
                )
                stderr_data = stderr_bytes.decode()
            except asyncio.TimeoutError:
                pass

        result_lines = [f"bash_id: {bash_id}", f"상태: {status}"]

        if stdout_data:
            result_lines.append(f"\n[stdout]\n{stdout_data}")

        if stderr_data:
            result_lines.append(f"\n[stderr]\n{stderr_data}")

        if not stdout_data and not stderr_data:
            result_lines.append("\n(새 출력 없음)")

        # 완료된 프로세스는 제거
        if status == "completed":
            del BACKGROUND_PROCESSES[bash_id]
            result_lines.append(f"\nexit_code: {proc.returncode}")

        return "\n".join(result_lines)

    except Exception as e:
        return f"오류: 출력 확인 실패: {e}"
