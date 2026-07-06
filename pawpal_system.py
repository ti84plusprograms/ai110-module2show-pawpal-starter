from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Iterable


def _parse_time(value: time | str) -> time:
    """Convert a time string into a time object."""
    if isinstance(value, time):
        return value
    return datetime.strptime(value, "%H:%M").time()


def _format_time(value: time) -> str:
    """Format a time object as HH:MM."""
    return value.strftime("%H:%M")


@dataclass
class Task:
    description: str
    time: time | str
    frequency: str = "once"
    completion_status: bool = False

    def __post_init__(self) -> None:
        """Normalize the task time value after initialization."""
        self.time = _parse_time(self.time)

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completion_status = True


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect every task from every pet."""
        tasks: list[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks():
                tasks.append((pet, task))
        return tasks


@dataclass
class ScheduledItem:
    pet_name: str
    task_description: str
    time: str
    frequency: str
    completion_status: bool


class Scheduler:
    def build_schedule(self, owner: Owner) -> list[ScheduledItem]:
        """Build today's schedule from the owner's pets and tasks."""
        tasks = owner.get_all_tasks()
        ordered_tasks = sorted(tasks, key=lambda item: (item[1].time, item[0].name, item[1].description))
        return [
            ScheduledItem(
                pet_name=pet.name,
                task_description=task.description,
                time=_format_time(task.time),
                frequency=task.frequency,
                completion_status=task.completion_status,
            )
            for pet, task in ordered_tasks
        ]

    def get_todays_schedule(self, owner: Owner) -> list[ScheduledItem]:
        """Return the schedule for today."""
        return self.build_schedule(owner)


# Backwards-compatible aliases for the later Streamlit implementation.
OwnerProfile = Owner
PetProfile = Pet
CareTask = Task
DailyPlan = list[ScheduledItem]
PawPalScheduler = Scheduler