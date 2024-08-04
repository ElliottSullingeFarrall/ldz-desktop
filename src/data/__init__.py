from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Tuple

if TYPE_CHECKING:
    from src.profiles import Profile

import os

import pandas as pd

from src.config import DATA_DIR


class Data:
    def __init__(self, profile: Profile) -> None:
        self.profile = profile

        self.filename = os.path.join(DATA_DIR, self.profile.name + os.extsep + "csv")
        try:
            # Load data from file
            self.data = pd.read_csv(self.filename, dtype=str, na_filter=False)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            # Create empty data
            self.data = pd.DataFrame(columns=list(self.profile.form.keys()))

    @property
    def keys(self) -> Tuple[str, ...]:
        return tuple(self.data.columns)

    @property
    def rows(self) -> Tuple[Any, ...]:
        return tuple(tuple(series.values) for _, series in self.data.iterrows())

    def append(self, data: List[pd.DataFrame]) -> None:
        self.data = pd.concat([self.data] + data)

    def remove(self, index: int) -> None:
        self.data = self.data.drop(index)
        self.data = self.data.reset_index(drop=True)

    def clear(self) -> None:
        self.data = pd.DataFrame(columns=list(self.profile.form.keys()))

    def save(self):
        self.data.to_csv(self.filename, index=False)

    def submit(self) -> None:
        self.data = pd.concat(
            [self.data, pd.DataFrame([self.profile.form])], ignore_index=True
        )

    def import_data(self, paths: Tuple[str, ...]) -> None:
        self.append([pd.read_excel(path, dtype=str, na_filter=False) for path in paths])

    def export_data(self, path: str) -> None:
        self.data.to_excel(path, index=False)
