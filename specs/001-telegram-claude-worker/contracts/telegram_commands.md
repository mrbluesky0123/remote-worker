# 텔레그램 명령어 스키마

**기능**: 001-telegram-claude-worker
**날짜**: 2025-11-08
**버전**: 1.0.0

## 개요

이 문서는 CCW 텔레그램 봇이 지원하는 모든 명령어의 구문, 파라미터, 응답 형식을 정의합니다.

## 명령어 목록

### 1. /task - 새 작업 시작

**설명**: 새로운 개발 작업을 시작합니다.

**구문**:
```
/task <작업 내용>
```

**파라미터**:
- `<작업 내용>`: 수행할 작업에 대한 자연어 설명 (필수)

**예시**:
```
/task main.py에 비동기 로깅 기능 추가
/task 사용자 인증 버그 수정
/task README.md 업데이트
```

**응답**:

**즉시 응답** (5초 이내):
```
✅ 작업을 시작합니다.

작업 ID: abc-123
설명: main.py에 비동기 로깅 기능 추가
예상 완료: 30분 이내
```

**작업 진행 중 응답** (다른 작업 요청 시):
```
⚠️ 작업이 이미 진행 중입니다.

현재 작업: main.py에 비동기 로깅 기능 추가
작업 ID: abc-123
시작 시각: 2025-11-08 10:30:00
예상 완료: 2025-11-08 11:00:00

현재 작업이 완료될 때까지 기다려주세요.
```

**완료 응답** (작업 완료 시):
```
✅ 작업이 완료되었습니다!

작업 ID: abc-123
소요 시간: 15분

**수행한 작업**:
- src/utils/logger.py 생성
- asyncio 기반 로깅 구현
- tests/unit/test_logger.py 추가

**변경된 파일**:
- src/utils/logger.py (신규)
- src/main.py (수정)
- tests/unit/test_logger.py (신규)

**다음 단계**:
- /diff 명령으로 변경사항 확인
- /commit 명령으로 커밋
```

**오류 응답**:
```
❌ 작업 실행 중 오류가 발생했습니다.

오류 타입: ImportError
메시지: No module named 'asyncio_logger'

원인: asyncio_logger 패키지가 설치되지 않았습니다.

해결 방법:
1. requirements.txt에 asyncio-logger 추가
2. uv sync 실행

작업이 중단되었습니다. 문제 해결 후 다시 시도해주세요.
```

**타임아웃 응답** (30분 초과 시):
```
⏱️ 작업이 타임아웃되었습니다.

작업 ID: abc-123
경과 시간: 30분

작업이 복잡하여 30분 내에 완료되지 않았습니다.
작업을 더 작은 단위로 나누어 다시 시도해주세요.

부분 결과는 로그에 저장되었습니다: .ccw/logs/feature-logging.md
```

---

### 2. /diff - 변경사항 확인 및 커밋 메시지 생성

**설명**: 마지막 커밋과 현재 작업 디렉토리의 차이를 확인하고 커밋 메시지를 생성합니다.

**구문**:
```
/diff [from_ref] [to_ref]
```

**파라미터**:
- `[from_ref]`: 비교 시작 참조 (기본값: HEAD~1, 선택)
- `[to_ref]`: 비교 끝 참조 (기본값: HEAD, 선택)

**예시**:
```
/diff
/diff HEAD~3 HEAD
/diff main feature-logging
```

**응답**:
```
📊 변경사항 요약

**비교**: HEAD~1...HEAD
**변경된 파일**: 3개

**추가**:
- src/utils/logger.py (+45 lines)
- tests/unit/test_logger.py (+78 lines)

**수정**:
- src/main.py (+12, -3 lines)

**제안 커밋 메시지**:
```
feat: Add async logging functionality

- Implement asyncio-based logger in src/utils/logger.py
- Integrate logger in main.py
- Add unit tests for logging module

Related to: feature-logging
```

이 메시지로 커밋하려면: /commit feat: Add async logging functionality
```

---

### 3. /commit - 변경사항 커밋

**설명**: 현재 변경사항을 Git에 커밋합니다.

**구문**:
```
/commit <커밋 메시지>
```

**파라미터**:
- `<커밋 메시지>`: 커밋 메시지 (필수)

