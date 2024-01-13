"""Module for compiling app.
"""

from __future__ import annotations

import PyInstaller.__main__ as compiler
import os
import platform

IMG_EXT: dict[str, str]  = {'Windows' : 'ico', 'Darwin' : 'icns', 'Linux' : 'ico'}

def compile():
    """Compiles app.
    """    
    try:
        compiler.run([
            f'ldz/source.py',
            f'--onefile',
            f'--windowed',
            f'--argv-emulation',
            f'--name=ldz',
            f'--distpath=dist/{platform.system()}',
            f'-i=ldz/images/stag.{IMG_EXT[platform.system()]}',
            f'--add-data=ldz/images/stag.png{os.pathsep}images',
            f'--hidden-import=babel.numbers',
            f'--noconfirm'
        ])
        print('Done!')
    except KeyError:
        print(f'The platform: {platform.system()} is not supported!')

if __name__ == '__main__':
    compile()