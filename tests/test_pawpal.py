from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status() -> None:
    task = Task(description="Morning walk", time="08:00", frequency="daily")

    assert task.completion_status is False

    task.mark_complete()

    assert task.completion_status is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="cat")
    task = Task(description="Feeding", time="08:15", frequency="daily")

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] == task