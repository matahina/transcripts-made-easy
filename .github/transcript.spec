# -*- mode: python ; coding: utf-8 -*-

import os
import whisper
import faster_whisper

from PyInstaller.utils.hooks import collect_all, copy_metadata


# ============================================================
# CONFIGURATION
# ============================================================

block_cipher = None

whisper_assets = os.path.join(
    os.path.dirname(whisper.__file__),
    'assets'
)

faster_assets = os.path.join(
    os.path.dirname(faster_whisper.__file__),
    'assets'
)


# ============================================================
# PACKAGES À COLLECTER
# ============================================================
#
# IMPORTANT :
# - torchcodec NE doit PAS être dans collect_all()
# - ses metadata sont ajoutées séparément avec copy_metadata()
#
# ============================================================

pkgs_to_collect = [
    'transformers',
    'torch',
    'openai-whisper',
    'faster-whisper',
    'hf_xet',
    'huggingface_hub',
    'tokenizers',
    'safetensors',
    'qwen_asr',
]


# ============================================================
# HIDDEN IMPORTS COMMUNS
# ============================================================

common_hiddenimports = [
    # Transformers Auto
    'transformers.models.auto.processing_auto',
    'transformers.models.auto.tokenization_auto',
    'transformers.models.auto.configuration_auto',

    # Transformers audio
    'transformers.audio_utils',
    'transformers.processing_utils',

    # Qwen3-ASR
    'qwen_asr',
    'qwen_asr.core',
    'qwen_asr.core.transformers_backend',
    'qwen_asr.inference',
    'qwen_asr.inference.qwen3_asr',

    # Tokenizers
    'tokenizers',
]


# ============================================================
# FONCTION DE COLLECTE
# ============================================================

def collect_packages(analysis):
    for pkg in pkgs_to_collect:

        print(f'Collecte de : {pkg}')

        d, b, h = collect_all(pkg)

        analysis.datas += d
        analysis.binaries += b
        analysis.hiddenimports += h


# ============================================================
# METADATA
# ============================================================
#
# Transformers fait ceci dans audio_utils.py :
#
#     importlib.metadata.version("torchcodec")
#
# Il faut donc que torchcodec-*.dist-info soit présent
# dans le dossier final de l'application.
#
# copy_metadata() est prévu précisément pour ce cas.
#
# ============================================================

def collect_metadata(analysis):

    metadata_packages = [
        'torchcodec',
        'torch',
        'transformers',
        'huggingface_hub',
        'tokenizers',
        'safetensors',
        'qwen_asr',
    ]

    for pkg in metadata_packages:

        print(f'Metadata de : {pkg}')

        try:
            metadata = copy_metadata(pkg)
            analysis.datas += metadata

        except Exception as e:
            print(
                f'WARNING: impossible de copier les metadata '
                f'de {pkg}: {e}'
            )


# ============================================================
# 1. CLI
# ============================================================

a_cli = Analysis(
    ['../transcript_cli.py'],

    pathex=[],

    binaries=[],

    datas=[
        (
            faster_assets,
            'faster_whisper/assets'
        ),
        (
            whisper_assets,
            'whisper/assets'
        ),
    ],

    hiddenimports=common_hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[
        'matplotlib',
        'PyQt5',
    ],

    win_no_prefer_redirects=False,

    win_private_assemblies=False,

    cipher=block_cipher,

    noarchive=False,
)


# Collecte des packages
collect_packages(a_cli)

# Collecte des metadata
collect_metadata(a_cli)


# ============================================================
# PYZ CLI
# ============================================================

pyz_cli = PYZ(
    a_cli.pure,
    a_cli.zipped_data,
    cipher=block_cipher
)


# ============================================================
# EXE CLI
# ============================================================

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


# ============================================================
# 2. GUI
# ============================================================

a_gui = Analysis(
    ['../transcript_cli.py'],

    pathex=[],

    binaries=[],

    datas=[
        (
            faster_assets,
            'faster_whisper/assets'
        ),
        (
            whisper_assets,
            'whisper/assets'
        ),
    ],

    hiddenimports=common_hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[
        'matplotlib',
        'PyQt5',
    ],

    win_no_prefer_redirects=False,

    win_private_assemblies=False,

    cipher=block_cipher,

    noarchive=False,
)


# Collecte des packages
collect_packages(a_gui)

# Collecte des metadata
collect_metadata(a_gui)


# ============================================================
# PYZ GUI
# ============================================================

pyz_gui = PYZ(
    a_gui.pure,
    a_gui.zipped_data,
    cipher=block_cipher
)


# ============================================================
# EXE GUI
# ============================================================

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


# ============================================================
# 3. DOSSIER FINAL UNIQUE
# ============================================================
#
# dist/
# └── transcript_app/
#     ├── transcript_cli.exe
#     ├── transcript_gui.exe
#     ├── _internal/
#     └── ...
#
# ============================================================

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
