# -*- mode: python ; coding: utf-8 -*-
import os
import whisper
import faster_whisper
from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

# Détection dynamique des dossiers d'assets indispensables
whisper_assets = os.path.join(os.path.dirname(whisper.__file__), 'assets')
faster_assets = os.path.join(os.path.dirname(faster_whisper.__file__), 'assets')

# 1. Analyse partagée des dépendances (Scripts, packages et modules cachés)
a = Analysis(
    ['../transcript_cli.py', '../transcript_gui.py'],
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
    excludes=['matplotlib', 'PyQt5'],  # Tkinter reste inclus implicitement ici
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collecte stricte des packages lourds et des métadonnées
datas_trans, binaries_trans, hidden_trans = collect_all('transformers')
a.datas += datas_trans
a.binaries += binaries_trans
a.hiddenimports += hidden_trans

a.datas += copy_metadata('torchcodec')
a.datas += copy_metadata('torch')
a.datas += copy_metadata('openai-whisper')
a.datas += copy_metadata('faster-whisper')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 2. Définition de l'exécutable CLI (console=True)
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

# 3. Définition de l'exécutable GUI (console=False / windowed)
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

# 4. Regroupement final dans un sous-dossier partagé
coll = COLLECT(
    exe_cli,
    exe_gui,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transcript_app',  # Tout se retrouve dans dist/transcript_app/
)
