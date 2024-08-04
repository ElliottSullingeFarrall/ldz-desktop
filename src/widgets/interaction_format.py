from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from . import Widget


class InteractionFormat(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(profile, labels=("Online", "Type"), defaults=("No", ""))
        self.values = [
            "Department - synchronous taught",
            "Department - synchronous Q+A",
            "Department - asynchronous (panopto recording)",
            "Discussion Forum",
            "Professional Service",
            "WPO",
        ]

        self.label0 = ttk.Label(self.profile, text=f"{self.labels[0]}:")
        self.field0 = ttk.Checkbutton(
            self.profile, variable=self.vars[0], offvalue="No", onvalue="Yes"
        )
        self.label1 = ttk.Label(self.profile, text=f"{self.labels[1]}:")
        self.field1 = ttk.Combobox(
            self.profile,
            textvariable=self.vars[1],
            values=self.values,
            state="readonly",
            width=10,
        )

        self.label0.grid(row=self.row, column=0, sticky="e")
        self.field0.grid(row=self.row, column=1, sticky="w")
        self.label1.grid(row=self.row, column=2, sticky="e")
        self.field1.grid(row=self.row, column=3, sticky="e")

        self.field1.bind("<ButtonPress>", self.expand_dropdown)
