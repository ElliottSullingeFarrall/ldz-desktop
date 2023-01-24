import PyInstaller.__main__ as compiler
import os
import platform

IMG_EXT = {'Windows' : 'ico', 'Darwin' : 'icns'}

def compile():
    try:
        compiler.run([
            f'src/source.py',
            f'--onefile',
            f'--windowed',
            f'--arv-emulation',
            f'--name=LDZ',
            f'-i=src/images/stag.{IMG_EXT[platform.system()]}',
            f'--add-data=src/images/stag.png{os.pathsep}images',
            f'--hidden-import=babel.numbers',
            f'--noconfirm'
        ])
        print('Done!')
    except KeyError:
        print(f'The platform: {platform.system()} is not supported!')

if __name__ == '__main__':
    compile()