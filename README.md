# 🐾 PawPal+ — Pet Care Scheduler

A Python-based pet care scheduling system with a Streamlit UI. **PawPal+** helps pet owners organize and manage care tasks for multiple pets with automatic sorting, conflict detection, and recurring task generation.

## Overview

**PawPal+** is a three-layer architecture application:

- **Domain Layer** (`pawpal_system.py`): `Owner`, `Pet`, `Task` classes with recurrence logic
- **Service Layer** (`pawpal_system.py`): `Scheduler` with 6 key methods (sort, filter, mark complete, detect conflicts)
- **Output Layer** (`pawpal_system.py`): `ScheduledItem` for display
- **UI Layer** (`app.py`): Streamlit interface with session state persistence

---

## ✨ Features

### Core Algorithms

| Feature | Implementation | Algorithm |
|---------|-----------------|-----------|
| **Task Sorting** | `Scheduler.sort_by_time()` | Orders tasks by time (ascending), then pet name, then description for stable deterministic ordering |
| **Task Filtering** | `Scheduler.filter_tasks()` | Filters by pet name, completion status, or due date (filters AND together) |
| **Recurring Tasks** | `Task.mark_complete()` + `Task.create_next_occurrence()` | Generates next task for "daily" (next day) or "weekly" (7 days later); idempotent completion |
| **Conflict Detection** | `Scheduler.detect_conflicts()` | Identifies pending tasks with same date AND time (ignores completed tasks); warns per (date, time) group |
| **Schedule Building** | `Scheduler.build_schedule()` | Filters today's tasks → sorts → converts to ScheduledItem list |
| **Completion Workflow** | `Scheduler.mark_task_complete()` | Marks task done, generates next occurrence (if recurring), appends to pet's task list |

### UI Features

| Feature | Location | Description |
|---------|----------|-------------|
| **Owner & Pet Management** | Sidebar | Add/edit owner name and register pets with species |
| **Task Assignment** | Form | Add tasks with time, frequency, and description to specific pets |
| **Live Filtering** | Schedule Section | Filter by pet and status (pending/completed); updates in real-time |
| **Today's Schedule** | Main Display | Sorted, filtered schedule with time, pet, task, and completion status |
| **Conflict Warnings** | Alerts Section | Highlights same-time collisions between pending tasks |
| **Task Completion** | Interactive Controls | Mark tasks complete; system generates next occurrence for recurring tasks |

---

## 🚀 Getting Started

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd ai110-module2show-pawpal-starter

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the App

**Streamlit UI:**
```bash
streamlit run app.py
```
Opens in browser at `http://localhost:8501`

**CLI Demo:**
```bash
python main.py
```
Demonstrates sorting, filtering, recurrence, and conflict detection

### Run Tests

```bash
python -m pytest tests/ -v
```
Runs 42 comprehensive tests covering all Scheduler behaviors

---

## 📊 Demo Walkthrough

### Example Workflow: Add a Pet and Schedule Tasks

#### Step 1: Enter Owner Information
- Launch the Streamlit app: `streamlit run app.py`
- Owner name defaults to "Jordan" (customizable)

#### Step 2: Register Pets
1. In the **"Add a Pet"** form, enter:
   - Pet name: "Mochi"
   - Species: "cat"
   - Click **Add Pet**
2. Repeat for second pet:
   - Pet name: "Barkley"
   - Species: "dog"
   - Click **Add Pet**
3. Current pets table shows both registered pets with task counts

#### Step 3: Assign Care Tasks
1. In the **"Add a Task"** form, select pet "Mochi" and add:
   - Task description: "Medication"
   - Task time: "08:00"
   - Frequency: "daily"
   - Click **Add Task**
2. Add another task for Mochi:
   - Task description: "Feeding"
   - Task time: "08:15"
   - Frequency: "daily"
   - Click **Add Task**
3. Add tasks for Barkley:
   - "Brush teeth" at "08:05" (daily)
   - "Morning walk" at "08:15" (daily)

