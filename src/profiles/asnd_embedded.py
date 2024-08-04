from __future__ import annotations

from src.widgets.assessment import Assessment
from src.widgets.contextualisation import Contextualisation
from src.widgets.date import Date
from src.widgets.department import Department
from src.widgets.interaction_format import InteractionFormat
from src.widgets.level import Level
from src.widgets.location import LocationEmbedded
from src.widgets.module import Module
from src.widgets.notes import Notes
from src.widgets.resources import Resources
from src.widgets.staff import Staff
from src.widgets.students import StudentsEmbedded
from src.widgets.time_spent import TimeSpent
from src.widgets.topic import Topic1ASND, Topic2ASND
from src.widgets.workshop_name import WorkshopName

from . import Profile


class EmbdASND(Profile):
    name = "AS&D (Embedded)"

    def layout(self) -> None:
        Date(self)
        TimeSpent(self)
        WorkshopName(self)
        Module(self)
        Department(self)
        Topic1ASND(self)
        Topic2ASND(self)
        Level(self)
        LocationEmbedded(self)
        InteractionFormat(self)
        Staff(self)
        Contextualisation(self)
        Assessment(self)
        Resources(self)
        StudentsEmbedded(self)
        Notes(self)
        super().layout()
