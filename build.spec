# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import tkinter
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# 收集tkinter的所有子模块
tkinter_modules = collect_submodules('tkinter')

# 获取tcl/tk数据文件路径
tcl_tk_path = os.path.dirname(tkinter.__file__)
tcl_path = os.path.join(tcl_tk_path, 'tcl')
tk_path = os.path.join(tcl_tk_path, 'tk')

# 收集所有tcl/tk数据文件
tcl_tk_files = []
for root, dirs, files in os.walk(tcl_path):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, tcl_tk_path)
        tcl_tk_files.append((full_path, os.path.dirname(rel_path)))
        
for root, dirs, files in os.walk(tk_path):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, tcl_tk_path)
        tcl_tk_files.append((full_path, os.path.dirname(rel_path)))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui', 'gui'),  # 包含gui目录
        ('api', 'api'),  # 包含api目录
        ('app.ico', '.'),  # 添加图标文件
    ] + tcl_tk_files,    # 添加tcl/tk文件
    hiddenimports=[
        'requests',
        'urllib3',
        'idna',
        'chardet',
        'certifi',
        'hmac',
        'hashlib',
        'json',
        'random',
        'threading',
        'time',
        'datetime',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        '_tkinter',
    ] + tkinter_modules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
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
    name='CEX提币器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 改回False以隐藏终端窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',  # 确保这里设置了图标
)