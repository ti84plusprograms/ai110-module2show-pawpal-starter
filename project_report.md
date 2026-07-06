# PawPal+ Project Report

## Overview

PawPal+ is a Streamlit app that helps a pet owner organize care tasks for one or more pets. The project started from a UML-driven design exercise and evolved into a working scheduling app with a logic layer, a Streamlit UI, tests, recurring-task handling, and lightweight conflict warnings.

## What Was Built

The current implementation includes:

- A domain layer in `pawpal_system.py` with `Owner`, `Pet`, `Task`, `ScheduledItem`, and `Scheduler`.
- A Streamlit UI in `app.py` that keeps the owner object in `st.session_state` so data survives reruns.
- A CLI demo in `main.py` that exercises sorting, filtering, recurring tasks, and conflict detection.
- Tests in `tests/test_pawpal.py` that verify recurrence and conflict behavior.
- Supporting documentation in `README.md`, `reflection.md`, and `diagrams/uml.mmd`.

## Design Summary

The logic layer follows a simple model:

| Class | Responsibility |
|---|---|
| `Task` | Stores a task description, time, frequency, completion state, and due date. |
| `Pet` | Owns a list of tasks. |
| `Owner` | Owns a list of pets and can collect all tasks across pets. |
| `ScheduledItem` | Represents a schedule row for display. |
| `Scheduler` | Sorts, filters, completes, and checks tasks for conflicts. |

The scheduler keeps the implementation lightweight and easy to explain. Tasks are ordered by time, filtered by pet or completion status, recurring tasks generate the next occurrence, and same date-and-time collisions between pending tasks produce warning messages.

## Scheduling Behavior

The implemented scheduler features are:

- **Sorting**: `Scheduler.sort_by_time()` sorts by task time, then pet name, then task description.
- **Filtering**: `Scheduler.filter_tasks()` filters by pet name, completion status, or due date.
- **Recurring tasks**: `Task.mark_complete()` returns a new task for the next occurrence when the task is daily or weekly, and `Scheduler.mark_task_complete()` appends that new task to the pet.
- **Conflict detection**: `Scheduler.detect_conflicts()` returns warning strings when two or more pending tasks share the same date and exact time. It scans every scheduled date (not only today) and ignores completed tasks, since a finished task no longer competes for the owner's attention.

## Verification

Validation was performed with:

```bash
./.venv/bin/python -m py_compile pawpal_system.py main.py tests/test_pawpal.py
./.venv/bin/python -m pytest tests/test_pawpal.py
./.venv/bin/python main.py
```

Results observed during verification:

- The Python files compiled successfully.
- The focused test suite passed.
- The CLI demo showed sorted tasks, filtered task views, recurring-task output, and a conflict warning for same-time tasks.

## Tradeoffs

The scheduler intentionally uses a lightweight conflict strategy: it flags exact same date-and-time matches between pending tasks rather than calculating overlapping durations. That keeps the code simple and the warnings easy to understand, but it means partially overlapping tasks (different start times, overlapping durations) are not detected.

## Reflection

The project went best when each feature stayed small and testable. Sorting, filtering, recurrence, and conflict detection were all easier to implement because they were isolated in `Scheduler` and verified with focused tests.

A useful lesson from the project is that clear method names and small return values make both the Streamlit UI and the CLI demo easier to maintain. The `README.md` and `reflection.md` now match the final behavior of the scheduler.
