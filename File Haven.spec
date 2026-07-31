# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/file_haven/app.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=['AppKit', 'Foundation'],
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
    [],
    exclude_binaries=True,
    name='File Haven',
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
    icon=['assets/FileHaven.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='File Haven',
)
app = BUNDLE(
    coll,
    name='File Haven.app',
    icon='assets/FileHaven.icns',
    bundle_identifier='com.savelmoshi.filehaven',
)
