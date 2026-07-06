import pytest

from scheduler import CareTask, OwnerProfile, PawPalScheduler, PetProfile


def test_scheduler_orders_high_priority_before_lower_priority() -> None:
    scheduler = PawPalScheduler()
    owner = OwnerProfile(name="Jordan", preferred_start_time="08:00", available_minutes=90)
    pet = PetProfile(name="Mochi", species="cat")
    tasks = [
        CareTask(title="Playtime", duration_minutes=20, priority="low"),
        CareTask(title="Medication", duration_minutes=10, priority="high"),
        CareTask(title="Feeding", duration_minutes=15, priority="high"),
    ]

    plan = scheduler.build_daily_plan(owner, pet, tasks)

    assert [task.title for task in plan.scheduled_tasks] == ["Medication", "Feeding", "Playtime"]
    assert plan.scheduled_tasks[0].start_time == "08:00"
    assert plan.scheduled_tasks[1].start_time == "08:10"


def test_scheduler_skips_tasks_that_do_not_fit() -> None:
    scheduler = PawPalScheduler()
    owner = OwnerProfile(name="Jordan", preferred_start_time="09:00", available_minutes=25)
    pet = PetProfile(name="Mochi", species="dog")
    tasks = [
        CareTask(title="Morning walk", duration_minutes=20, priority="high"),
        CareTask(title="Brushing", duration_minutes=15, priority="medium"),
    ]

    plan = scheduler.build_daily_plan(owner, pet, tasks)

    assert [task.title for task in plan.scheduled_tasks] == ["Morning walk"]
    assert len(plan.skipped_tasks) == 1
    assert "Brushing" in plan.skipped_tasks[0]


def test_shorter_task_wins_tie_within_same_priority() -> None:
    scheduler = PawPalScheduler()
    owner = OwnerProfile(name="Jordan", preferred_start_time="08:00", available_minutes=120)
    pet = PetProfile(name="Mochi", species="dog")
    tasks = [
        CareTask(title="Long walk", duration_minutes=45, priority="high"),
        CareTask(title="Quick meds", duration_minutes=5, priority="high"),
    ]

    plan = scheduler.build_daily_plan(owner, pet, tasks)

    assert [task.title for task in plan.scheduled_tasks] == ["Quick meds", "Long walk"]


def test_scheduled_end_times_and_totals_are_consistent() -> None:
    scheduler = PawPalScheduler()
    owner = OwnerProfile(name="Jordan", preferred_start_time="08:00", available_minutes=60)
    pet = PetProfile(name="Mochi", species="cat")
    tasks = [
        CareTask(title="Feeding", duration_minutes=15, priority="high"),
        CareTask(title="Play", duration_minutes=10, priority="medium"),
    ]

    plan = scheduler.build_daily_plan(owner, pet, tasks)

    assert plan.scheduled_tasks[0].end_time == "08:15"
    assert plan.scheduled_tasks[1].start_time == "08:15"
    assert plan.total_scheduled_minutes == 25
    assert plan.remaining_minutes == 35


def test_each_scheduled_task_has_an_explanation() -> None:
    scheduler = PawPalScheduler()
    owner = OwnerProfile(name="Jordan", preferred_start_time="08:00", available_minutes=60)
    pet = PetProfile(name="Mochi", species="dog")
    tasks = [CareTask(title="Walk", duration_minutes=20, priority="high")]

    plan = scheduler.build_daily_plan(owner, pet, tasks)

    assert plan.scheduled_tasks[0].reason
    assert "high" in plan.scheduled_tasks[0].reason


def test_empty_task_list_produces_empty_plan() -> None:
    scheduler = PawPalScheduler()
    owner = OwnerProfile(name="Jordan", preferred_start_time="08:00", available_minutes=60)
    pet = PetProfile(name="Mochi", species="cat")

    plan = scheduler.build_daily_plan(owner, pet, [])

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_scheduled_minutes == 0


def test_invalid_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        CareTask(title="Bad", duration_minutes=0, priority="high")
    with pytest.raises(ValueError):
        CareTask(title="Bad", duration_minutes=10, priority="urgent")
    with pytest.raises(ValueError):
        OwnerProfile(name="Jordan", available_minutes=0)