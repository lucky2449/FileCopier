#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

# ============================================================
# GitHub 저장소 주소 설정 (업데이트 배포 시 변경 필요)
# 예: "username/FileCopier"
GITHUB_REPO = "your-username/your-repo"
# ============================================================


def _parse_version(version_str):
    """'v1.2.3' 또는 '1.2.3' 형식을 정수 튜플로 변환"""
    clean = version_str.lstrip("v").strip()
    try:
        return tuple(int(x) for x in clean.split("."))
    except ValueError:
        return (0,)


def get_latest_release(repo=GITHUB_REPO):
    """GitHub Releases API에서 최신 버전 정보를 가져옵니다.

    Returns:
        (version_str, download_url) 또는 실패 시 (None, None)
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FileCopier-Updater"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        tag = data.get("tag_name", "")
        assets = data.get("assets", [])

        download_url = None
        for asset in assets:
            name = asset.get("name", "")
            if name.lower().endswith(".exe"):
                download_url = asset.get("browser_download_url")
                break

        if tag and download_url:
            return tag, download_url
    except Exception:
        pass
    return None, None


def is_newer(latest_str, current_str):
    """latest가 current보다 높은 버전이면 True"""
    return _parse_version(latest_str) > _parse_version(current_str)


def download_update(download_url, progress_callback=None):
    """새 EXE를 임시 파일로 다운로드합니다.

    Args:
        download_url: 다운로드 URL
        progress_callback: (downloaded_bytes, total_bytes) 를 받는 콜백 함수

    Returns:
        다운로드된 임시 파일 경로 또는 실패 시 None
    """
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".exe", delete=False)
        tmp_path = tmp.name
        tmp.close()

        def _report(block_count, block_size, total_size):
            if progress_callback and total_size > 0:
                downloaded = min(block_count * block_size, total_size)
                progress_callback(downloaded, total_size)

        urllib.request.urlretrieve(download_url, tmp_path, _report)
        return tmp_path
    except Exception:
        return None


def apply_update(new_exe_path):
    """현재 실행 중인 EXE를 새 버전으로 교체하고 재시작합니다.

    Windows에서는 실행 중인 EXE를 직접 덮어쓸 수 없으므로
    배치 파일을 통해 교체 후 재시작합니다.
    """
    current_exe = Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0]).resolve()
    new_exe = Path(new_exe_path).resolve()
    bat_path = current_exe.parent / "_updater_temp.bat"

    bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
copy /y "{new_exe}" "{current_exe}"
del "{new_exe}"
start "" "{current_exe}"
del "%~f0"
"""
    bat_path.write_text(bat_content, encoding="cp949")
    subprocess.Popen(["cmd", "/c", str(bat_path)], creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit(0)
