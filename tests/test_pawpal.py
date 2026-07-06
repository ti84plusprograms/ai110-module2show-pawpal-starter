from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def _owner_with(*pets: Pet) -> Owner:
    owner = Owner(name="Jordan")
    for pet in pets:
        owner.add_pet(pet)
    return owner


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


# ---------------------------------------------------------------------------
# Required coverage: sorting, recurrence, conflict detection
# ---------------------------------------------------------------------------


def test_sort_by_time_returns_tasks_in_chronological_order() -> None:
    """Sorting Correctness: tasks come back in ascending time order."""
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Dinner", time="18:00", due_date=date(2026, 7, 6)))
    pet.add_task(Task(description="Medication", time="08:00", due_date=date(2026, 7, 6)))
    pet.add_task(Task(description="Lunch", time="12:30", due_date=date(2026, 7, 6)))
    owner = _owner_with(pet)

    ordered = scheduler.sort_by_time(owner.get_all_tasks())
    times = [task.time for _, task in ordered]

    assert times == [time(8, 0), time(12, 30), time(18, 0)]
    assert times == sorted(times)


def test_sort_by_time_breaks_ties_by_pet_name_then_description() -> None:
    """Equal times sort deterministically by pet name, then description."""
    scheduler = Scheduler()
    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Feeding", time="08:15", due_date=date(2026, 7, 6)))
    barkley = Pet(name="Barkley", species="dog")
    barkley.add_task(Task(description="Morning walk", time="08:15", due_date=date(2026, 7, 6)))
    owner = _owner_with(mochi, barkley)

    ordered = scheduler.sort_by_time(owner.get_all_tasks())
    labels = [(pet.name, task.description) for pet, task in ordered]

    assert labels == [("Barkley", "Morning walk"), ("Mochi", "Feeding")]


def test_marking_daily_task_complete_creates_task_for_following_day() -> None:
    """Recurrence Logic: completing a daily task yields the next day's task."""
    task = Task(description="Feeding", time="08:00", frequency="daily", due_date=date(2026, 7, 6))

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 7)
    assert next_task.description == "Feeding"
    assert next_task.time == time(8, 0)
    assert next_task.frequency == "daily"
    assert next_task.completion_status is False


def test_detect_conflicts_flags_duplicate_times() -> None:
    """Conflict Detection: two tasks at the same time on the same day are flagged."""
    scheduler = Scheduler()
    today = date.today()
    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Feeding", time="08:15", due_date=today))
    barkley = Pet(name="Barkley", species="dog")
    barkley.add_task(Task(description="Morning walk", time="08:15", due_date=today))
    owner = _owner_with(mochi, barkley)

    warnings = scheduler.detect_conflicts(owner)

    assert len(warnings) == 1
    assert "08:15" in warnings[0]
    assert "Mochi: Feeding" in warnings[0]
    assert "Barkley: Morning walk" in warnings[0]


def test_detect_conflicts_ignores_distinct_times() -> None:
    """Different times on the same day produce no conflict warning."""
    scheduler = Scheduler()
    today = date.today()
    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Feeding", time="08:15", due_date=today))
    mochi.add_task(Task(description="Medication", time="08:00", due_date=today))
    owner = _owner_with(mochi)

    assert scheduler.detect_conflicts(owner) == []


# ---------------------------------------------------------------------------
# Recurrence edge cases
# ---------------------------------------------------------------------------


def test_marking_complete_twice_does_not_create_a_second_occurrence() -> None:
    """mark_complete is idempotent: a second call returns None, adds nothing."""
    task = Task(description="Feeding", time="08:00", frequency="daily", due_date=date(2026, 7, 6))

    assert task.mark_complete() is not None
    assert task.mark_complete() is None


@pytest.mark.parametrize("frequency", ["once", "monthly", "annually", ""])
def test_non_recurring_frequency_produces_no_next_task(frequency: str) -> None:
    """Only daily/weekly recur; anything else yields no next occurrence."""
    task = Task(description="Vet visit", time="10:00", frequency=frequency, due_date=date(2026, 7, 6))

    assert task.mark_complete() is None


