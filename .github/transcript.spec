# -*- mode: python ; coding: utf-8 -*-

import os

import whisper
import faster_whisper

from PyInstaller.utils.hooks import collect_all, copy_metadata


block_cipher = None


# ============================================================
# ASSETS WHISPER / FASTER-WHISPER
# ============================================================

whisper_assets = os.path.join(
    os.path.dirname(whisper.__file__),
    "assets"
)

faster_assets = os.path.join(
    os.path.dirname(faster_whisper.__file__),
    "assets"
)


# ============================================================
# DONNÉES COMMUNES AUX DEUX EXÉCUTABLES
# ============================================================
#
# IMPORTANT :
#
# Tout ce qui vient de collect_all() ou copy_metadata()
# doit être ajouté ICI, AVANT Analysis().
#
# Ne plus faire ensuite :
#
#     a_cli.datas += ...
#     a_cli.binaries += ...
#
# avec les retours de collect_all/copy_metadata.
#
# ============================================================

common_datas = [
    (faster_assets, "faster_whisper/assets"),
    (whisper_assets, "whisper/assets"),
]

common_binaries = []

common_hiddenimports = [
    # Transformers Auto
    "transformers.models.auto.processing_auto",
    "transformers.models.auto.tokenization_auto",
    "transformers.models.auto.configuration_auto",

    # Transformers audio / processor
    "transformers.audio_utils",
    "transformers.processing_utils",

    # Qwen3-ASR
    "qwen_asr",
    "qwen_asr.core",
    "qwen_asr.core.transformers_backend",
    "qwen_asr.inference",
    "qwen_asr.inference.qwen3_asr",

    # Tokenizers
    "tokenizers",
]


# ============================================================
# PACKAGES À COLLECTER
# ============================================================
#
# torchcodec n'est volontairement PAS ici.
#
# On a besoin surtout de ses metadata pour :
#
# importlib.metadata.version("torchcodec")
#
# dans transformers.audio_utils.
#
# ============================================================

pkgs_to_collect = [
    "transformers",
    "torch",
    "openai-whisper",
    "faster-whisper",
    "hf_xet",
    "huggingface_hub",
    "tokenizers",
    "safetensors",
    "qwen_asr",
]


for pkg in pkgs_to_collect:
    print(f"Collecte de : {pkg}")

    datas, binaries, hiddenimports = collect_all(pkg)

    common_datas += datas
    common_binaries += binaries
    common_hiddenimports += hiddenimports


# ============================================================
# METADATA
# ============================================================
#
# copy_metadata() utilise le NOM DE LA DISTRIBUTION installée.
#
# Exemple :
#
# module importé : qwen_asr
# distribution   : qwen-asr
#
# ============================================================

metadata_packages = [
    "torchcodec",
    "torch",
    "transformers",
    "huggingface_hub",
    "tokenizers",
    "safetensors",
    "qwen-asr",
]


for pkg in metadata_packages:
    print(f"Metadata de : {pkg}")

    try:
        metadata = copy_metadata(pkg)

        common_datas += metadata

        print(
            f"OK metadata {pkg}: "
            f"{len(metadata)} entrée(s)"
        )

    except Exception as e:
        print(
            f"WARNING: impossible de copier "
            f"les metadata de {pkg}: {e}"
        )


# ============================================================
# DEBUG IMPORTANT POUR TORCHCODEC
# ============================================================

print("")
print("============================================")
print("VÉRIFICATION METADATA TORCHCODEC")
print("============================================")

torchcodec_metadata = [
    item
    for item in common_datas
    if "torchcodec" in str(item).lower()
]

for item in torchcodec_metadata:
    print(item)

print("============================================")
print("")


# ============================================================
# 1. CLI
# ============================================================

a_cli = Analysis(
    ["../transcript_cli.py"],

    pathex=[],

    binaries=common_binaries.copy(),

    datas=common_datas.copy(),

    hiddenimports=common_hiddenimports.copy(),

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[
        "matplotlib",
        "PyQt5",
    ],

    win_no_prefer_redirects=False,

    win_private_assemblies=False,

    cipher=block_cipher,

    noarchive=False,
)


# ============================================================
# PYZ CLI
# ============================================================

pyz_cli = PYZ(
    a_cli.pure,
    a_cli.zipped_data,
    cipher=block_cipher,
)


# ============================================================
# EXE CLI
# ============================================================

exe_cli = EXE(
    pyz_cli,

    a_cli.scripts,

    [],

    exclude_binaries=True,

    name="transcript_cli",

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
#
# Je conserve ici le comportement de ton spec actuel :
# le deuxième EXE utilise également transcript_cli.py,
# avec console=False.
#
# Ton spec actuel fait bien cela.
#
# ============================================================

a_gui = Analysis(
    ["../transcript_gui.py"],

    pathex=[],

    binaries=common_binaries.copy(),

    datas=common_datas.copy(),

    hiddenimports=common_hiddenimports.copy(),

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[
        "matplotlib",
        "PyQt5",
    ],

    win_no_prefer_redirects=False,

    win_private_assemblies=False,

    cipher=block_cipher,

    noarchive=False,
)


# ============================================================
# PYZ GUI
# ============================================================

pyz_gui = PYZ(
    a_gui.pure,
    a_gui.zipped_data,
    cipher=block_cipher,
)


# ============================================================
# EXE GUI
# ============================================================

exe_gui = EXE(
    pyz_gui,

    a_gui.scripts,

    [],

    exclude_binaries=True,

    name="transcript_gui",

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
# 3. DOSSIER FINAL COMMUN
# ============================================================
#
# Résultat :
#
# dist/
# └── transcript_app/
#     ├── transcript_cli.exe
#     ├── transcript_gui.exe
#     └── _internal/
#
# IMPORTANT :
# Aucun clean_toc().
#
# Les Analysis() ont déjà converti les datas/binaries
# au format TOC interne correct.
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

    name="transcript_app",
)
