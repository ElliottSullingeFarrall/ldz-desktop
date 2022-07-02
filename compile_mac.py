import PyInstaller.__main__
import os
import shutil

PyInstaller.__main__.run([
    'Record.py',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '-i=stag.icns',
    '--distpath=',
    '--add-data=*.icns:.',
    '--hidden-import=babel.numbers'
])
PyInstaller.__main__.run([
    'Sync.py',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '-i=stag.icns',
    '--distpath=',
    '--add-data=*.icns:.'
])

files = ['Record.app', 'Sync.app', 'Record.spec', 'Sync.spec', 'build']
for file in files:
    if os.path.exists(file):
        try:
            os.remove(file)
        except Exception:
            shutil.rmtree(file)
        print(f'{file} removed')
print('Done!')