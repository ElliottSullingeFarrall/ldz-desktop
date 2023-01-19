import PyInstaller.__main__ as compiler
import os
import platform

def compile():
    img_ext = {'Windows' : 'ico', 'Darwin' : 'icns'}
    
    try:
        compiler.run([
            'src/source.py',
            '--onefile',
            '--windowed',
            '--noconfirm',
            '--argv-emulation',
            '--name=LDZ',
            f'-i=src/images/stag.{img_ext[platform.system()]}',
            f'--add-data=src/images/stag.png{os.pathsep}images',
            '--hidden-import=babel.numbers'
        ])
        print('Finished Compiling!')
    except KeyError:
        print(f'The platform: {platform.system()} is not supported!')

if __name__ == '__main__':
    compile()