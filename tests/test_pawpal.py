"""
Tests for PawPal+ core logic.
Run with: python -m pytest
"""

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_is_idempotent():
    """Calling mark_complete() twice should leave completed as True."""
    task = Task("Feeding", duration_minutes=10, priority="medium")
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


def test_recurring_daily_task_returns_next_instance():
    """Completing a daily task should return a new Task due the following day."""
    today = date.today()
    task = Task("Walk", duration_minutes=20, priority="high", frequency="daily", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_recurring_weekly_task_returns_next_instance():
    """Completing a weekly task should return a new Task due seven days later."""
    today = date.today()
    task = Task("Bath", duration_minutes=30, priority="medium", frequency="weekly", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_one_time_task_returns_none_on_complete():
    """Completing a one-time task should return None (no next occurrence)."""
    task = Task("Vet visit", duration_minutes=60, priority="high", frequency="once")
    result = task.mark_complete()
    assert result is None


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", duration_minutes=20, priority="high"))
    assert len(pet.tasks) == 1


def test_add_multiple_tasks_increases_count():
    """Adding three tasks should result in a task list of length three."""
    pet = Pet(name="Luna", species="cat", age=5)
    pet.add_task(Task("Play",  duration_minutes=15, priority="medium"))
    pet.add_task(Task("Feed",  duration_minutes=10, priority="high"))
    pet.add_task(Task("Groom", duration_minutes=5,  priority="low"))
    assert len(pet.tasks) == 3


def test_remove_task_decreases_count():
    """Removing a task by title should reduce the task list length by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task("Feed", duration_minutes=10, priority="high"))
    pet.remove_task("Walk")
    assert len(pet.tasks) == 1


def test_get_tasks_by_priority_orders_correctly():
    """get_tasks_by_priority() should return tasks high → medium → low."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Nap",  duration_minutes=60, priority="low"))
    pet.add_task(Task("Meds", duration_minutes=5,  priority="high"))
    pet.add_task(Task("Play", duration_minutes=20, priority="medium"))
    ordered = pet.get_tasks_by_priority()
    assert [t.priority for t in ordered] == ["high", "medium", "low"]


def test_mark_task_complete_appends_next_recurring():
    """mark_task_complete() on a daily task should append the next occurrence."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", duration_minutes=20, priority="high", frequency="daily"))
    assert len(pet.tasks) == 1
    pet.mark_task_complete("Walk")
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_budget():
    """Scheduler should not schedule more total minutes than available."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Long walk", duration_minutes=25, priority="high"))
    pet.add_task(Task("Bath",      duration_minutes=20, priority="medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    assert scheduler.get_total_duration() <= 30


def test_scheduler_prefers_high_priority():
    """When time is tight, high-priority tasks should be chosen over low-priority ones."""
    owner = Owner(name="Jordan", available_minutes=20)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Medicine", duration_minutes=10, priority="high"))
    pet.add_task(Task("Nap time", duration_minutes=15, priority="low"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    titles = [t.title for t in scheduler.schedule]
    assert "Medicine" in titles
    assert "Nap time" not in titles


def test_scheduler_excludes_completed_tasks():
    """Completed tasks should not appear in a newly generated schedule."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", age=3)
    done = Task("Old walk", duration_minutes=20, priority="high")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Feed", duration_minutes=10, priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    titles = [t.title for t in scheduler.schedule]
    assert "Old walk" not in titles
    assert "Feed" in titles


def test_sort_by_time_orders_by_start_time():
    """sort_by_time() should order tasks by HH:MM, with None times last."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Evening walk", 30, "medium", start_time="18:00"))
    pet.add_task(Task("Morning feed", 10, "high",   start_time="07:30"))
    pet.add_task(Task("Flexible",     5,  "low",    start_time=None))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    sorted_tasks = scheduler.sort_by_time()
    times = [t.start_time or "99:99" for t in sorted_tasks]
    assert times == sorted(times)


def test_detect_conflicts_finds_same_time_tasks():
    """detect_conflicts() should flag two tasks sharing the same start_time."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk",  30, "high",   start_time="08:00"))
    pet.add_task(Task("Bath",  20, "medium", start_time="08:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) should return only that pet's tasks."""
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)
    mochi.add_task(Task("Walk", 20, "high"))
    luna.add_task(Task("Play", 15, "medium"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    results = scheduler.filter_tasks(pet_name="Mochi")
    assert all(t.title == "Walk" for t in results)
    assert len(results) == 1


def test_filter_tasks_by_completion():
    """filter_tasks(completed=False) should return only incomplete tasks."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", age=3)
    done = Task("Walk", 20, "high")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Feed", 10, "high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    pending = scheduler.filter_tasks(completed=False)
    assert len(pending) == 1
    assert pending[0].title == "Feed"
