# -*- mode: python ; coding: utf-8 -*-
import os, sys
import whisper
import faster_whisper
from PyInstaller.utils.hooks import collect_all, copy_metadata, collect_data_files

site_packages = os.path.join(
    sys.prefix,
    "Lib",
    "site-packages"
)

print("PYTHON PREFIX:", sys.prefix)
print("SITE PACKAGES:", site_packages)

print(
    "TORCHCODEC DIST-INFO:",
    [
        x for x in os.listdir(site_packages)
        if "torchcodec" in x.lower()
    ]
)

block_cipher = None

whisper_assets = os.path.join(os.path.dirname(whisper.__file__), 'assets')
faster_assets = os.path.join(os.path.dirname(faster_whisper.__file__), 'assets')

# Fonction de sécurité pour nettoyer les résidus mal formés de Python 3.14
def clean_toc(toc_list):
    cleaned = []
    for item in toc_list:
        # Une entrée valide dans PyInstaller DOIT avoir 3 éléments
        if isinstance(item, (list, tuple)) and len(item) == 3:
            cleaned.append(item)
        # Si PyInstaller a généré un tuple à 2 éléments, on tente de le corriger en lui attribuant le type 'DATA'
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            cleaned.append((item[0], item[1], 'DATA'))
    return cleaned

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
    hiddenimports=[
        'transformers.models.auto.processing_auto',
        'transformers.models.auto.tokenization_auto',
        'transformers.models.auto.configuration_auto',

        'qwen_asr',
        'qwen_asr.core',
        'qwen_asr.core.transformers_backend',
        'qwen_asr.inference',
        'qwen_asr.inference.qwen3_asr',

        'tokenizers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'PyQt5'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

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

for pkg in pkgs_to_collect:
    d, b, h = collect_all(pkg)
    a_cli.datas += d
    a_cli.binaries += b
    a_cli.hiddenimports += h

# ============================================================
# torchcodec : ajouter manuellement ses metadata
# ============================================================

site_packages = os.path.join(
    sys.prefix,
    'Lib',
    'site-packages'
)

torchcodec_dist_info = next(
    (
        os.path.join(site_packages, d)
        for d in os.listdir(site_packages)
        if d.lower().startswith('torchcodec-')
        and d.lower().endswith('.dist-info')
    ),
    None
)

if torchcodec_dist_info is None:
    raise RuntimeError(
        f"Impossible de trouver torchcodec-*.dist-info dans : "
        f"{site_packages}"
    )

a_cli.datas.append(
    (
        torchcodec_dist_info,
        os.path.basename(torchcodec_dist_info)
    )
)

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
    ['../transcript_cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        (faster_assets, 'faster_whisper/assets'),
        (whisper_assets, 'whisper/assets')
    ],
    hiddenimports=[
        'transformers.models.auto.processing_auto',
        'transformers.models.auto.tokenization_auto',
        'transformers.models.auto.configuration_auto',

        'qwen_asr',
        'qwen_asr.core',
        'qwen_asr.core.transformers_backend',
        'qwen_asr.inference',
        'qwen_asr.inference.qwen3_asr',

        'tokenizers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'PyQt5'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

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

for pkg in pkgs_to_collect:
    d, b, h = collect_all(pkg)
    a_gui.datas += d
    a_gui.binaries += b
    a_gui.hiddenimports += h

# ============================================================
# torchcodec : ajouter manuellement ses metadata
# ============================================================

site_packages = os.path.join(
    sys.prefix,
    'Lib',
    'site-packages'
)

torchcodec_dist_info = next(
    (
        os.path.join(site_packages, d)
        for d in os.listdir(site_packages)
        if d.lower().startswith('torchcodec-')
        and d.lower().endswith('.dist-info')
    ),
    None
)

if torchcodec_dist_info is None:
    raise RuntimeError(
        f"Impossible de trouver torchcodec-*.dist-info dans : "
        f"{site_packages}"
    )

a_gui.datas.append(
    (
        torchcodec_dist_info,
        os.path.basename(torchcodec_dist_info)
    )
)

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
# 3. REGROUPEMENT FINAL ET NETTOYAGE
# ==========================================
coll = COLLECT(
    exe_cli,
    clean_toc(a_cli.binaries),
    clean_toc(a_cli.zipfiles),
    clean_toc(a_cli.datas),
    exe_gui,
    clean_toc(a_gui.binaries),
    clean_toc(a_gui.zipfiles),
    clean_toc(a_gui.datas),
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transcript_app',
)
