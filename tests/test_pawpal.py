"""
Tests for PawPal+ core logic.
Run with: python -m pytest
"""

from pawpal_system import Task, Pet, Owner, Scheduler


# --- Task tests ---

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


# --- Pet tests ---

def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", duration_minutes=20, priority="high"))
    assert len(pet.tasks) == 1


def test_add_multiple_tasks_increases_count():
    """Adding three tasks should result in a task list of length three."""
    pet = Pet(name="Luna", species="cat", age=5)
    pet.add_task(Task("Play",    duration_minutes=15, priority="medium"))
    pet.add_task(Task("Feed",    duration_minutes=10, priority="high"))
    pet.add_task(Task("Groom",   duration_minutes=5,  priority="low"))
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


# --- Scheduler tests ---

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
