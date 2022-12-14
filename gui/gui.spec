# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['gui.py'],
    pathex=['\\home\\krayt\\FINAL\\'],
    binaries=[],
    datas=[('../backend/','.'),('../sql/','.'),('../modules/','.'), ('../json/','.'), ('account.kv', '.'), ('addInv.kv', '.'), ('adminLogin.kv', '.'), ('adminMenu.kv', '.'), ('cart.kv', '.'), ('frontPage.kv', '.'), ('helpScreen.kv', '.'), ('login.kv', '.'), ('mainPOS.kv', '.'), ('reports.kv', '.'), ('searchItem.kv', '.')],
    hiddenimports=['pandas','os','sys', 'docx', 'smtplib', 'email', 'email.mime', 'email.mime.multipart', 'email.mime.text', 'email.mime.base', 'email.encoders'],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