**예시**:
```
/commit feat: Add async logging functionality
/commit fix: Resolve authentication bug
/commit docs: Update README with new instructions
```

**응답**:
```
✅ 커밋이 완료되었습니다.

커밋 SHA: a1b2c3d4
브랜치: feature-logging
메시지: feat: Add async logging functionality

**커밋된 파일**:
- src/utils/logger.py
- src/main.py
- tests/unit/test_logger.py

**다음 단계**:
- /mr 명령으로 Merge Request 생성
```

**오류 응답** (변경사항 없음):
```
⚠️ 커밋할 변경사항이 없습니다.

작업 디렉토리가 깨끗합니다.
변경사항을 먼저 생성해주세요.
```

---

### 4. /exec - 서버 명령어 실행

**설명**: 안전한 서버 명령어를 실행합니다.

**구문**:
```
/exec <명령어>
```

**파라미터**:
- `<명령어>`: 실행할 명령어 (필수)

**예시**:
```
/exec ls -la
/exec cat src/main.py
/exec grep "TODO" src/**/*.py
/exec df -h
```

**응답 (성공)**:
```
✅ 명령어 실행 완료

**명령어**: ls -la
**종료 코드**: 0
**실행 시간**: 45ms

**출력**:
```
total 24
drwxr-xr-x  5 randy randy 4096 Nov  8 10:30 .
drwxr-xr-x 15 randy randy 4096 Nov  8 09:00 ..
-rw-r--r--  1 randy randy  123 Nov  8 10:30 main.py
-rw-r--r--  1 randy randy  456 Nov  8 10:25 README.md
```
```

**응답 (차단)**:
```
🚫 명령어가 차단되었습니다.

**명령어**: rm -rf /tmp/test
**차단 사유**: 파괴적 명령어 'rm'는 실행할 수 없습니다.

**대안**:
파일을 삭제하려면:
1. 먼저 'ls /tmp/test'로 내용 확인
2. 삭제 대상을 구체적으로 지정
3. 텔레그램으로 명시적 삭제 요청

안전을 위해 자동 삭제는 지원하지 않습니다.
```

**응답 (대화형 명령 차단)**:
```
🚫 명령어가 차단되었습니다.

**명령어**: vi config.txt
**차단 사유**: 대화형 명령어 'vi'는 지원되지 않습니다.

**대안**:
파일 내용을 보려면:
- cat config.txt
- head -n 20 config.txt
- tail -n 20 config.txt

파일을 수정하려면:
- /task "config.txt의 특정 부분 수정" 명령 사용
```

---

### 5. /logs - 작업 로그 확인

**설명**: 최근 작업 로그를 확인합니다.

**구문**:
```
/logs [개수]
```

**파라미터**:
- `[개수]`: 확인할 로그 개수 (기본값: 2, 선택)

**예시**:
```
/logs
/logs 5
/logs 1
```

**응답**:
```
📝 최근 작업 로그 (2개)

---

## 1. feature-logging

**최종 업데이트**: 2025-11-08 10:45:00
**작업**: 비동기 로깅 기능 추가

**요약**:
asyncio 기반 로깅 모듈을 구현했습니다. RotatingFileHandler를 사용하여 로그 파일 크기를 관리합니다.

**내린 결정**:
- asyncio-logger 대신 내장 logging 모듈 사용 (의존성 최소화)

**발생한 이슈**:
- 비동기 파일 쓰기 시 경쟁 조건 → asyncio.Lock 사용하여 해결

---

## 2. bug-auth

**최종 업데이트**: 2025-11-07 16:20:00
**작업**: 사용자 인증 버그 수정

**요약**:
화이트리스트 검증 로직의 타입 불일치 오류를 수정했습니다.

**내린 결정**:
- 환경 변수를 int로 명시적 변환

**발생한 이슈**:
- str과 int 비교로 인한 인증 실패 → 타입 변환 추가

---

전체 로그: .ccw/logs/
```

---

### 6. /mr - Merge Request 생성

**설명**: 현재 브랜치의 변경사항으로 GitHub Merge Request(Pull Request)를 생성합니다.

**구문**:
```
/mr [target_branch]
```

