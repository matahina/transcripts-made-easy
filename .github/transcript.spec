# -*- mode: python ; coding: utf-8 -*-
import os
import whisper
import faster_whisper
from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

whisper_assets = os.path.join(os.path.dirname(whisper.__file__), 'assets')
faster_assets = os.path.join(os.path.dirname(faster_whisper.__file__), 'assets')

# 1. Analyse principale basée sur le script CLI (qui inclut toutes les dépendances lourdes partagées)
a = Analysis(
    ['../transcript_cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        (faster_assets, 'faster_whisper/assets'),
        (whisper_assets, 'whisper/assets')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'PyQt5'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collecte des dépendances et métadonnées
datas_trans, binaries_trans, hidden_trans = collect_all('transformers')
a.datas += datas_trans
a.binaries += binaries_trans
a.hiddenimports += hidden_trans

a.datas += copy_metadata('torchcodec')
a.datas += copy_metadata('torch')
a.datas += copy_metadata('openai-whisper')
a.datas += copy_metadata('faster-whisper')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 2. Premier exécutable : CLI (console=True)
exe_cli = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transcript_cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 3. Deuxième exécutable : GUI (console=False)
# On réutilise exactement la même analyse de dépendances de base (a.scripts et pyz)
exe_gui = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transcript_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 4. Regroupement final sans conflits de listes
coll = COLLECT(
    exe_cli,
    exe_gui,       # Les deux binaires pointent vers le même package de dépendances 'a'
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transcript_app',
)
