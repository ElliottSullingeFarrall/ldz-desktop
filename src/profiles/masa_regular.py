from __future__ import annotations

from src.widgets.appointment import Appointment
from src.widgets.date import Date
from src.widgets.department import Department
from src.widgets.level import Level
from src.widgets.location import LocationRegular
from src.widgets.notes import Notes
from src.widgets.students import StudentsRegular
from src.widgets.times import Times
from src.widgets.topic import Topic1MASA, Topic2MASA

from . import Profile


class RegMASA(Profile):
    name = "MASA"

    def layout(self) -> None:
        Date(self)
        Times(self)
        Department(self)
        Topic1MASA(self)
        Topic2MASA(self)
        Level(self)
        LocationRegular(self)
        Appointment(self)
        StudentsRegular(self)
        Notes(self)
        super().layout()