Current tasks table now shows 4 tasks across 2 pets.

#### Step 4: View Today's Schedule (Sorted)
The **"Today's Schedule"** section displays automatically:
- Tasks filtered for today (due_date = today)
- Sorted by time, then pet name, then description
- Status shown as ✓ Done or ⏳ Pending

**Output:**
```
08:00  Mochi: Medication (daily, ⏳ Pending)
08:05  Barkley: Brush teeth (daily, ⏳ Pending)
08:15  Barkley: Morning walk (daily, ⏳ Pending)  ← Tie-break: Barkley before Mochi (alphabetical)
08:15  Mochi: Feeding (daily, ⏳ Pending)
```

#### Step 5: Check for Conflicts
The **"Conflict Detection"** section warns if multiple tasks share the same time:
```
⚠️ Scheduling conflicts detected!
Warning: 2 tasks are scheduled at 08:15 on 2026-07-06: Barkley: Morning walk, Mochi: Feeding
```

#### Step 6: Mark a Task Complete
In **"Mark Task Complete"** section:
1. Select pet: "Mochi"
2. Select task: "Medication"
3. Click **Mark Complete**

**Result:**
- ✓ Completed 'Medication'. Next occurrence scheduled for 2026-07-07
- New task "Medication" automatically added to Mochi's tasks for tomorrow
- Live schedule updates immediately

#### Step 7: Filter & View Subsets
Use the filter dropdowns to explore:
- **Filter by pet:** "Mochi" → shows only Mochi's tasks
- **Filter by status:** "Pending" → hides completed tasks
- **Combination:** Pet "Barkley" + Status "Completed" → shows completed tasks for Barkley only

---

## 🖥️ CLI Demo Output

Run `python main.py` to see all Scheduler capabilities in action:

```
Today's Schedule for Jordan

08:00  Mochi: Medication (daily, pending)
08:05  Barkley: Brush teeth (daily, pending)
08:15  Barkley: Morning walk (daily, pending)
08:15  Mochi: Feeding (daily, pending)

Mochi tasks only
08:00  Mochi: Medication
08:15  Mochi: Feeding

Completed tasks only

Recurring tasks after completion
2026-07-06  08:00  Mochi: Medication (daily, done)
2026-07-07  08:00  Mochi: Medication (daily, pending)
2026-07-06  08:15  Mochi: Feeding (daily, pending)

Conflict warnings
Warning: 2 tasks are scheduled at 08:15 on 2026-07-06: Mochi: Feeding, Barkley: Morning walk
```

**Key Behaviors Demonstrated:**

1. **Sorting** — Tasks ordered by time (08:00 → 08:05 → 08:15), then by pet name alphabetically (Barkley before Mochi at 08:15)
2. **Filtering** — "Mochi tasks only" section shows only Mochi's tasks; "Completed tasks only" section is empty (no tasks marked complete in demo)
3. **Recurrence** — Completing "Medication" (daily) generates a new task for 2026-07-07 with completion_status=False
4. **Conflict Detection** — Two tasks at 08:15 (Morning walk + Feeding) trigger a warning with task details

---

## 🧪 Testing

### Test Coverage

The test suite (`tests/test_pawpal.py`) includes 35 comprehensive tests:

- **Sorting Correctness** (2 tests) — Tasks returned in chronological order with deterministic tie-breaking
- **Filtering** (4 tests) — pet_name, completion_status, due_date filters individually and combined
- **Recurrence Logic** (5 tests) — daily/weekly generate next; once/unknown don't; month boundary edge cases
- **Completion Workflow** (3 tests) — Idempotent marking; next occurrence added to pet's list; no-match returns None
- **Conflict Detection** (5 tests) — Same-time collisions flagged; future dates detected; completed tasks ignored; 3-way pileups listed
- **Edge Cases** (8 tests) — Empty owner, malformed input, invalid time strings, default due_date=today

**Run Tests:**

```bash
python -m pytest tests/test_pawpal.py -v
```

