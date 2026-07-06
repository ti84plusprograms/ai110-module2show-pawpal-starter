from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Sequence


PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def _normalize_time(start_time: time | str) -> time:
    if isinstance(start_time, time):
        return start_time
    return datetime.strptime(start_time, "%H:%M").time()


def _format_time(value: datetime) -> str:
    return value.strftime("%H:%M")


@dataclass
class OwnerProfile:
    name: str
    preferred_start_time: time | str = "08:00"
    available_minutes: int = 180

    def __post_init__(self) -> None:
        self.preferred_start_time = _normalize_time(self.preferred_start_time)
        if self.available_minutes <= 0:
            raise ValueError("available_minutes must be positive")


@dataclass
class PetProfile:
    name: str
    species: str


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str
    notes: str = ""

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_ORDER:
            raise ValueError(f"priority must be one of {', '.join(PRIORITY_ORDER)}")


@dataclass
class ScheduledTask:
    title: str
    start_time: str
    end_time: str
    duration_minutes: int
    priority: str
    reason: str


@dataclass
class DailyPlan:
    owner_name: str
    pet_name: str
    species: str
    start_time: str
    available_minutes: int
    scheduled_tasks: list[ScheduledTask]
    skipped_tasks: list[str]

    @property
    def total_scheduled_minutes(self) -> int:
        return sum(task.duration_minutes for task in self.scheduled_tasks)

    @property
    def remaining_minutes(self) -> int:
        return self.available_minutes - self.total_scheduled_minutes


class PawPalScheduler:
    def build_daily_plan(
        self,
        owner: OwnerProfile,
        pet: PetProfile,
        tasks: Sequence[CareTask],
    ) -> DailyPlan:
        ordered_tasks = sorted(
            enumerate(tasks),
            key=lambda item: (
                PRIORITY_ORDER[item[1].priority],
                item[1].duration_minutes,
                item[0],
            ),
        )

        current_time = datetime.combine(datetime.today(), owner.preferred_start_time)
        remaining_minutes = owner.available_minutes
        scheduled_tasks: list[ScheduledTask] = []
        skipped_tasks: list[str] = []

        for _, task in ordered_tasks:
            if task.duration_minutes > remaining_minutes:
                skipped_tasks.append(
                    f"{task.title} was skipped because it needs {task.duration_minutes} min "
                    f"and only {remaining_minutes} min remained."
                )
                continue

            task_start = _format_time(current_time)
            current_time += timedelta(minutes=task.duration_minutes)
            task_end = _format_time(current_time)
            remaining_minutes -= task.duration_minutes

            scheduled_tasks.append(
                ScheduledTask(
                    title=task.title,
                    start_time=task_start,
                    end_time=task_end,
                    duration_minutes=task.duration_minutes,
                    priority=task.priority,
                    reason=(
                        f"Selected because it is {task.priority} priority and fits within "
                        f"the remaining time budget."
                    ),
                )
            )

        return DailyPlan(
            owner_name=owner.name,
            pet_name=pet.name,
            species=pet.species,
            start_time=_format_time(datetime.combine(datetime.today(), owner.preferred_start_time)),
            available_minutes=owner.available_minutes,
            scheduled_tasks=scheduled_tasks,
            skipped_tasks=skipped_tasks,
        )