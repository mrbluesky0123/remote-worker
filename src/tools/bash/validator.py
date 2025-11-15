"""
명령어 검증 도구

파괴적 명령과 대화형 명령을 차단합니다.
"""
from typing import Tuple


# 파괴적 명령 블랙리스트
DESTRUCTIVE_COMMANDS = [
    "rm",
    "rmdir",
    "mkfs",
    "dd",
    "format",
    "fdisk",
    "parted",
    ":(){:|:&};:",  # Fork bomb
]

# 대화형 명령 블랙리스트
INTERACTIVE_COMMANDS = [
    "vi",
    "vim",
    "nvim",
    "nano",
    "emacs",
    "less",
    "more",
    "top",
    "htop",
    "sudo",  # 대화형 비밀번호 입력
]

# 보호된 경로 (쓰기 차단)
PROTECTED_PATHS = [
    "/etc/",
    "/sys/",
    "/proc/",
    "/boot/",
    "/dev/",
]


def is_safe_command(command: str) -> Tuple[bool, str]:
    """
    명령어의 안전성을 검증합니다.

    Args:
        command: 검증할 명령어

    Returns:
        (안전 여부, 차단 사유)
    """
    if not command or not command.strip():
        return False, "빈 명령어"

    # 명령어 파싱
    parts = command.split()
    if not parts:
        return False, "빈 명령어"

    cmd = parts[0]

    # 파괴적 명령 체크
    for destructive in DESTRUCTIVE_COMMANDS:
        if cmd == destructive or cmd.endswith(f"/{destructive}"):
            return (
                False,
                f"파괴적 명령어 '{destructive}'는 실행할 수 없습니다.",
            )

    # 대화형 명령 체크
    for interactive in INTERACTIVE_COMMANDS:
        if cmd == interactive or cmd.endswith(f"/{interactive}"):
            return (
                False,
                f"대화형 명령어 '{interactive}'는 지원되지 않습니다.",
            )

    # 보호된 경로 쓰기 체크
    for protected_path in PROTECTED_PATHS:
        if protected_path in command and (
            ">" in command or "tee" in command or "echo" in command
        ):
            return (
                False,
                f"시스템 경로 '{protected_path}'에 쓰기를 시도할 수 없습니다.",
            )

    # rm -rf 특별 체크
    if "rm" in command and "-rf" in command:
        return False, "rm -rf 명령은 매우 위험하여 차단되었습니다."

    # / 경로 대상 작업 체크
    if cmd in ["chmod", "chown", "chgrp"] and " / " in command:
        return False, f"{cmd} 명령을 루트 경로(/)에 실행할 수 없습니다."

    return True, ""
