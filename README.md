# 🐾 PawPal+

**PawPal+** is a Streamlit app that helps a busy pet owner stay consistent with daily pet care. It generates a prioritized daily schedule across multiple pets, detects scheduling conflicts, handles recurring tasks, and explains every decision it makes.

---

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

---

## Features

### Core Scheduling
- **Priority-based greedy scheduler** — tasks are ranked high → medium → low and selected in that order until the owner's time budget is exhausted. Critical care (medication, feeding) is always prioritized over enrichment.
- **Time budget enforcement** — the owner sets available minutes for the day; the scheduler never exceeds it.
- **Plain-English explanation** — after generating a schedule, the app explains which tasks were chosen, which were skipped, and why.

### Smarter Scheduling
- **Sort by time** — the generated schedule can be reordered chronologically by `start_time` (HH:MM). Tasks without a set time are placed at the end as "flexible."
- **Conflict detection** — if two tasks share the same `start_time` slot, the app surfaces a visible warning so the owner can resolve it before the day begins.
- **Recurring tasks** — tasks can be marked `daily` or `weekly`. When completed, the next occurrence is automatically added to the pet's task list with the correct due date (calculated via Python's `timedelta`).
- **Filtering** — tasks can be browsed by pet or by completion status (pending / completed / all).

### Multi-Pet Support
- The owner can register multiple pets. Each pet has its own task list. The scheduler aggregates and prioritizes tasks across all pets in a single daily plan.

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the manual demo

```bash
python3 main.py
```

---

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

Verbose output (shows each test name):

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
| Scheduler — sorting | `sort_by_time()` orders HH:MM chronologically; flexible tasks go last |
| Scheduler — filtering | By pet name, by completion status, by both combined; unknown name returns `[]` |
| Conflict detection | Flags duplicate start times within and across pets; ignores tasks with no start time; returns `[]` when no conflicts |
| Edge cases / safe no-ops | Empty pet, no pets, zero-budget → empty schedule; exact-budget-fit task is scheduled; remove/complete on missing title doesn't crash |
| Data integrity | `to_dict()` returns all eight expected fields |

**Confidence level: ★★★★☆ (4/5)**

All implemented behaviors are covered including boundary conditions. The known gap is duration-overlap conflict detection — tasks at adjacent but overlapping time slots are not yet flagged (see `reflection.md §2b`).

---

## Project Structure

```
pawpal_system.py     # Backend — Task, Pet, Owner, Scheduler classes
app.py               # Streamlit UI
main.py              # Terminal demo (manual testing ground)
tests/
  test_pawpal.py     # 31 automated tests
reflection.md        # Design decisions, tradeoffs, AI collaboration notes
```

---

## Suggested Workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
