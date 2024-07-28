"""Module for building app.
"""

from __future__ import annotations

import PyInstaller.__main__ as builder
import os
import platform

IMG_EXT: dict[str, str] = {'Windows' : 'ico', 'Darwin' : 'icns', 'Linux' : 'ico'}

def build():
    """Builds app.
    """    
    try:
        builder.run([
            f'ldz/__init__.py',
            f'--onefile',
            f'--windowed',
            f'--argv-emulation',
            f'--name=ldz',
            f'-i=ldz/assets/stag.{IMG_EXT[platform.system()]}',
            f'--add-data=ldz/assets/stag.png{os.pathsep}assets',
            f'--hidden-import=babel.numbers',
            f'--noconfirm'
        ])
        print('Done!')
    except KeyError:
        print(f'The platform: {platform.system()} is not supported!')

if __name__ == '__main__':
    build()