# -*- mode: python ; coding: utf-8 -*-
import os
import whisper
import faster_whisper
from PyInstaller.utils.hooks import collect_all

block_cipher = None

whisper_assets = os.path.join(os.path.dirname(whisper.__file__), 'assets')
faster_assets = os.path.join(os.path.dirname(faster_whisper.__file__), 'assets')

# ==========================================
# 1. ANALYSE ET CONFIGURATION POUR CLI
# ==========================================
a_cli = Analysis(
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

# Collecte complète et sécurisée pour Transformers
datas_trans, binaries_trans, hidden_trans = collect_all('transformers')
a_cli.datas += datas_trans
a_cli.binaries += binaries_trans
a_cli.hiddenimports += hidden_trans

# Collecte complète pour les autres dépendances lourdes (gère les métadonnées proprement)
for pkg in ['torchcodec', 'torch', 'openai-whisper', 'faster-whisper']:
    d, b, h = collect_all(pkg)
    a_cli.datas += d
    a_cli.binaries += b
    a_cli.hiddenimports += h

pyz_cli = PYZ(a_cli.pure, a_cli.zipped_data, cipher=block_cipher)

exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
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

# ==========================================
# 2. ANALYSE ET CONFIGURATION POUR GUI
# ==========================================
a_gui = Analysis(
    ['../transcript_gui.py'],
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

# On applique exactement les mêmes collectes validées pour le GUI
a_gui.datas += datas_trans
a_gui.binaries += binaries_trans
a_gui.hiddenimports += hidden_trans

for pkg in ['torchcodec', 'torch', 'openai-whisper', 'faster-whisper']:
    d, b, h = collect_all(pkg)
    a_gui.datas += d
    a_gui.binaries += b
    a_gui.hiddenimports += h

pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data, cipher=block_cipher)

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
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

# ==========================================
# 3. REGROUPEMENT FINAL DANS UN DOSSIER UNIQUE
# ==========================================
coll = COLLECT(
    exe_cli,
    a_cli.binaries,
    a_cli.zipfiles,
    a_cli.datas,
    exe_gui,
    a_gui.binaries,
    a_gui.zipfiles,
    a_gui.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transcript_app',
)
