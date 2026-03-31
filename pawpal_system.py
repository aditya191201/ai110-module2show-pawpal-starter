"""
PawPal+ — logic layer
All backend classes for the pet care scheduling system.
"""

from datetime import date, timedelta
from collections import defaultdict

_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


class Task:
    """A single pet care task (walk, feeding, medication, etc.)."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
        category: str = "general",
        start_time: str | None = None,
        frequency: str = "once",
        due_date: date | None = None,
    ):
        """Initialise a task with its title, duration, priority, and optional scheduling fields.

        Args:
            title: Short name for the task.
            duration_minutes: How long the task takes.
            priority: "high", "medium", or "low".
            category: Broad type (exercise, feeding, grooming, …).
            start_time: Scheduled start in "HH:MM" format, or None.
            frequency: How often the task recurs — "once", "daily", or "weekly".
            due_date: The date this instance is due (defaults to today).
        """
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.start_time = start_time        # "HH:MM" or None
        self.frequency = frequency          # "once", "daily", "weekly"
        self.due_date = due_date or date.today()
        self.completed = False

    def mark_complete(self) -> "Task | None":
        """Mark this task complete and return the next occurrence if it recurs.

        Returns:
            A new Task due on the next occurrence date, or None if frequency is "once".
        """
        self.completed = True
        if self.frequency == "daily":
            return Task(
                self.title, self.duration_minutes, self.priority,
                self.category, self.start_time, self.frequency,
                self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                self.title, self.duration_minutes, self.priority,
                self.category, self.start_time, self.frequency,
                self.due_date + timedelta(weeks=1),
            )
        return None

    def to_dict(self) -> dict:
        """Return a dictionary representation of the task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "start_time": self.start_time,
            "frequency": self.frequency,
            "due_date": str(self.due_date),
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

    def mark_task_complete(self, title: str) -> None:
        """Mark a task complete; if it recurs, append the next occurrence to the task list."""
        for task in self.tasks:
            if task.title == title and not task.completed:
                next_task = task.mark_complete()
                if next_task:
                    self.tasks.append(next_task)
                break


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
        """Return all tasks across every pet, sorted by priority."""
        all_tasks = [task for pet in self.pets for task in pet.tasks]
        return sorted(all_tasks, key=lambda t: _PRIORITY_RANK.get(t.priority, 99))


class Scheduler:
    """Generates, sorts, filters, and validates a daily care schedule across all pets."""

    def __init__(self, owner: Owner):
        """Initialise the scheduler with an Owner instance."""
        self.owner = owner
        self.schedule: list[Task] = []

    # ------------------------------------------------------------------
    # Core scheduling
    # ------------------------------------------------------------------

    def generate_schedule(self) -> list[Task]:
        """Build a priority-ordered task list that fits within the owner's time budget."""
        self.schedule = self._fit_within_budget(self.owner.get_all_tasks())
        return self.schedule

    def explain_schedule(self) -> str:
        """Return a plain-English explanation of scheduled tasks and any omissions."""
        if not self.schedule:
            return "No tasks scheduled. Run generate_schedule() first or add tasks."

        lines = [f"Daily plan for {self.owner.name} ({self.get_total_duration()} min total):\n"]
        elapsed = 0
        for task in self.schedule:
            time_label = f"@{task.start_time}" if task.start_time else f"+{elapsed}min"
            lines.append(
                f"  {time_label:<10}  {task.title}"
                f"  ({task.duration_minutes} min, priority: {task.priority})"
            )
            elapsed += task.duration_minutes

        skipped = [t for t in self.owner.get_all_tasks() if t not in self.schedule]
        if skipped:
            lines.append("\nSkipped (not enough time):")
            for t in skipped:
                lines.append(f"  - {t.title} ({t.duration_minutes} min, priority: {t.priority})")

        return "\n".join(lines)

    def get_total_duration(self) -> int:
        """Return the sum of durations (in minutes) for all scheduled tasks."""
        return sum(t.duration_minutes for t in self.schedule)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self) -> list[Task]:
        """Return scheduled tasks sorted by start_time (HH:MM); tasks without a time go last.

        Uses a lambda key so that None start_times sort after all valid HH:MM strings
        ("99:99" is safely beyond any real time value).
        """
        return sorted(self.schedule, key=lambda t: t.start_time or "99:99")

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Args:
            pet_name: If given, only include tasks belonging to this pet.
            completed: If True, return only completed tasks; if False, only pending ones.
                       If None, return tasks regardless of completion status.
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any tasks that share the same start_time slot.

        Only tasks with an explicit start_time are checked; tasks without one are
        ignored (they are treated as flexible). Detection uses exact HH:MM matching —
        see reflection.md §2b for the tradeoff this implies.
        """
        time_groups: dict[str, list[Task]] = defaultdict(list)
        for task in self.schedule:
            if task.start_time:
                time_groups[task.start_time].append(task)

        warnings = []
        for slot, tasks in time_groups.items():
            if len(tasks) > 1:
                names = ", ".join(f'"{t.title}"' for t in tasks)
                warnings.append(f"Conflict at {slot}: {names} are all scheduled at the same time.")
        return warnings

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fit_within_budget(self, sorted_tasks: list[Task]) -> list[Task]:
        """Greedily select incomplete tasks in priority order until the time budget is exhausted."""
        chosen, remaining = [], self.owner.available_minutes
        for task in sorted_tasks:
            if task.completed:
                continue
            if task.duration_minutes <= remaining:
                chosen.append(task)
                remaining -= task.duration_minutes
        return chosen
