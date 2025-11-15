"""
코드 검색 도구

Glob 패턴 매칭과 ripgrep 기반 코드 검색을 제공합니다.
"""
import subprocess
from pathlib import Path
from typing import Optional


def glob_files(pattern: str, path: str = ".") -> str:
    """
    파일 패턴으로 파일 목록을 검색합니다.

    Args:
        pattern: Glob 패턴 (예: **/*.py, src/**/*.ts)
        path: 검색 시작 디렉토리 (기본: 현재 디렉토리)

    Returns:
        매칭된 파일 경로 목록 (수정 시간 기준 역순 정렬)
    """
    base_path = Path(path)

    if not base_path.exists():
        return f"오류: 경로를 찾을 수 없습니다: {path}"

    try:
        # Glob 패턴 검색
        if "**" in pattern:
            files = base_path.glob(pattern)
        else:
            files = base_path.glob(pattern)

        # 수정 시간 기준 정렬 (최신 순)
        sorted_files = sorted(
            files, key=lambda x: x.stat().st_mtime, reverse=True
        )

        if not sorted_files:
            return f"패턴 '{pattern}'과 일치하는 파일이 없습니다"

        # 결과 반환
        return "\n".join(str(f) for f in sorted_files)

    except Exception as e:
        return f"오류: 검색 실패: {e}"


def grep(
    pattern: str,
    path: str = ".",
    output_mode: str = "files_with_matches",
    file_type: Optional[str] = None,
    case_insensitive: bool = False,
) -> str:
    """
    코드에서 패턴을 검색합니다 (ripgrep 기반).

    Args:
        pattern: 검색 패턴 (정규표현식)
        path: 검색 경로 (기본: 현재 디렉토리)
        output_mode: 출력 모드 (files_with_matches, content, count)
        file_type: 파일 타입 필터 (py, js, ts 등)
        case_insensitive: 대소문자 무시 (기본: False)

    Returns:
        검색 결과
    """
    cmd = ["rg"]

    # 출력 모드 설정
    if output_mode == "files_with_matches":
        cmd.append("-l")
    elif output_mode == "count":
        cmd.append("-c")
    # content 모드는 기본값

    # 대소문자 무시
    if case_insensitive:
        cmd.append("-i")

    # 파일 타입 필터
    if file_type:
        cmd.extend(["-t", file_type])

    # 패턴과 경로 추가
    cmd.extend([pattern, path])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )

        # ripgrep은 매칭 없으면 exit code 1 반환
        if result.returncode == 1 and not result.stdout:
            return f"패턴 '{pattern}'과 일치하는 항목이 없습니다"

        if result.returncode > 1:
            return f"오류: ripgrep 실행 실패:\n{result.stderr}"

        return result.stdout.strip()

    except FileNotFoundError:
        return (
            "오류: ripgrep(rg)이 설치되어 있지 않습니다.\n"
            "설치 방법: brew install ripgrep (macOS) 또는 apt install ripgrep (Linux)"
        )
    except subprocess.TimeoutExpired:
        return "오류: 검색 타임아웃 (30초 초과)"
    except Exception as e:
        return f"오류: 검색 실패: {e}"
