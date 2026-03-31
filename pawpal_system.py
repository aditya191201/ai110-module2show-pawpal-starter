"""
PawPal+ — logic layer
All backend classes for the pet care scheduling system.
"""

_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


class Task:
    """A single pet care task (walk, feeding, medication, etc.)."""

    def __init__(self, title: str, duration_minutes: int, priority: str, category: str = "general"):
        """Initialise a task with its title, duration, priority, and optional category."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low", "medium", or "high"
        self.category = category
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def to_dict(self) -> dict:
        """Return a dictionary representation of the task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "completed": self.completed,
        }


class Pet:
    """A pet with a list of care tasks."""

    def __init__(self, name: str, species: str, age: int):
        """Initialise a pet with its name, species, and age."""
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first task whose title matches; does nothing if not found."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return a copy of tasks sorted from highest to lowest priority."""
        return sorted(self.tasks, key=lambda t: _PRIORITY_RANK.get(t.priority, 99))


class Owner:
    """A pet owner who may have multiple pets and a daily time budget."""

    def __init__(self, name: str, available_minutes: int):
        """Initialise the owner with their name and available time budget."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def set_availability(self, minutes: int) -> None:
        """Update the number of minutes the owner has available today."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across every pet owned, sorted by priority."""
        all_tasks = [task for pet in self.pets for task in pet.tasks]
        return sorted(all_tasks, key=lambda t: _PRIORITY_RANK.get(t.priority, 99))


class Scheduler:
    """Generates and explains a daily care schedule across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Initialise the scheduler with an Owner instance."""
        self.owner = owner
        self.schedule: list[Task] = []

    def generate_schedule(self) -> list[Task]:
        """Build an ordered task list that fits within the owner's available time budget."""
        self.schedule = self._fit_within_budget(self.owner.get_all_tasks())
        return self.schedule

    def explain_schedule(self) -> str:
        """Return a plain-English explanation of the scheduled tasks and any omissions."""
        if not self.schedule:
            return "No tasks scheduled. Run generate_schedule() first or add tasks."

        lines = [f"Daily plan for {self.owner.name} ({self.get_total_duration()} min total):\n"]
        elapsed = 0
        for task in self.schedule:
            start = elapsed
            end = elapsed + task.duration_minutes
            lines.append(
                f"  [{start:>3}–{end:>3} min]  {task.title}"
                f"  (priority: {task.priority}, category: {task.category})"
            )
            elapsed = end

        skipped = [
            t for t in self.owner.get_all_tasks() if t not in self.schedule
        ]
        if skipped:
            lines.append("\nSkipped (not enough time):")
            for t in skipped:
                lines.append(f"  - {t.title} ({t.duration_minutes} min, priority: {t.priority})")

        return "\n".join(lines)

    def get_total_duration(self) -> int:
        """Return the sum of durations (in minutes) for all scheduled tasks."""
        return sum(t.duration_minutes for t in self.schedule)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fit_within_budget(self, sorted_tasks: list[Task]) -> list[Task]:
        """Greedily select tasks in priority order until the time budget is exhausted."""
        chosen = []
        remaining = self.owner.available_minutes
        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                chosen.append(task)
                remaining -= task.duration_minutes
        return chosen
