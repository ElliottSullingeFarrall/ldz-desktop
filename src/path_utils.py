import os
import sys

def get_app_name():
    app = sys.argv[0]
    path = os.path.dirname(app)
    os.chdir(path)
    while '.app' in path:
        app = path
        path = os.path.dirname(app)
        os.chdir(path)
    return os.path.splitext(os.path.basename(app))[0]

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)