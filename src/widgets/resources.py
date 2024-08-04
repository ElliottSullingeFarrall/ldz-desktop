from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from . import Widget


class Resources(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile,
            labels=("Resources", "Applications"),
            defaults=("No", "Not applicable to other workshops"),
        )
        self.values = [
            "Not applicable to other workshops",
            "Is applicable to other workshops",
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

    def update(self, variable: str = "", index: str = "", mode: str = "") -> None:
        self.profile.form[self.labels[0]] = self.vars[0].get()
        if self.vars[0].get() == "No":
            # Disable secondary field
            self.field1["state"] = "disabled"
            self.vars[1].set("N/A")
        else:
            # Enable secondary field
            self.field1["state"] = "readonly"
            if self.vars[1].get() == "N/A":
                self.vars[1].set("Not applicable to other workshops")
        self.profile.form[self.labels[1]] = self.vars[1].get()
