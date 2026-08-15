# -*- mode: python ; coding: utf-8 -*-
import os
import whisper
import faster_whisper
from PyInstaller.utils.hooks import collect_all, copy_metadata, collect_data_files

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
        # Ajoutez ces deux lignes si vous utilisez un modèle Nemotron-4 ou similaire basé sur Llama/Gemma
        # 'transformers.models.llama',
        # 'transformers.models.gemma',
        'tokenizers'
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

datas_trans, binaries_trans, hidden_trans = collect_all('transformers')
a_cli.datas += datas_trans
a_cli.binaries += binaries_trans
a_cli.hiddenimports += hidden_trans

for pkg in ['torchcodec', 'torch', 'openai-whisper', 'faster-whisper', 'hf_xet']:
    d, b, h = collect_all(pkg)
    a_cli.datas += d
    a_cli.binaries += b
    a_cli.hiddenimports += h

a_cli.datas += collect_data_files('transformers', include_py_files=True)
pkgs_to_collect = [
    'transformers', 
    'torchcodec', 
    'torch', 
    'openai-whisper', 
    'faster-whisper', 
    'hf_xet', 
    'huggingface_hub', 
    'tokenizers',
    'safetensors' # Indispensable pour charger les poids .safetensors de Nemotron
]

for pkg in pkgs_to_collect:
    try:
        d, b, h = collect_all(pkg)
        a_cli.datas += d
        a_cli.binaries += b
        a_cli.hiddenimports += h
        a_cli.datas += copy_metadata(pkg)
    except Exception:
        pass
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
    hiddenimports=[
        'transformers.models.auto.processing_auto',
        'transformers.models.auto.tokenization_auto',
        'transformers.models.auto.configuration_auto',
        # Ajoutez ces deux lignes si vous utilisez un modèle Nemotron-4 ou similaire basé sur Llama/Gemma
        # 'transformers.models.llama',
        # 'transformers.models.gemma',
        'tokenizers'
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

a_gui.datas += datas_trans
a_gui.binaries += binaries_trans
a_gui.hiddenimports += hidden_trans

for pkg in ['torchcodec', 'torch', 'openai-whisper', 'faster-whisper', 'hf_xet']:
    d, b, h = collect_all(pkg)
    a_gui.datas += d
    a_gui.binaries += b
    a_gui.hiddenimports += h

a_gui.datas += collect_data_files('transformers', include_py_files=True)
pkgs_to_collect = [
    'transformers', 
    'torchcodec', 
    'torch', 
    'openai-whisper', 
    'faster-whisper', 
    'hf_xet', 
    'huggingface_hub', 
    'tokenizers',
    'safetensors' # Indispensable pour charger les poids .safetensors de Nemotron
]

for pkg in pkgs_to_collect:
    try:
        d, b, h = collect_all(pkg)
        a_gui.datas += d
        a_gui.binaries += b
        a_gui.hiddenimports += h
        a_gui.datas += copy_metadata(pkg)
    except Exception:
        pass

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
