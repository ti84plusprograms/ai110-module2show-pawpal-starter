# Project Report: PawPal+ Pet Care Scheduler

## Repository Summary

This repo is the Module 2 project **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet. The assignment asks the developer to design the system first (UML), implement the scheduling logic in Python, connect it to the Streamlit UI, write tests for the important scheduling behaviors, and document the work. The starter ships with a placeholder UI in `app.py` and no backend logic.

## Environment Setup

- Created a local virtual environment at `.venv/`.
- Installed dependencies from `requirements.txt` into that environment.
- Key installed packages:
  - `streamlit 1.58.0`
  - `pytest 9.1.1`
  - `altair 6.2.2` (pulled in by Streamlit)
- `.venv/` is ignored by `.gitignore`.

Useful commands:

```bash
python -m venv .venv
source .venv/bin/activate
python -m streamlit run app.py
python -m pytest tests/
```

## Initial Baseline

The starter `app.py` was a thin placeholder: it collected owner/pet/task inputs but the **Generate schedule** button did nothing useful, and there was no backend module or test suite. The first job was to design the domain classes, implement a scheduler, and wire the UI to it.

## Important Files

- `README.md`: Scenario, setup steps, sample output, testing notes, scheduling feature table, and demo walkthrough.
- `app.py`: Streamlit UI. Collects owner/pet/task inputs and renders the generated plan.
- `scheduler.py`: Backend module with the domain classes and the scheduling engine.
- `tests/test_scheduler.py`: Pytest suite covering the key scheduling behaviors.
- `diagrams/uml.mmd`: Mermaid class diagram of the implemented design.
- `reflection.md`: Student reflection (design, tradeoffs, AI collaboration, testing).
- `ai_interactions.md`: Optional log of AI usage.

## Design

The implementation uses six classes with narrow responsibilities:

| Class | Responsibility |
|---|---|
| `OwnerProfile` | Owner name, preferred start time, and available-minutes budget (validates the budget, normalizes the start time) |
| `PetProfile` | Basic pet identity (name, species) |
| `CareTask` | A task to schedule: title, duration, priority, optional notes (validates duration and priority) |
| `ScheduledTask` | A task placed in the plan: concrete start/end times, duration, priority, and a reason |
| `DailyPlan` | Result object holding scheduled + skipped tasks, with computed `total_scheduled_minutes` and `remaining_minutes` |
| `PawPalScheduler` | Sorts tasks and builds the `DailyPlan` |

The scheduler uses a greedy rule: high-priority tasks are scheduled first, then medium, then low. Within the same priority, shorter tasks come first so more work fits into the day, with original order as a stable tiebreaker. Tasks that exceed the remaining time budget are skipped with an explanation.

## Recommended Next Steps (at the outset)

1. Draft a UML class diagram for the domain.
2. Convert it into Python dataclasses in a `scheduler.py` module (input vs. output types separated).
3. Implement `PawPalScheduler.build_daily_plan` with a deterministic sort and a greedy time-budget fit.
4. Have each scheduled task carry a human-readable reason; record skipped tasks with why they were skipped.
5. Wire `app.py` to import from `scheduler.py` and render the plan.
6. Add tests for ordering, skipping, tiebreaking, time math, explanations, empty input, and validation.
7. Run `python -m pytest tests/` until green, then boot the app to verify end to end.
8. Fill in README placeholders, reflection, and the UML diagram to match what was built.

## Completed Fix Log

### Fix Gate 1: Domain Model And Scheduler

Status: implemented and tested.

What changed:

- Added `scheduler.py` with `OwnerProfile`, `PetProfile`, `CareTask`, `ScheduledTask`, `DailyPlan`, and `PawPalScheduler`.
- Separated input types (`CareTask`) from output types (`ScheduledTask`) so the scheduler is a pure transformation.
- Implemented `build_daily_plan`: sort by `(priority, duration, original_index)`, lay tasks back-to-back from the start time, and skip tasks that do not fit the remaining budget.
- Made `total_scheduled_minutes` and `remaining_minutes` computed `@property` values so totals cannot drift from the task list.
- Added validation: positive durations, known priorities, positive available-minutes.

### Fix Gate 2: Streamlit UI Wiring

Status: implemented and tested.

What changed:

- `app.py` imports the domain classes from `scheduler.py`.
- The **Generate schedule** button now builds real `OwnerProfile`/`PetProfile`/`CareTask` objects from the entered data and calls the scheduler.
- Renders the scheduled tasks (start/end, duration, priority, reason) and any skipped tasks with explanations.
- Guards against generating a plan with no tasks.

### Fix Gate 3: Test Suite

Status: implemented and passing.

Tests written in `tests/test_scheduler.py`:

- `test_scheduler_orders_high_priority_before_lower_priority`
- `test_scheduler_skips_tasks_that_do_not_fit`
- `test_shorter_task_wins_tie_within_same_priority`
- `test_scheduled_end_times_and_totals_are_consistent`
- `test_each_scheduled_task_has_an_explanation`
- `test_empty_task_list_produces_empty_plan`
- `test_invalid_inputs_are_rejected`

Pytest result:

```text
7 passed in 0.03s
```

### Fix Gate 4: Documentation

Status: complete.

What changed:

- Filled in `README.md`: sample output, pytest output, the Smarter Scheduling feature table (task sorting, filtering, conflict handling, recurring-task note), and a five-step demo walkthrough.
- Completed `reflection.md` sections 1–5 (design, scheduling tradeoffs, AI collaboration, testing, reflection).
- Confirmed `diagrams/uml.mmd` matches the implemented six-class design (with `DailyPlan` totals as methods).

## Sample Output

```text
Daily plan for Mochi (cat)
Starts at 08:00 with 60 minutes available. Scheduled 25 min, 35 min unused.

Scheduled tasks
  08:00 – 08:10  Medication  (10 min) [high]  — high priority, fits the budget
  08:10 – 08:25  Feeding     (15 min) [high]  — high priority, fits the budget
  08:25 – 08:45  Playtime    (20 min) [low]   — low priority, still fits

Skipped tasks
  Brushing was skipped because it needs 15 min and only 5 min remained.
```

## Final Verification

Status: complete.

Checks run:

- `.venv/bin/python -m pytest tests/`
- `.venv/bin/python -m py_compile app.py scheduler.py tests/test_scheduler.py`
- `.venv/bin/python -m streamlit run app.py --server.headless true --server.port 8503`

Results:

- Pytest passed with 7 tests in 0.03 seconds.
- Python compilation passed.
- Streamlit started successfully and served `HTTP 200` on `http://localhost:8503`.
- The temporary Streamlit verification server was stopped after startup was confirmed.

## Documentation Still To Complete

- Optionally add a screenshot of a generated plan to `README.md`.
- Use `ai_interactions.md` if stretch features involving AI workflows are attempted.
