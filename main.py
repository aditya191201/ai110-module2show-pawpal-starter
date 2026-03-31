"""
PawPal+ — manual test script
Exercises sorting, filtering, recurring tasks, and conflict detection.
Run with: python3 main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 54}")
    print(f"  {title}")
    print("=" * 54)


def main():
    # ----------------------------------------------------------------
    # Setup
    # ----------------------------------------------------------------
    owner = Owner(name="Jordan", available_minutes=120)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks added OUT OF ORDER on purpose to test sort_by_time()
    mochi.add_task(Task("Evening walk",      30, "medium", "exercise",    start_time="18:00", frequency="daily"))
    mochi.add_task(Task("Breakfast feeding", 10, "high",   "feeding",     start_time="07:30", frequency="daily"))
    mochi.add_task(Task("Morning walk",      25, "high",   "exercise",    start_time="07:00", frequency="daily"))
    mochi.add_task(Task("Teeth brushing",     5, "medium", "grooming",    start_time=None,    frequency="once"))

    luna.add_task(Task("Litter box cleaning", 10, "high",   "hygiene",    start_time="08:00", frequency="daily"))
    luna.add_task(Task("Playtime",            20, "medium", "enrichment", start_time="18:00", frequency="weekly"))  # conflicts with Mochi's evening walk
    luna.add_task(Task("Flea treatment",      15, "low",    "medication", start_time=None,    frequency="once"))

    # ----------------------------------------------------------------
    # 1. Basic schedule
    # ----------------------------------------------------------------
    section("1. Today's Schedule (priority order)")
    scheduler = Scheduler(owner)
    scheduler.generate_schedule()
    print(scheduler.explain_schedule())

    # ----------------------------------------------------------------
    # 2. Sort by time
    # ----------------------------------------------------------------
    section("2. Schedule sorted by start_time (HH:MM)")
    for t in scheduler.sort_by_time():
        label = t.start_time or "(flexible)"
        print(f"  {label:<10}  {t.title:<25}  priority: {t.priority}")

    # ----------------------------------------------------------------
    # 3. Filter — pending tasks for Mochi only
    # ----------------------------------------------------------------
    section("3. Filtered — Mochi's pending tasks")
    for t in scheduler.filter_tasks(pet_name="Mochi", completed=False):
        print(f"  [{t.priority:>6}]  {t.title}")

    # ----------------------------------------------------------------
    # 4. Recurring task — mark Mochi's morning walk complete
    # ----------------------------------------------------------------
    section("4. Recurring task — mark 'Morning walk' complete")
    mochi_tasks_before = len(mochi.tasks)
    mochi.mark_task_complete("Morning walk")
    mochi_tasks_after = len(mochi.tasks)

    walk = next(t for t in mochi.tasks if t.title == "Morning walk" and t.completed)
    next_walk = next(t for t in mochi.tasks if t.title == "Morning walk" and not t.completed)
    print(f"  Completed:     '{walk.title}'  (due: {walk.due_date})")
    print(f"  Next instance: '{next_walk.title}'  (due: {next_walk.due_date})")
    print(f"  Task count before: {mochi_tasks_before}  →  after: {mochi_tasks_after}")

    # ----------------------------------------------------------------
    # 5. Conflict detection — Evening walk (Mochi) and Playtime (Luna) both at 18:00
    # ----------------------------------------------------------------
    section("5. Conflict detection")
    # Regenerate schedule to pick up any new tasks
    scheduler2 = Scheduler(owner)
    scheduler2.generate_schedule()
    conflicts = scheduler2.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠  {warning}")
    else:
        print("  No conflicts detected.")

    # ----------------------------------------------------------------
    # 6. Filter — show only completed tasks (across all pets)
    # ----------------------------------------------------------------
    section("6. Completed tasks across all pets")
    done = scheduler2.filter_tasks(completed=True)
    if done:
        for t in done:
            print(f"  ✓  {t.title}")
    else:
        print("  None yet.")


if __name__ == "__main__":
    main()
