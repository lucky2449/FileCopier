#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실행 파일 및 설치 프로그램 생성 스크립트
1단계: PyInstaller로 단일 EXE 빌드
2단계: Inno Setup으로 설치 프로그램(.exe) 빌드
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


def build_executable(project_root, version):
    print("\n[1/2] EXE 빌드 (PyInstaller)")
    print("-" * 40)

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

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True,
            encoding="utf-8", errors="ignore"
        )
        if result.stdout:
            print(result.stdout[-2000:])

        exe = project_root / "dist" / "FileCopier.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / 1024 / 1024
            print(f"✅ {exe.name} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"❌ {exe} 파일을 찾을 수 없습니다.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 빌드 실패: {e}")
        if e.stderr:
            print(e.stderr[-1000:])
        return False
    except FileNotFoundError:
        print("❌ PyInstaller를 찾을 수 없습니다.  →  pip install pyinstaller")
        return False


def build_installer(project_root, version):
    print("\n[2/2] 설치 프로그램 빌드 (Inno Setup)")
    print("-" * 40)

    iss_file = project_root / "installer" / "FileCopier_Setup.iss"
    if not iss_file.exists():
        print(f"❌ {iss_file} 파일을 찾을 수 없습니다.")
        return False

    # Inno Setup 설치 경로 후보
    iscc_candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 5\ISCC.exe"),
    ]
    iscc = next((p for p in iscc_candidates if p.exists()), None)

    if iscc is None:
        print("⚠️  Inno Setup이 설치되어 있지 않아 설치 프로그램을 건너뜁니다.")
        print("   설치: https://jrsoftware.org/isdl.php")
        return False

    # AppVersion 값을 현재 버전으로 오버라이드
    cmd = [str(iscc), f"/DAppVersion={version}", str(iss_file)]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True,
            encoding="utf-8", errors="ignore"
        )

        installer_dir = project_root / "installer_output"
        installer = installer_dir / f"FileCopier_설치_v{version}.exe"
        if installer.exists():
            size_mb = installer.stat().st_size / 1024 / 1024
            print(f"✅ {installer.name} ({size_mb:.1f} MB)")
            return True
        else:
            # 파일명이 다를 수 있으므로 폴더에서 검색
            candidates = list(installer_dir.glob("FileCopier_설치*.exe")) if installer_dir.exists() else []
            if candidates:
                f = candidates[-1]
                print(f"✅ {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
                return True
            print(f"❌ 설치 프로그램 파일을 찾을 수 없습니다: {installer_dir}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Inno Setup 빌드 실패: {e}")
        if e.stderr:
            print(e.stderr[-500:])
        return False


def main():
    version = get_version()
    project_root = Path(__file__).parent.parent

    print("=" * 50)
    print(f"파일 복사 프로그램 v{version} 빌드")
    print("=" * 50)

    exe_ok = build_executable(project_root, version)
    if not exe_ok:
        print("\n빌드 실패 ❌")
        sys.exit(1)

    installer_ok = build_installer(project_root, version)

    print("\n" + "=" * 50)
    if exe_ok and installer_ok:
        print("빌드 완료 ✅")
        print(f"\n📌 GitHub Release 업로드 목록:")
        print(f"   • dist/FileCopier.exe")
        print(f"   • installer_output/FileCopier_설치_v{version}.exe")
    elif exe_ok:
        print("EXE 빌드 완료 ✅  (설치 프로그램 생략)")
        print(f"\n📌 GitHub Release 업로드 목록:")
        print(f"   • dist/FileCopier.exe")
    print("=" * 50)


if __name__ == "__main__":
    main()
