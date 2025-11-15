"""
파일 I/O 도구

파일 읽기, 쓰기, 편집 기능을 제공합니다.
"""
from pathlib import Path
from typing import Optional


def read_file(path: str, offset: int = 0, limit: Optional[int] = None) -> str:
    """
    파일 내용을 읽어옵니다.

    Args:
        path: 파일 경로
        offset: 시작 라인 번호 (기본: 0)
        limit: 읽을 라인 수 (기본: 전체)

    Returns:
        파일 내용 (라인 번호 포함, cat -n 형식)
    """
    file_path = Path(path)

    if not file_path.exists():
        return f"오류: 파일을 찾을 수 없습니다: {path}"

    if not file_path.is_file():
        return f"오류: {path}는 파일이 아닙니다"

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return f"오류: {path}는 텍스트 파일이 아닙니다 (바이너리 파일)"

    # 라인 범위 적용
    if limit:
        lines = lines[offset:offset + limit]
    else:
        lines = lines[offset:]

    # cat -n 형식으로 반환 (라인 번호 + 탭 + 내용)
    return "\n".join(f"{i+1+offset}\t{line}" for i, line in enumerate(lines))


def write_file(path: str, content: str, overwrite: bool = False) -> str:
    """
    새 파일을 생성합니다.

    Args:
        path: 파일 경로
        content: 파일 내용
        overwrite: 기존 파일 덮어쓰기 허용 (기본: False)

    Returns:
        작업 결과 메시지
    """
    file_path = Path(path)

    if file_path.exists() and not overwrite:
        return (
            f"경고: 파일이 이미 존재합니다: {path}\n"
            "edit_file 도구를 사용하거나 overwrite=True로 재시도하세요."
        )

    try:
        # 디렉토리 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 쓰기
        file_path.write_text(content, encoding="utf-8")

        return f"파일 생성 완료: {path}"

    except Exception as e:
        return f"오류: 파일 생성 실패: {e}"


def edit_file(
    path: str, old_string: str, new_string: str, replace_all: bool = False
) -> str:
    """
    기존 파일의 특정 문자열을 치환합니다.

    Args:
        path: 파일 경로
        old_string: 찾을 문자열 (정확히 일치해야 함)
        new_string: 바꿀 문자열
        replace_all: 모든 발생 치환 (기본: False, 고유해야 함)

    Returns:
        작업 결과 메시지
    """
    file_path = Path(path)

    if not file_path.exists():
        return f"오류: 파일을 찾을 수 없습니다: {path}"

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"오류: {path}는 텍스트 파일이 아닙니다"

    # 발생 횟수 확인
    count = content.count(old_string)

    if count == 0:
        return f"오류: '{old_string}'을 찾을 수 없습니다"

    if count > 1 and not replace_all:
        return (
            f"오류: '{old_string}'이 {count}번 발견되었습니다.\n"
            "replace_all=True를 사용하거나 더 구체적인 문자열을 지정하세요."
        )

    # 치환
    try:
        new_content = content.replace(old_string, new_string)
        file_path.write_text(new_content, encoding="utf-8")

        return f"파일 수정 완료: {count}개 치환됨"

    except Exception as e:
        return f"오류: 파일 수정 실패: {e}"
