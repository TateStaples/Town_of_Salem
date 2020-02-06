# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src/main/python/main.py'],
             pathex=['/Users/22staples/PycharmProjects/Town_of_Salem'],
             binaries=[],
             datas=[('path/libshiboken2.abi3.5.12.dylib', '**./libshiboken2.abi3.5.12.dylib')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir='made_up',
          console=True )
