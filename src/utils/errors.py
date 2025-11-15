"""커스텀 예외 클래스 정의"""


class CCWError(Exception):
    """CCW 시스템의 기본 예외 클래스"""

    pass


class ConfigurationError(CCWError):
    """설정 관련 예외"""

    pass


class AuthenticationError(CCWError):
    """인증 관련 예외"""

    pass


class TaskError(CCWError):
    """작업 실행 관련 예외"""

    pass


class TaskTimeoutError(TaskError):
    """작업 타임아웃 예외"""

    pass


class TaskAlreadyRunningError(TaskError):
    """이미 실행 중인 작업이 있을 때 발생하는 예외"""

    pass


class AgentError(CCWError):
    """에이전트 실행 관련 예외"""

    pass


class ToolError(CCWError):
    """도구 실행 관련 예외"""

    pass


class CommandBlockedError(ToolError):
    """파괴적 명령어가 차단되었을 때 발생하는 예외"""

    def __init__(self, command: str, reason: str):
        self.command = command
        self.reason = reason
        super().__init__(f"명령어가 차단되었습니다: {command}\n사유: {reason}")


class GitError(CCWError):
    """Git 작업 관련 예외"""

    pass


class GitHubError(CCWError):
    """GitHub API 관련 예외"""

    pass


class LogError(CCWError):
    """로그 작성/읽기 관련 예외"""

    pass
