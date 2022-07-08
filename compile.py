import PyInstaller.__main__
import os
import shutil
import platform

icons = {"Windows" : "stag.ico", "Darwin" : "stag.icns"}

args_run = [
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

PyInstaller.__main__.run(args_run)
PyInstaller.__main__.run(args_sync)

files = ["Record.spec", "Sync.spec", "build"]
for file in files:
    if os.path.exists(file):
        try:
            os.remove(file)
        except Exception:
            shutil.rmtree(file)
        print(f"{file} removed")
print("Done!")