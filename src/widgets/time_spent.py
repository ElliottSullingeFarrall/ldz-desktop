from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from . import Widget


class TimeSpent(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile, labels=("Session", "Preparation"), defaults=("0.25", "0.50")
        )
        self.values = (
            [f"{0.25*i:.2f}" for i in range(1, 11)],
            [f"{0.50*i:.2f}" for i in range(1, 11)],
        )

        frame = ttk.Frame(self.profile)
        frame.grid(row=self.row, column=1, sticky="ew", columnspan=3)
        frame.grid_columnconfigure(tuple(range(4)), weight=1)

        self.labelf = ttk.Label(self.profile, text="Time (Hours) ")
        self.label0 = ttk.Label(frame, text=f"{self.labels[0]}:")
        self.field0 = ttk.Spinbox(
            frame,
            textvariable=self.vars[0],
            values=self.values[0],
            validate="focusout",
            validatecommand=((self.profile.register(self.validate)), "0", "%P", "%W"),
            width=4,
        )
        self.label1 = ttk.Label(frame, text=f"{self.labels[1]}:")
        self.field1 = ttk.Spinbox(
            frame,
            textvariable=self.vars[1],
            values=self.values[1],
            validate="focusout",
            validatecommand=((self.profile.register(self.validate)), "1", "%P", "%W"),
            width=4,
        )

        self.labelf.grid(row=self.row, column=0, sticky="e")
        self.label0.grid(row=0, column=0, sticky="w")
        self.field0.grid(row=0, column=1, sticky="w")
        self.label1.grid(row=0, column=2, sticky="e")
        self.field1.grid(row=0, column=3, sticky="e")

    def validate(self, idx: str, P: str, W: str) -> bool:
        if P in self.values[int(idx)]:
            return True
        else:
            try:
                self.profile.nametowidget(W).set(
                    self.values[int(idx)][
                        min(
                            range(len(self.values[int(idx)])),
                            key=lambda i: abs(
                                float(self.values[int(idx)][i]) - float(P)
                            ),
                        )
                    ]
                )
            except ValueError:
                self.profile.nametowidget(W).set(self.values[int(idx)][0])
            return False
