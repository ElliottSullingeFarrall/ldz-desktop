from __future__ import annotations

import os
import pathlib
import platform
import sys
import tkinter as tk
import traceback
from importlib.resources import files
from tkinter import ttk

from .config import DATA_DIR
from .profiles.asnd_embedded import EmbdASND
from .profiles.asnd_regular import RegASND
from .profiles.masa_embedded import EmbdMASA
from .profiles.masa_regular import RegMASA

FROZEN = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.title("Select Profile")
        self.iconphoto(True, tk.PhotoImage(file=self.resource_path("assets/stag.png")))
        self.resizable(False, False)
        self.geometry("250x120")

        self.profile = None
        self.profiles = {
            profile.name: profile for profile in (RegASND, RegMASA, EmbdMASA, EmbdASND)
        }

        table = ttk.Treeview(
            self, columns="Profile", show="headings", selectmode="browse"
        )
        for col in table["columns"]:
            table.heading(col, anchor="center", text=col)
            table.column(col, anchor="center", stretch=False, width=250)
        for profile in self.profiles:
            table.insert(parent="", index="end", values=(profile,))
        table.bind("<Motion>", "break")
        table.pack(fill="both", expand=True)

        def select_profile(event: tk.Event) -> None:
            profile_name = table.item(table.focus())["values"][0]
            self.withdraw()
            self.profile = self.profiles[profile_name](self)
            self.profile.mainloop()

        table.bind("<<TreeviewSelect>>", select_profile)

    def resource_path(self, relative_path: str) -> str:
        if FROZEN:
            base_path = sys._MEIPASS  # type: ignore[attr-defined]
        else:
            base_path = str(files("src"))
        return os.path.join(base_path, relative_path)


def get_app_dir(platform: str) -> pathlib.Path:
    path = pathlib.Path(os.getcwd())
    match platform:
        case "Windows":
            # Change working directory to the directory containing the executable
            path = pathlib.Path(sys.argv[0]).parent
        case "Darwin":
            # Change working directory to the directory containing the app bundle
            idx = [
                i
                for i, part in enumerate(pathlib.Path(sys.argv[0]).parts)
                if part.endswith(".app")
            ][0]
            path = pathlib.Path(*pathlib.Path(sys.argv[0]).parts[:idx])
    return path


def dump_error(error: Exception) -> None:
    with open("CRASH.dump", "w") as crash_dump:
        crash_dump.write(traceback.format_exc())
    print("An error occurred. Details have been written to CRASH.dump.")
    sys.exit(1)


def run() -> None:
    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)

    # Set correct working directory
    if FROZEN:
        os.chdir(get_app_dir(platform.system()))

    # Clear old crash dump
    if os.path.exists("CRASH.dump"):
        os.remove("CRASH.dump")

    # Run the application
    try:
        App().mainloop()
    except Exception as error:
        dump_error(error)


if __name__ == "__main__":
    run()
