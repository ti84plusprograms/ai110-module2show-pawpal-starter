# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Jordan

08:00  Mochi: Medication (daily, pending)
08:15  Mochi: Feeding (daily, pending)
08:30  Barkley: Morning walk (daily, pending)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
collected 7 items

tests/test_scheduler.py .......                                          [100%]

============================== 7 passed in 0.03s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by time, then pet name, then task description for stable ordering. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name, completion status, or due date. |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warning messages when two or more tasks share the same exact time on the same day. |
| Recurring tasks | `Task.mark_complete()` / `Task.create_next_occurrence()` / `Scheduler.mark_task_complete()` | Marks daily or weekly tasks complete and creates the next occurrence using `timedelta(days=1)` or `timedelta(days=7)`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Launch the app with `python -m streamlit run app.py` and open the local URL.
2. Enter the owner name, pet name, and species, then set a start time and the total minutes available for the day.
3. Add a few care tasks — each with a title, duration in minutes, and a priority of low/medium/high. Added tasks appear in the "Current tasks" table.
4. Click **Generate schedule**. The app converts your entries into scheduler objects and builds a daily plan.
5. Review the results: scheduled tasks show start/end times and a short reason for inclusion, while any task that did not fit the time budget is listed under "Skipped tasks" with an explanation.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
