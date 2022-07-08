import PyInstaller.__main__
import os
import shutil
import platform

icons = {"Windows" : "stag.ico", "Darwin" : "stag.icns"}

args_record = [
    "Record.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--argv-emulation",
    "--distpath=",
    f"-i=images/{icons[platform.system()]}",
    f"--add-data=images{os.pathsep}images",
    "--hidden-import=babel.numbers"
]
args_sync = [
    "Sync.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--argv-emulation",
    "--distpath=",
    f"-i=images/{icons[platform.system()]}",
    f"--add-data=images{os.pathsep}images"
]

if platform.system() == 'Windows':
    PyInstaller.__main__.run(args_record)
    PyInstaller.__main__.run(args_sync)
elif platform.system() == 'Darwin':
    PyInstaller.__main__.run(args_record)
else:
    print(f'The {platform.system()} is not supported!')

files = ["Record", "Sync", "Record.spec", "Sync.spec", "build"]
for file in files:
    if os.path.exists(file):
        try:
            os.remove(file)
        except Exception:
            shutil.rmtree(file)
        print(f"{file} removed")
print("Done!")