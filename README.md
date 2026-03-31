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

## Smarter Scheduling

Beyond the basic priority-and-time-budget scheduler, PawPal+ includes four algorithmic improvements:

- **Sort by time** — `Scheduler.sort_by_time()` orders the scheduled task list by `start_time` (HH:MM strings), with flexible tasks (no start time) pushed to the end. Uses a `lambda` key: tasks without a time are mapped to `"99:99"` so Python's `sorted()` places them last.

- **Filtering** — `Scheduler.filter_tasks(pet_name, completed)` lets you query tasks by pet and/or completion status across all pets, making it easy to display "Mochi's pending tasks" or "everything completed today."

- **Recurring tasks** — `Task.mark_complete()` checks the task's `frequency` ("once", "daily", "weekly") and returns a new `Task` with the next due date calculated via Python's `timedelta`. `Pet.mark_task_complete(title)` calls this and automatically appends the next instance to the pet's task list, so recurring care never falls off the schedule.

- **Conflict detection** — `Scheduler.detect_conflicts()` groups scheduled tasks by `start_time` and returns a warning string for any slot occupied by more than one task. Detection uses exact HH:MM matching; see `reflection.md §2b` for the tradeoff this implies.

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

Or for verbose output showing each test name:

```bash
python -m pytest tests/ -v
```

**What the tests cover** (`tests/test_pawpal.py` — 31 tests):

| Category | Tests |
|---|---|
| Task completion | `mark_complete()` flips status; idempotent on double-call |
| Recurring logic | Daily/weekly tasks return a correctly-dated next instance; one-time tasks return `None`; next instance inherits all properties |
| Pet task management | Add, remove, priority sort; `mark_task_complete()` auto-appends next occurrence |
| Scheduler — happy paths | Respects time budget; prefers high priority; excludes already-completed tasks |
| Scheduler — sorting | `sort_by_time()` orders HH:MM chronologically; flexible tasks (no time) go last |
| Scheduler — filtering | By pet name, by completion status, by both combined; unknown name returns `[]` |
| Conflict detection | Flags duplicate start times within and across pets; ignores tasks with no start time; returns `[]` when no conflicts |
| Edge cases / safe no-ops | Empty pet, no pets, zero-budget → empty schedule; exact-budget-fit task is scheduled; remove/complete on missing title doesn't crash |
| Data integrity | `to_dict()` returns all eight expected fields |

**Confidence level: ★★★★☆ (4/5)**

The greedy priority scheduler, sorting, filtering, recurring logic, and conflict detection are all well-covered. The remaining uncertainty is the exact-match conflict detection tradeoff (see `reflection.md §2b`) — overlapping-duration conflicts between tasks with different start times are not yet caught.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