def test_daily_recurrence_rolls_over_month_boundary() -> None:
    task = Task(description="Feeding", time="08:00", frequency="daily", due_date=date(2026, 7, 31))

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2026, 8, 1)


def test_frequency_matching_is_case_insensitive() -> None:
    task = Task(description="Feeding", time="08:00", frequency="DAILY", due_date=date(2026, 7, 6))

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 7)


# ---------------------------------------------------------------------------
# Scheduler.mark_task_complete matching behavior
# ---------------------------------------------------------------------------


def test_mark_task_complete_returns_none_when_nothing_matches() -> None:
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Feeding", time="08:00", frequency="daily", due_date=date(2026, 7, 6)))
    owner = _owner_with(pet)

    assert scheduler.mark_task_complete(owner, pet_name="Nobody", task_description="Feeding") is None
    assert scheduler.mark_task_complete(owner, pet_name="Mochi", task_description="Nap") is None
    assert len(pet.tasks) == 1
    assert pet.tasks[0].completion_status is False


def test_mark_task_complete_only_affects_the_matching_pet() -> None:
    scheduler = Scheduler()
    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Feeding", time="08:00", frequency="daily", due_date=date(2026, 7, 6)))
    barkley = Pet(name="Barkley", species="dog")
    barkley.add_task(Task(description="Feeding", time="08:00", frequency="daily", due_date=date(2026, 7, 6)))
    owner = _owner_with(mochi, barkley)

    scheduler.mark_task_complete(owner, pet_name="Mochi", task_description="Feeding")

    assert mochi.tasks[0].completion_status is True
    assert len(mochi.tasks) == 2
    assert barkley.tasks[0].completion_status is False
    assert len(barkley.tasks) == 1


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_by_pet_name_and_completion_status_combine() -> None:
    scheduler = Scheduler()
    mochi = Pet(name="Mochi", species="cat")
    done = Task(description="Feeding", time="08:00", due_date=date(2026, 7, 6))
    done.mark_complete()
    mochi.add_task(done)
    mochi.add_task(Task(description="Medication", time="09:00", due_date=date(2026, 7, 6)))
    barkley = Pet(name="Barkley", species="dog")
    barkley.add_task(Task(description="Walk", time="08:00", due_date=date(2026, 7, 6)))
    owner = _owner_with(mochi, barkley)

    result = scheduler.filter_tasks(owner, pet_name="Mochi", completion_status=True)

    assert [task.description for _, task in result] == ["Feeding"]


def test_filter_completion_status_false_means_pending_only_not_no_filter() -> None:
    """completion_status=False filters to pending; None means no filter."""
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="cat")
    done = Task(description="Feeding", time="08:00", due_date=date(2026, 7, 6))
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task(description="Medication", time="09:00", due_date=date(2026, 7, 6)))
    owner = _owner_with(pet)

    pending = scheduler.filter_tasks(owner, completion_status=False)
    everything = scheduler.filter_tasks(owner, completion_status=None)

    assert [task.description for _, task in pending] == ["Medication"]
    assert len(everything) == 2


def test_filter_by_due_date() -> None:
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Feeding", time="08:00", due_date=date(2026, 7, 6)))
    pet.add_task(Task(description="Grooming", time="09:00", due_date=date(2026, 7, 7)))
    owner = _owner_with(pet)

    result = scheduler.filter_tasks(owner, due_date=date(2026, 7, 7))

    assert [task.description for _, task in result] == ["Grooming"]


# ---------------------------------------------------------------------------
# Conflict detection edge cases (documents current behavior)
# ---------------------------------------------------------------------------


def test_conflict_detection_lists_all_tasks_in_a_three_way_pileup() -> None:
    scheduler = Scheduler()
    today = date.today()
    owner = _owner_with(
        Pet(name="A", species="cat", tasks=[Task(description="t1", time="08:00", due_date=today)]),
        Pet(name="B", species="dog", tasks=[Task(description="t2", time="08:00", due_date=today)]),
        Pet(name="C", species="bird", tasks=[Task(description="t3", time="08:00", due_date=today)]),
    )

    warnings = scheduler.detect_conflicts(owner)

    assert len(warnings) == 1
    assert "3 tasks" in warnings[0]
    for label in ("A: t1", "B: t2", "C: t3"):
        assert label in warnings[0]


