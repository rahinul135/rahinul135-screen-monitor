block_cipher = None

# You can modify this to match your environment
binaries = [('C:\\Program Files\\Python\\Python311\\python311.dll', '.')]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=[
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'mss',
        'pystray',
        'requests',
        'sqlalchemy',
        'jwt',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    PYZ,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='main',
    icon='icon.ico',
)