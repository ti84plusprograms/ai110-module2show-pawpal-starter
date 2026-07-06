from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status_and_creates_next_daily_task() -> None:
    task = Task(description="Morning walk", time="08:00", frequency="daily", due_date=date(2026, 7, 6))

    assert task.completion_status is False

    next_task = task.mark_complete()

    assert task.completion_status is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 7)
    assert next_task.completion_status is False


def test_weekly_task_uses_a_seven_day_recurrence() -> None:
    task = Task(description="Grooming", time="09:00", frequency="weekly", due_date=date(2026, 7, 6))

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 13)


def test_scheduler_marks_task_complete_and_appends_next_occurrence() -> None:
    scheduler = Scheduler()
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Feeding", time="08:15", frequency="daily", due_date=date(2026, 7, 6)))
    owner.add_pet(pet)

    next_task = scheduler.mark_task_complete(owner, pet_name="Mochi", task_description="Feeding")

    assert next_task is not None
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completion_status is True
    assert pet.tasks[1].due_date == date(2026, 7, 7)


def test_conflicts_are_reported_as_warnings() -> None:
    scheduler = Scheduler()
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Feeding", time="08:15", frequency="daily", due_date=date(2026, 7, 6)))

    barkley = Pet(name="Barkley", species="dog")
    barkley.add_task(Task(description="Morning walk", time="08:15", frequency="daily", due_date=date(2026, 7, 6)))

    owner.add_pet(mochi)
    owner.add_pet(barkley)

    warnings = scheduler.detect_conflicts(owner)

    assert len(warnings) == 1
    assert "08:15" in warnings[0]
    assert "Mochi: Feeding" in warnings[0]
    assert "Barkley: Morning walk" in warnings[0]


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="cat")
    task = Task(description="Feeding", time="08:15", frequency="daily")

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] == task