from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from src.profiles import Profile

import tkinter as tk
from tkinter import font as tkf
from tkinter import messagebox, ttk


class Widget:
    def __init__(
        self,
        profile: Profile,
        labels: Tuple[str, ...] = (),
        defaults: Tuple[str, ...] = (),
        required: bool = True,
    ) -> None:
        self.profile = profile
        self.labels = labels
        self.defaults = defaults
        self.required = required

        self.vars = [tk.StringVar(self.profile, value=default) for default in defaults]
        for var in self.vars:
            var.trace_add("write", self.update)

        self.row = len(self.profile.widgets)
        self.profile.widgets.append(self)

    def update(self, variable: str = "", index: str = "", mode: str = "") -> None:
        for var, name in zip(self.vars, self.labels):
            self.profile.form[name] = var.get()

    def reset(self) -> None:
        for var, default in zip(self.vars, self.defaults):
            var.set(default)

    def expand_dropdown(self, event: tk.Event) -> None:
        combo = event.widget
        style = ttk.Style(combo.master)

        long = max(combo.cget("values"), key=len)

        font = tkf.nametofont(str(combo.cget("font")))
        width = max(0, font.measure(long.strip() + "0") - combo.winfo_width())

        style.configure("TCombobox", postoffset=(0, 0, width, 0))


class Submit:
    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        self.label = "Submit"

        self.row = len(self.profile.widgets)

        button = ttk.Button(profile, text=self.label, command=self.command)
        button.grid(row=self.row, column=0, columnspan=4)

    def command(self) -> None:
        missing_values = False
        for widget in self.profile.widgets:
            for label in widget.labels:
                if not self.profile.form[label] and widget.required:
                    missing_values = True
                    break

        if missing_values:
            messagebox.showinfo(
                parent=self.profile, message="Please fill in all the fields."
            )
        else:
            self.profile.data.submit()
            self.profile.data.save()
            for widget in self.profile.widgets:
                widget.reset()
