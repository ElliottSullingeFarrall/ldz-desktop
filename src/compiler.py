import PyInstaller.__main__ as compiler
import os
import platform

def compile():
    img_ext = {'Windows' : 'ico', 'Darwin' : 'icns'}
    
    try:
        compiler.run([
            f'src/source.py',
            f'--onefile',
            f'--windowed',
            f'--name=LDZ',
            f'-i=src/images/stag.{img_ext[platform.system()]}',
            f'--add-data=src/images/stag.png{os.pathsep}images',
            f'--hidden-import=babel.numbers',
            f'--noconfirm'
        ])
        print('Done!')
    except KeyError:
        print(f'The platform: {platform.system()} is not supported!')

if __name__ == '__main__':
    compile()