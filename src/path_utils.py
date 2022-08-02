import os
import sys

def set_app_path():
    path = os.path.dirname(sys.argv[0])
    os.chdir(path)
    while '.app' in path:
        app = path
        path = os.path.dirname(path)
        os.chdir(path)
    return app

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)