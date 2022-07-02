import PyInstaller.__main__
import os
import shutil
import platform

print(platform.system())

if platform.system() == 'Windows':
    PyInstaller.__main__.run([
        'Record.py',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '-i=stag.ico',
        '--distpath=',
        '--add-data=*.ico;.',
        '--hidden-import=babel.numbers',
        '--enable-shared'
    ])
    PyInstaller.__main__.run([
        'Sync.py',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '-i=stag.ico',
        '--distpath=',
        '--add-data=*.ico;.',
        '--enable-shared'
    ])
else:
    PyInstaller.__main__.run([
        'Record.py',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '-i=stag.icns',
        '--distpath=',
        '--add-data=*.icns:.',
        '--hidden-import=babel.numbers',
        '--enable-framework'
    ])
    PyInstaller.__main__.run([
        'Sync.py',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '-i=stag.icns',
        '--distpath=',
        '--add-data=*.icns:.',
        '--enable-framework'
    ])
    shutil.rmtree('Record.app')
    shutil.rmtree('Sync.app')

shutil.rmtree('build')
os.remove('Record.spec')
os.remove('Sync.spec')
print('Done!')