**파라미터**:
- `[target_branch]`: 타겟 브랜치 (기본값: main, 선택)

**예시**:
```
/mr
/mr develop
/mr main
```

**응답**:
```
✅ Merge Request가 생성되었습니다.

**제목**: feat: Add async logging functionality
**소스 브랜치**: feature-logging
**타겟 브랜치**: main

**설명**:
## 요약
- 비동기 로깅 기능 구현
- asyncio 기반 파일 쓰기
- 단위 테스트 추가

## 변경사항
- src/utils/logger.py (신규)
- src/main.py (수정)
- tests/unit/test_logger.py (신규)

**링크**: https://github.com/owner/repo/pull/123

Merge Request를 검토하고 승인해주세요.
```

**오류 응답** (GitHub 인증 실패):
```
❌ Merge Request 생성 실패

오류: GitHub 인증 실패
상태 코드: 401

원인:
GitHub Personal Access Token이 만료되었거나 권한이 부족합니다.

해결 방법:
1. GitHub에서 새 PAT 생성
2. 환경 변수 GITHUB_TOKEN 업데이트
3. CCW 재시작
```

---

### 7. /branch - 새 브랜치 생성

**설명**: 새로운 Git 브랜치를 생성하고 전환합니다.

**구문**:
```
/branch <base_branch> <new_branch>
```

**파라미터**:
- `<base_branch>`: 기준 브랜치 (필수)
- `<new_branch>`: 새 브랜치명 (필수)

**예시**:
```
/branch main feature-auth
/branch develop bugfix-123
/branch feature-logging feature-logging-refactor
```

**응답**:
```
✅ 새 브랜치가 생성되었습니다.

**기준 브랜치**: main
**새 브랜치**: feature-auth

현재 브랜치: feature-auth

이제 /task 명령으로 작업을 시작하세요.
```

**오류 응답** (브랜치 이미 존재):
```
❌ 브랜치 생성 실패

오류: 브랜치 'feature-auth'가 이미 존재합니다.

대안:
- 기존 브랜치로 전환: git checkout feature-auth
- 다른 이름 사용: /branch main feature-auth-v2
```

---

## 공통 응답 패턴

### 권한 없음

모든 명령어에 대해 화이트리스트에 없는 사용자가 요청 시:

```
🚫 권한이 없습니다.

이 봇은 인증된 사용자만 사용할 수 있습니다.
액세스가 필요하면 관리자에게 문의하세요.
```

### 환경 변수 미설정

필수 환경 변수가 설정되지 않은 경우:

```
❌ 설정 오류

필수 환경 변수가 설정되지 않았습니다:
- TELEGRAM_ALLOWED_USERS
- ANTHROPIC_API_KEY

.env 파일을 확인하고 CCW를 재시작하세요.
```

### 연결 끊김

작업 중 텔레그램 연결이 끊긴 경우 (재연결 시):

```
⚠️ 작업이 중단되었습니다.

작업 ID: abc-123
중단 시각: 2025-11-08 10:45:00
중단 사유: 텔레그램 연결 끊김

변경사항이 롤백되었습니다.
작업을 다시 시도해주세요.
```

## 명령어 우선순위

1. **인증 검사** (모든 명령어)
2. **작업 진행 중 체크** (/task, /commit, /mr, /branch)
3. **환경 변수 검증** (모든 명령어)
4. **명령어 실행**

## 에러 코드

| 코드 | 설명 |
|------|------|
| AUTH_FAILED | 사용자 인증 실패 |
| TASK_IN_PROGRESS | 작업이 이미 진행 중 |
| COMMAND_BLOCKED | 명령어 차단됨 |
| TIMEOUT | 작업 타임아웃 |
| CONNECTION_LOST | 텔레그램 연결 끊김 |
| GIT_ERROR | Git 작업 실패 |
| GITHUB_AUTH_FAILED | GitHub 인증 실패 |
| AGENT_ERROR | 에이전트 실행 오류 |

## 다음 단계

텔레그램 명령어 스키마가 정의되었습니다. 다음 작업:

1. **claude_api_contract.md** 생성: Claude API 호출 계약
2. **github_api_contract.md** 생성: GitHub API 호출 계약
3. **quickstart.md** 생성: 개발 환경 설정 가이드
