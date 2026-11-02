# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('frontend', 'frontend')]
binaries = []
hiddenimports = ['starlette.routing', 'starlette.middleware', 'starlette.staticfiles', 'starlette.responses', 'starlette.background', 'anyio', 'anyio._backends._asyncio', 'anyio._backends._trio']
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('multipart')
hiddenimports += collect_submodules('python_multipart')
tmp_ret = collect_all('pymupdf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDFSpanRemover',
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
