from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from ._text import Text


class Module(Text):
    def __init__(self, profile: Profile) -> None:
        super().__init__(profile, label="Module")
