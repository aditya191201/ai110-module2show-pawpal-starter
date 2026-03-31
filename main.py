"""
PawPal+ — manual test script
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Build owner and pets ---
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Add tasks to Mochi (dog) ---
    mochi.add_task(Task("Morning walk",      duration_minutes=30, priority="high",   category="exercise"))
    mochi.add_task(Task("Breakfast feeding", duration_minutes=10, priority="high",   category="feeding"))
    mochi.add_task(Task("Teeth brushing",    duration_minutes=5,  priority="medium", category="grooming"))

    # --- Add tasks to Luna (cat) ---
    luna.add_task(Task("Litter box cleaning", duration_minutes=10, priority="high",   category="hygiene"))
    luna.add_task(Task("Playtime",            duration_minutes=20, priority="medium", category="enrichment"))
    luna.add_task(Task("Flea treatment",      duration_minutes=15, priority="low",    category="medication"))

    # --- Generate and display schedule ---
    scheduler = Scheduler(owner)
    scheduler.generate_schedule()

    print("=" * 52)
    print("           🐾  PawPal+ — Today's Schedule")
    print("=" * 52)
    print(scheduler.explain_schedule())
    print("=" * 52)


if __name__ == "__main__":
    main()
