# -*- mode: python ; coding: utf-8 -*-
import os


block_cipher = None


a = Analysis(
    ["club-q.py"],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[(os.path.join("resources", file_name), "resources") for file_name in os.listdir("resources")],
    hiddenimports=["pymysql"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="club-q",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon="resources\\icon_q.ico"
)
