from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from src.options import LOCATIONS

from . import Widget
from ._choose import Choose


class LocationEmbedded(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile, label="Location", values=LOCATIONS, default="Stag Hill"
        )


class LocationRegular(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile, labels=("Format", "Location"), defaults=("In Person", "Stag Hill")
        )
        self.values = (["In Person", "Online"], LOCATIONS)

        self.label0 = ttk.Label(self.profile, text=f"{self.labels[0]}:")
        self.field0 = ttk.Combobox(
            self.profile,
            textvariable=self.vars[0],
            values=self.values[0],
            state="readonly",
            width=10,
        )
        self.label1 = ttk.Label(self.profile, text=f"{self.labels[1]}:")
        self.field1 = ttk.Combobox(
            self.profile,
            textvariable=self.vars[1],
            values=self.values[1],
            state="readonly",
            width=10,
        )

        self.label0.grid(row=self.row, column=0, sticky="e")
        self.field0.grid(row=self.row, column=1, sticky="w")
        self.label1.grid(row=self.row, column=2, sticky="e")
        self.field1.grid(row=self.row, column=3)

        self.field0.bind("<ButtonPress>", self.expand_dropdown)
        self.field1.bind("<ButtonPress>", self.expand_dropdown)

    def update(self, variable: str = "", index: str = "", mode: str = "") -> None:
        self.profile.form[self.labels[0]] = self.vars[0].get()
        if self.vars[0].get() == "In Person":
            # Enable secondary field
            self.field1["state"] = "readonly"
            if self.vars[1].get() == "Online":
                self.vars[1].set("Stag Hill")
        else:
            # Disable secondary field
            self.field1["state"] = "disabled"
            self.vars[1].set("Online")
        self.profile.form[self.labels[1]] = self.vars[1].get()
