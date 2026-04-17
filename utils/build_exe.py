#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실행 파일 생성 스크립트
PyInstaller를 사용하여 단일 EXE 파일로 빌드합니다.
빌드 후 dist/FileCopier.exe 를 GitHub Release에 업로드하세요.
"""

import subprocess
import sys
import re
from pathlib import Path


def get_version():
    source = Path(__file__).parent.parent / "modern_file_copier.py"
    for line in source.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^__version__\s*=\s*["\'](.+)["\']', line)
        if m:
            return m.group(1)
    return "0.0.0"


def build_executable():
    print("=" * 50)
    version = get_version()
    print(f"파일 복사 프로그램 v{version} 빌드")
    print("=" * 50)

    project_root = Path(__file__).parent.parent
    spec_file = project_root / "FileCopier.spec"

    if not spec_file.exists():
        print("❌ FileCopier.spec 파일을 찾을 수 없습니다.")
        return False

    cmd = [
        "pyinstaller",
        str(spec_file),
        "--clean",
        "--noconfirm",
        "--distpath", str(project_root / "dist"),
        "--workpath", str(project_root / "build"),
    ]

    print(f"명령어: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True,
            encoding="utf-8", errors="ignore"
        )
        print("✅ PyInstaller 완료")
        if result.stdout:
            print(result.stdout[-2000:])

        exe = project_root / "dist" / "FileCopier.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / 1024 / 1024
            print(f"\n✅ 빌드 성공: {exe}")
            print(f"   크기: {size_mb:.1f} MB")
            print(f"\n📌 다음 단계:")
            print(f"   1. GitHub에서 새 Release 생성 (태그: v{version})")
            print(f"   2. {exe.name} 파일을 Release에 첨부")
            print(f"   3. Release 게시")
            return True
        else:
            print(f"❌ {exe} 파일을 찾을 수 없습니다.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        if e.stderr:
            print(e.stderr[-1000:])
        return False
    except FileNotFoundError:
        print("❌ PyInstaller를 찾을 수 없습니다.")
        print("   pip install pyinstaller")
        return False


def main():
    success = build_executable()
    print("\n" + "=" * 50)
    print("빌드 성공! 🎉" if success else "빌드 실패! ❌")
    print("=" * 50)


if __name__ == "__main__":
    main()
