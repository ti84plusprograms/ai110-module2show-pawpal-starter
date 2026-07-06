from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass
class OwnerProfile:
    name: str
    preferred_start_time: time = time(8, 0)
    available_minutes: int = 180


@dataclass
class PetProfile:
    name: str
    species: str
    age: int | None = None
    preferences: list[str] = field(default_factory=list)


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str
    notes: str = ""


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
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[str] = field(default_factory=list)

    def total_scheduled_minutes(self) -> int:
        raise NotImplementedError

    def remaining_minutes(self) -> int:
        raise NotImplementedError


class PawPalScheduler:
    def build_daily_plan(
        self,
        owner: OwnerProfile,
        pet: PetProfile,
        tasks: list[CareTask],
    ) -> DailyPlan:
        raise NotImplementedError