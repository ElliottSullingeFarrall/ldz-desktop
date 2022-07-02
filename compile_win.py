import PyInstaller.__main__
import os
import shutil

PyInstaller.__main__.run([
    'Record.py',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '-i=stag.ico',
    '--distpath=',
    '--add-data=*.ico;.',
    '--hidden-import=babel.numbers'
])
PyInstaller.__main__.run([
    'Sync.py',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '-i=stag.ico',
    '--distpath=',
    '--add-data=*.ico;.'
])

shutil.rmtree('build')
os.remove('Record.spec')
os.remove('Sync.spec')
print('Done!')