def test_conflict_detection_flags_future_dates_too() -> None:
    """Conflicts are detected on any date, not just today."""
    scheduler = Scheduler()
    tomorrow = date.today() + timedelta(days=1)
    owner = _owner_with(
        Pet(name="A", species="cat", tasks=[Task(description="t1", time="08:00", due_date=tomorrow)]),
        Pet(name="B", species="dog", tasks=[Task(description="t2", time="08:00", due_date=tomorrow)]),
    )

    warnings = scheduler.detect_conflicts(owner)

    assert len(warnings) == 1
    assert tomorrow.isoformat() in warnings[0]


def test_conflict_detection_reports_each_conflicting_date_separately() -> None:
    """A same-time collision on two different dates yields two warnings."""
    scheduler = Scheduler()
    today = date.today()
    tomorrow = today + timedelta(days=1)
    owner = _owner_with(
        Pet(name="A", species="cat", tasks=[
            Task(description="t1", time="08:00", due_date=today),
            Task(description="t3", time="08:00", due_date=tomorrow),
        ]),
        Pet(name="B", species="dog", tasks=[
            Task(description="t2", time="08:00", due_date=today),
            Task(description="t4", time="08:00", due_date=tomorrow),
        ]),
    )

    warnings = scheduler.detect_conflicts(owner)

    assert len(warnings) == 2
    assert any(today.isoformat() in w for w in warnings)
    assert any(tomorrow.isoformat() in w for w in warnings)


def test_completed_task_is_excluded_from_conflicts() -> None:
    """A completed task no longer competes, so it does not create a conflict."""
    scheduler = Scheduler()
    today = date.today()
    done = Task(description="Feeding", time="08:15", due_date=today)
    done.mark_complete()
    owner = _owner_with(
        Pet(name="Mochi", species="cat", tasks=[done]),
        Pet(name="Barkley", species="dog", tasks=[Task(description="Walk", time="08:15", due_date=today)]),
    )

    assert scheduler.detect_conflicts(owner) == []


# ---------------------------------------------------------------------------
# build_schedule
# ---------------------------------------------------------------------------


def test_build_schedule_returns_todays_tasks_in_time_order() -> None:
    scheduler = Scheduler()
    today = date.today()
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(description="Dinner", time="18:00", due_date=today))
    pet.add_task(Task(description="Breakfast", time="08:00", due_date=today))
    pet.add_task(Task(description="Tomorrow", time="07:00", due_date=today + timedelta(days=1)))
    owner = _owner_with(pet)

    schedule = scheduler.get_todays_schedule(owner)

    assert [item.task_description for item in schedule] == ["Breakfast", "Dinner"]
    assert [item.time for item in schedule] == ["08:00", "18:00"]


def test_build_schedule_is_empty_for_owner_without_tasks() -> None:
    scheduler = Scheduler()
    owner = _owner_with(Pet(name="Mochi", species="cat"))

    assert scheduler.get_todays_schedule(owner) == []
    assert scheduler.detect_conflicts(owner) == []


# ---------------------------------------------------------------------------
# Input parsing / normalization
# ---------------------------------------------------------------------------


def test_string_and_object_inputs_normalize_equivalently() -> None:
    from_strings = Task(description="Feeding", time="08:15", due_date="2026-07-06")
    from_objects = Task(description="Feeding", time=time(8, 15), due_date=date(2026, 7, 6))

    assert from_strings.time == from_objects.time == time(8, 15)
    assert from_strings.due_date == from_objects.due_date == date(2026, 7, 6)


def test_missing_due_date_defaults_to_today() -> None:
    task = Task(description="Feeding", time="08:00")

    assert task.due_date == date.today()


@pytest.mark.parametrize("bad_time", ["25:00", "", "noon", "08:60"])
def test_invalid_time_string_raises(bad_time: str) -> None:
    with pytest.raises(ValueError):
        Task(description="Feeding", time=bad_time, due_date=date(2026, 7, 6))


def test_invalid_date_string_raises() -> None:
    with pytest.raises(ValueError):
        Task(description="Feeding", time="08:00", due_date="07/06/2026")