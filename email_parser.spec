# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for email_parser

import sys
from pathlib import Path

# Get the root directory
root_dir = Path.cwd()

a = Analysis(
    ['email_parser_exe.py'],  # Main entry point wrapper for executable
    pathex=[str(root_dir)],
    binaries=[],
    datas=[
        # Include configuration files
        ('config\\default.yaml', 'config'),
        # Include any additional data files if needed
    ],
    hiddenimports=[
        # Core email_parser modules
        'email_parser',
        'email_parser.cli',
        'email_parser.cli.interactive',
        'email_parser.cli.interactive_file',
        'email_parser.cli.main',
        'email_parser.core',
        'email_parser.core.email_processor',
        'email_parser.core.mime_parser',
        'email_parser.core.component_extractor',
        'email_parser.core.direct_file_converter',
        'email_parser.converters',
        'email_parser.converters.pdf_converter',
        'email_parser.converters.docx_converter',
        'email_parser.converters.excel_converter',
        'email_parser.converters.base_converter',
        'email_parser.config',
        'email_parser.config.config_manager',
        'email_parser.exceptions',
        'email_parser.security',
        'email_parser.security.file_validator',
        'email_parser.utils',
        'email_parser.utils.file_utils',
        'email_parser.utils.logging_utils',
        # Dependencies that might not be detected automatically
        'email_validator',
        'pypdf2',
        'PIL',
        'filetype',
        'openpyxl',
        'pandas',
        'chardet',
        'mistralai',
        'mammoth',
        'bs4',
        'lxml',
        'tiktoken',
        'docx',
        'prompt_toolkit',
        'requests',
        'psutil',
        # Common pandas dependencies
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.hashtable',
        'pandas._libs.properties',
        'pandas._libs.algos',
        'pandas._libs.interval',
        'pandas._libs.join',
        'pandas._libs.lib',
        'pandas._libs.ops',
        'pandas._libs.reduction',
        'pandas._libs.sparse',
        'pandas._libs.tslib',
        'pandas._libs.indexing',
        'pandas._libs.index',
        'pandas._libs.writers',
        'pandas._libs.window',
        'pandas._libs.groupby',
        # Additional hidden imports for tiktoken
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        # XML parsers for lxml
        'lxml.etree',
        'lxml.html',
        # Encodings
        'encodings',
        'encodings.utf_8',
        'encodings.latin_1',
        'encodings.cp1252',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude development dependencies
        'pytest',
        'pytest_cov',
        'black',
        'isort',
        'mypy',
        'bandit',
        'safety',
        'sphinx',
        'sphinx_rtd_theme',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='email-parser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for CLI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',  # Version file (we'll create this)
    icon='resources\\icon.ico' if (root_dir / 'resources' / 'icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='email-parser',
)

# Alternative single-file build (uncomment to use)
# exe_onefile = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.datas,
#     [],
#     name='email-parser-portable',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=True,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
#     version='version_info.txt',
#     icon='resources\\icon.ico' if (root_dir / 'resources' / 'icon.ico').exists() else None,
# )