**Output:**

```
tests/test_pawpal.py::test_sort_by_time_returns_tasks_in_chronological_order PASSED       [  2%]
tests/test_pawpal.py::test_sort_by_time_breaks_ties_by_pet_name_then_description PASSED   [  5%]
tests/test_pawpal.py::test_marking_daily_task_complete_creates_task_for_following_day PASSED [  8%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_times PASSED                   [ 11%]
...
============================== 35 passed in 0.06s ===============================
```

**Confidence Level:** ★★★★★ (All high-value edge cases covered; 100% test pass rate)

---

## 📐 Architecture Overview

### Three-Layer Design

```
┌─────────────────────────────────────────────────┐
│  Streamlit UI (app.py)                          │
│  • Owner/Pet/Task forms                         │
│  • Live filtering & sorting                     │
│  • Conflict warnings                            │
│  • Task completion workflow                     │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  Service Layer (Scheduler)                      │
│  • sort_by_time()                               │
│  • filter_tasks()                               │
│  • mark_task_complete()                         │
│  • detect_conflicts()                           │
│  • build_schedule()                             │
│  • get_todays_schedule()                        │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  Domain Layer (Owner → Pet → Task)              │
│  • Composition chain with lifetime dependency   │
│  • Task recurrence logic (mark_complete)        │
│  • Immutable ScheduledItem view                 │
└─────────────────────────────────────────────────┘
```

### Key Classes

| Class | Role | Key Methods |
|-------|------|-------------|
| `Owner` | Root aggregate | `add_pet()`, `get_all_tasks()` |
| `Pet` | Secondary aggregate | `add_task()`, `get_tasks()` |
| `Task` | Domain entity | `mark_complete()`, `create_next_occurrence()` |
| `ScheduledItem` | Display view | (data class, no methods) |
| `Scheduler` | Service/orchestrator | All 6 key methods |

---

## 📁 Project Structure

```
pawpal_system.py           # Domain + Service layers (Owner, Pet, Task, Scheduler, ScheduledItem)
main.py                    # CLI demo (exercises all Scheduler methods)
app.py                     # Streamlit UI with session state persistence
tests/
├── test_pawpal.py         # 35 comprehensive tests (sorting, filtering, recurrence, conflicts)
└── test_scheduler.py      # 7 additional tests for Scheduler class
diagrams/uml.mmd           # Mermaid UML diagram (class definitions, relationships, annotations)
requirements.txt           # Dependencies (streamlit, pytest, etc.)
README.md                  # This file
```

---

## 🎯 Design Decisions

### Recurrence is Self-Contained
- `Task.mark_complete()` generates the next Task (daily/weekly)
- `Scheduler.mark_task_complete()` orchestrates the workflow
- Result: Easy to test, extend, and understand

### Conflicts Based on Time Only
- Checks `(date, time)` pairs, not duration overlaps
- Keeps logic lightweight and warnings easy to understand
- Completed tasks excluded (don't compete for attention)

### Immutable Display Layer
- `ScheduledItem` is immutable snapshot for display
- `Task` is mutable domain object
- Separation of concerns: domain logic vs. presentation

### Stateless Scheduler
- All methods take `Owner` as parameter
- No internal state; highly testable
- Composes domain methods into workflows

---

## 🔧 Extending PawPal+

To add new features, follow established patterns:

- **New frequency** (e.g., "monthly"): Add case to `Task._recurrence_delta()`
- **New filter** (e.g., by species): Extend `Scheduler.filter_tasks()` signature
- **New sort key** (e.g., by priority): Extend `sort_by_time()` key function
- **Persistence**: Add database layer that loads/saves Owner objects
- **Notifications**: Hook into `mark_task_complete()` to send reminders

---

## 📝 License

This project is part of the AI110 Module 2 assignment.
5. Review the results: scheduled tasks show start/end times and a short reason for inclusion, while any task that did not fit the time budget is listed under "Skipped tasks" with an explanation.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
