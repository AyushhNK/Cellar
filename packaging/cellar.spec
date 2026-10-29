# -*- mode: python ; coding: utf-8 -*-
# Build from the repo root:  pyinstaller packaging/cellar.spec
import os

ROOT = os.path.dirname(SPECPATH)

a = Analysis(
    [os.path.join(ROOT, 'src', 'cellar', '__main__.py')],
    pathex=[os.path.join(ROOT, 'src')],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Cellar',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
