# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드를 다룰 때 참고하는 안내 문서입니다.

## 프로젝트 개요

사용자가 제공한 숫자, 파일명, 파일 경로 목록을 기반으로 소스 폴더에서 대상 폴더로 파일을 복사하는 PyQt5 GUI 애플리케이션입니다. 주로 숫자 ID로 이미지/미디어 파일을 일괄 복사하는 용도로 사용됩니다.

## 애플리케이션 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
python modern_file_copier.py
```

## 빌드 및 배포 흐름

### 1. EXE 빌드

```bash
python utils/build_exe.py
```

`dist/FileCopier.exe` 단일 파일이 생성됩니다.

### 2. GitHub Release 업로드

1. `modern_file_copier.py`의 `__version__` 값을 올린다 (예: `"1.0.1"`)
2. `python utils/build_exe.py` 로 빌드
3. GitHub에서 새 Release를 만들고 태그를 `v{버전}` 으로 설정 (예: `v1.0.1`)
4. `dist/FileCopier.exe` 를 Release에 첨부하고 게시

앱이 실행될 때 GitHub Releases API를 백그라운드에서 확인하여 새 버전이 있으면 상단에 업데이트 배너를 표시합니다.

### 3. 인스톨러 생성 (최초 배포)

`installer/FileCopier_Setup.iss` 를 Inno Setup Compiler로 열어 빌드하면 설치 프로그램(`.exe`)이 생성됩니다.
- 다운로드: https://jrsoftware.org/isdl.php
- 설치 위치: `%LOCALAPPDATA%\FileCopier` (관리자 권한 불필요)
- 바탕화면 및 시작 메뉴 바로가기 생성

### GitHub 저장소 설정

`utils/updater.py` 상단의 `GITHUB_REPO` 값을 실제 저장소 주소로 변경해야 자동 업데이트가 동작합니다.

```python
GITHUB_REPO = "your-username/your-repo"  # ← 실제 값으로 변경
```

## 아키텍처

### 메인 애플리케이션 (`modern_file_copier.py`)

`ModernFileCopier`(QMainWindow)는 최상위 윈도우로 두 패널로 구성됩니다:
- **왼쪽 패널**: 소스/대상 경로 입력 + 텍스트 입력 영역 (숫자, 파일명, 전체 경로 입력 가능; `.txt` 파일 불러오기 또는 다이얼로그를 통한 파일 선택도 지원)
- **오른쪽 패널**: 확장자 필터 콤보박스 + 진행률 표시줄 + 실행 로그

`FileScanThread`(QThread)는 백그라운드에서 폴더를 스캔하여 사용 가능한 파일 확장자를 탐색하고, UI를 차단하지 않고 콤보박스를 채웁니다.

### 자동 업데이트 (`utils/updater.py`)

앱 시작 시 `UpdateCheckThread`가 GitHub Releases API를 백그라운드에서 조회합니다. 현재 `__version__`보다 높은 태그가 있으면 메인 윈도우 상단에 초록 배너를 표시하고, "지금 업데이트" 버튼을 통해 다운로드 및 자동 교체합니다.

### 파일 매칭 로직 (`find_files` 메서드)

복사를 시작하면 각 입력 항목은 다음 순서의 전략으로 파일로 변환됩니다:
1. 절대 경로 — `os.path.exists(item)`이 참인 경우
2. 정확한 파일명 일치 (확장자 포함)
3. 스템 일치 — 확장자 없는 파일명이 입력과 동일한 경우 (다이얼로그로 파일 선택 시 확장자가 제거될 때 사용)
4. 숫자 접미사 일치 — 스템의 마지막 5자를 앞의 0을 제거한 정수로 비교

### 주요 파일

| 파일 | 용도 |
|---|---|
| `modern_file_copier.py` | 메인 애플리케이션 진입점 (`__version__` 관리) |
| `utils/updater.py` | GitHub 업데이트 확인·다운로드·교체 |
| `utils/build_exe.py` | PyInstaller 빌드 + Release 안내 |
| `FileCopier.spec` | PyInstaller spec (단일 EXE 출력) |
| `installer/FileCopier_Setup.iss` | Inno Setup 인스톨러 스크립트 |
