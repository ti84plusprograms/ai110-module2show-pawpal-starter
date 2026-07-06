# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML captured the four core building blocks the assignment asked for, plus the output objects needed to explain the plan:

- `OwnerProfile` — the owner's name, preferred start time, and how many minutes are available.
- `PetProfile` — basic pet identity (name, species, optional preferences).
- `CareTask` — a task to schedule: title, duration, priority, optional notes.
- `PawPalScheduler` — the planner that turns input tasks into a daily schedule.
- `ScheduledTask` — a task that made it into the plan, with concrete start/end times and a reason.
- `DailyPlan` — the result object holding scheduled and skipped tasks plus derived totals.

The split keeps the *input* data (`CareTask`) separate from the *output* data (`ScheduledTask`), so the scheduler is a pure transformation.

**b. Design changes**

Yes. Originally the plan totals (`total_scheduled_minutes`, `remaining_minutes`) were going to be plain fields the scheduler filled in. During implementation they became computed `@property` values on `DailyPlan` instead, so they can never drift out of sync with the actual task list. The UML was updated to show them as methods.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: **priority** (high → medium → low) and the **available time budget**. Priority matters most, because the point of the app is making sure the important care happens first when a day is busy. Time is the hard limit that decides how much of the priority-ordered list actually fits.

**b. Tradeoffs**

Within the same priority level, shorter tasks are scheduled first. This is a greedy "fit more in" rule — it maximizes the *number* of tasks completed rather than guaranteeing that a particular long task runs. That is reasonable here because most pet-care items are short and interchangeable in timing; getting more of them done is more useful than protecting one long task. The downside is that a long, equally-important task can get bumped to the end and skipped.

Another tradeoff is that conflict detection only checks for exact date-and-time matches between pending tasks (across any scheduled date, ignoring completed tasks). That keeps the scheduler lightweight and easy to explain, but it does not catch tasks that overlap in duration if they start at different times.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used to scaffold the dataclasses from the UML, to suggest the sort key, and to draft the test cases for the ordering and skip behaviors. The most helpful prompts were concrete ones that stated the exact contract — e.g. "sort by priority, then duration, then keep original order for ties" — rather than open-ended "write a scheduler" prompts.

**b. Judgment and verification**

A first-cut sort key sorted only by priority and duration, which made the ordering of same-priority, same-duration tasks non-deterministic. I added the original index as a final tiebreaker so the output is stable and testable. Every suggestion was verified by running `pytest` and by booting the Streamlit app to confirm the plan rendered correctly end to end.

---

## 4. Testing and Verification

**a. What you tested**

Seven tests cover: priority ordering, skipping tasks that do not fit, the shorter-task tiebreaker, start/end time and total/remaining-minute consistency, that each scheduled task carries an explanation, the empty-task-list case, and input validation (rejecting zero durations and unknown priorities). These are the behaviors a user would actually notice if they broke.

**b. Confidence**

Fairly confident for the core greedy path. Given more time I would test tasks whose durations exactly consume the remaining budget, overlapping fixed-time tasks, and non-`time` start-time inputs coming from the UI.

---

## 5. Reflection

**a. What went well**

Separating `CareTask` (input) from `ScheduledTask` (output) kept the scheduler easy to test. It is a pure function of its inputs with no hidden state.

**b. What you would improve**

Add recurring tasks and real time-of-day conflict handling, and let the owner mark certain tasks as fixed-time so they anchor the schedule instead of flowing back-to-back.

**c. Key takeaway**

Encoding the exact ordering contract — including tiebreakers — up front made both the AI collaboration and the tests dramatically clearer. Vague requirements produce vague, flaky code.
