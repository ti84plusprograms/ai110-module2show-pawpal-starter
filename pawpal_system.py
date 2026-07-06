from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Iterable


def _parse_time(value: time | str) -> time:
    """Convert a time string into a time object."""
    if isinstance(value, time):
        return value
    return datetime.strptime(value, "%H:%M").time()


def _format_time(value: time) -> str:
    """Format a time object as HH:MM."""
    return value.strftime("%H:%M")


def _parse_date(value: date | str | None) -> date:
    """Convert a date string into a date object, defaulting to today."""
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass
class Task:
    description: str
    time: time | str
    frequency: str = "once"
    completion_status: bool = False
    due_date: date | str | None = None

    def __post_init__(self) -> None:
        """Normalize the task time value after initialization."""
        self.time = _parse_time(self.time)
        self.due_date = _parse_date(self.due_date)

    def _recurrence_delta(self) -> timedelta | None:
        """Return the recurrence interval for daily and weekly tasks."""
        frequency = self.frequency.lower()
        if frequency == "daily":
            return timedelta(days=1)
        if frequency == "weekly":
            return timedelta(days=7)
        return None

    def create_next_occurrence(self) -> Task | None:
        """Create the next due task for recurring items."""
        delta = self._recurrence_delta()
        if delta is None:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            completion_status=False,
            due_date=self.due_date + delta,
        )

    def mark_complete(self) -> Task | None:
        """Mark this task complete and return the next recurring task, if any."""
        if self.completion_status:
            return None
        self.completion_status = True
        return self.create_next_occurrence()


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
    due_date: str
    frequency: str
    completion_status: bool


class Scheduler:
    def sort_by_time(self, tasks: Iterable[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort tasks by time and use pet name and description as tie-breakers."""
        return sorted(tasks, key=lambda item: (item[1].time, item[0].name, item[1].description))

    def filter_tasks(
        self,
        owner: Owner,
        *,
        pet_name: str | None = None,
        completion_status: bool | None = None,
        due_date: date | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet name, completion status, or due date."""
        tasks = owner.get_all_tasks()
        filtered_tasks: list[tuple[Pet, Task]] = []
        for pet, task in tasks:
            if pet_name is not None and pet.name != pet_name:
                continue
            if completion_status is not None and task.completion_status != completion_status:
                continue
            if due_date is not None and task.due_date != due_date:
                continue
            filtered_tasks.append((pet, task))
        return filtered_tasks

    def mark_task_complete(self, owner: Owner, pet_name: str, task_description: str) -> Task | None:
        """Mark a matching task complete and append its next recurring copy."""
        for pet, task in owner.get_all_tasks():
            if pet.name != pet_name or task.description != task_description:
                continue
            next_task = task.mark_complete()
            if next_task is not None:
                pet.add_task(next_task)
            return next_task
        return None

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return warning strings for tasks that share an exact same-day time."""
        grouped_tasks: dict[tuple[date, time], list[tuple[Pet, Task]]] = defaultdict(list)
        for pet, task in self.filter_tasks(owner, due_date=date.today()):
            grouped_tasks[(task.due_date, task.time)].append((pet, task))

        warnings: list[str] = []
        for (task_date, task_time), tasks in sorted(grouped_tasks.items(), key=lambda item: item[0]):
            if len(tasks) < 2:
                continue

            task_list = ", ".join(f"{pet.name}: {task.description}" for pet, task in tasks)
            warnings.append(
                f"Warning: {len(tasks)} tasks are scheduled at {task_time.strftime('%H:%M')} on {task_date.isoformat()}: {task_list}"
            )
        return warnings

    def build_schedule(self, owner: Owner) -> list[ScheduledItem]:
        """Build today's ordered schedule from tasks due on the current date."""
        today = date.today()
        ordered_tasks = self.sort_by_time(self.filter_tasks(owner, due_date=today))
        return [
            ScheduledItem(
                pet_name=pet.name,
                task_description=task.description,
                time=_format_time(task.time),
                due_date=task.due_date.isoformat(),
                frequency=task.frequency,
                completion_status=task.completion_status,
            )
            for pet, task in ordered_tasks
        ]

    def get_todays_schedule(self, owner: Owner) -> list[ScheduledItem]:
        """Return the current day's schedule in display-friendly records."""
        return self.build_schedule(owner)


# Backwards-compatible aliases for the later Streamlit implementation.
OwnerProfile = Owner
PetProfile = Pet
CareTask = Task
DailyPlan = list[ScheduledItem]
PawPalScheduler = Scheduler