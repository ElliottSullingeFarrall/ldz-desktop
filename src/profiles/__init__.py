from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from src import App
    from src.widgets import Widget

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.data import Data
from src.widgets import Submit


class Profile(tk.Tk):
    def __init__(self, app: App) -> None:
        super().__init__()
        self.name: str = "" if not hasattr(self, "name") else self.name
        self.app = app

        self.title(f"{self.name}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        menubar = tk.Menu(self)
        menu_profile = tk.Menu(menubar, tearoff=False)
        menu_profile.add_command(label="Switch Profile", command=self.switch_profile)
        menu_data = tk.Menu(menubar, tearoff=False)
        menu_data.add_command(label="View/Delete Data", command=self.view_data)
        menu_data.add_separator()
        menu_data.add_command(label="Import Data...", command=self.import_data)
        menu_data.add_command(label="Export Data...", command=self.export_data)
        menubar.add_cascade(label="Profile", menu=menu_profile)
        menubar.add_cascade(label="Data", menu=menu_data)
        self.config(menu=menubar)

    def layout(self) -> None:
        Submit(self)

    def mainloop(self, n: int = 0) -> None:
        self.widgets: List[Widget] = []
        self.form: Dict[str, str] = {}

        self.layout()

        for widget in self.widgets:
            widget.update()

        self.data = Data(self)

        super().mainloop()

    def view_data(self) -> None:
        window = tk.Toplevel(self)
        window.title("View Data")
        window.resizable(False, False)
        window.geometry(f"{self.winfo_width()}x{self.winfo_height()}")
        window.attributes("-topmost", "true")
        window.grab_set()

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(0, weight=1)

        table = ttk.Treeview(
            window, columns=self.data.keys, show="headings", selectmode="browse"
        )
        for col in table["columns"]:
            table.heading(col, text=col, anchor="center")
            table.column(col, stretch=False, anchor="center", width=100)
        for row in self.data.rows:
            table.insert(parent="", index="end", values=row)
        table.bind("<Motion>", "break")
        table.grid(row=0, column=0, sticky="ns")

        vsb = ttk.Scrollbar(window, orient="vertical", command=table.yview)
        vsb.grid(row=0, column=1, sticky="ns", rowspan=2)
        table.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(window, orient="horizontal", command=table.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        table.configure(xscrollcommand=hsb.set)

        def delete_data(event: tk.Event) -> None:
            answer = messagebox.askquestion(
                parent=window,
                title="Delete Data",
                message="Are you sure you would like to delete this entry?",
            )
            if answer == "no":
                pass
            else:
                row_num = table.index(*table.selection())
                self.data.remove(row_num)
                self.data.save()
                window.destroy()

        table.bind("<<TreeviewSelect>>", delete_data)

    def import_data(self) -> None:
        paths = filedialog.askopenfilenames(
            parent=self, title="Import Data", filetypes=[("excel files", "*.xlsx")]
        )
        if paths:
            answer = messagebox.askyesnocancel(
                parent=self,
                title="Import Data",
                message="Would you like to clear the existing data? This action cannot be undone!",
            )
            if answer:
                self.data.clear()
            if answer is not None:
                self.data.import_data(paths)

    def export_data(self) -> None:
        path = filedialog.asksaveasfile(
            parent=self,
            title="Export Data",
            filetypes=[("excel files", "*.xlsx")],
            defaultextension="*.xlsx",
            mode="wb",
        )
        if path:
            answer = messagebox.askyesnocancel(
                parent=self,
                title="Export Data",
                message="Would you like to clear the existing data? This action cannot be undone!",
            )
            if answer is not None:
                self.data.export_data(path.name)
            if answer:
                self.data.clear()

    def destroy(self) -> None:
        self.data.save()
        super().destroy()
        self.app.destroy()

    def switch_profile(self) -> None:
        self.data.save()
        super().destroy()
        self.app.deiconify()
