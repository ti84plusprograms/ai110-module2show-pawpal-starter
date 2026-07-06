from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(description="Feeding", time="08:15", frequency="daily"))
    mochi.add_task(Task(description="Medication", time="08:00", frequency="daily"))

    barkley = Pet(name="Barkley", species="dog")
    barkley.add_task(Task(description="Morning walk", time="08:15", frequency="daily"))
    barkley.add_task(Task(description="Brush teeth", time="08:05", frequency="daily"))

    owner.add_pet(mochi)
    owner.add_pet(barkley)
    return owner


def print_schedule(owner: Owner) -> None:
    scheduler = Scheduler()
    schedule = scheduler.get_todays_schedule(owner)

    print(f"Today's Schedule for {owner.name}")
    print()
    for item in schedule:
        status = "done" if item.completion_status else "pending"
        print(f"{item.time}  {item.pet_name}: {item.task_description} ({item.frequency}, {status})")


def print_filtered_views(owner: Owner) -> None:
    scheduler = Scheduler()

    print()
    print("Mochi tasks only")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(owner, pet_name="Mochi")):
        print(f"{task.time.strftime('%H:%M')}  {pet.name}: {task.description}")

    print()
    print("Completed tasks only")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(owner, completion_status=True)):
        print(f"{task.time.strftime('%H:%M')}  {pet.name}: {task.description}")


def print_recurring_demo(owner: Owner) -> None:
    scheduler = Scheduler()
    scheduler.mark_task_complete(owner, pet_name="Mochi", task_description="Medication")

    print()
    print("Recurring tasks after completion")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(owner, pet_name="Mochi")):
        status = "done" if task.completion_status else "pending"
        print(f"{task.due_date.isoformat()}  {task.time.strftime('%H:%M')}  {pet.name}: {task.description} ({task.frequency}, {status})")


def print_conflicts(owner: Owner) -> None:
    scheduler = Scheduler()
    warnings = scheduler.detect_conflicts(owner)

    print()
    print("Conflict warnings")
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("No conflicts found.")


def main() -> None:
    owner = build_demo_owner()
    print_schedule(owner)
    print_filtered_views(owner)
    print_recurring_demo(owner)
    print_conflicts(owner)


if __name__ == "__main__":
    main()