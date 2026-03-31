"""
PawPal+ — logic layer
All backend classes for the pet care scheduling system.
"""


class Task:
    """A single pet care task (walk, feeding, medication, etc.)."""

    def __init__(self, title: str, duration_minutes: int, priority: str, category: str = "general"):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low", "medium", or "high"
        self.category = category
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def to_dict(self) -> dict:
        """Return a dictionary representation of the task."""
        pass


class Pet:
    """A pet with a list of care tasks."""

    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by title from this pet's task list."""
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted from highest to lowest priority."""
        pass


class Owner:
    """A pet owner with a time budget for the day."""

    def __init__(self, name: str, available_minutes: int, pet: Pet):
        self.name = name
        self.available_minutes = available_minutes
        self.pet = pet

    def set_availability(self, minutes: int) -> None:
        """Update how many minutes the owner has available today."""
        pass

    def get_pet(self) -> Pet:
        """Return the owner's pet."""
        pass


class Scheduler:
    """Generates and explains a daily care schedule for a pet."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule: list[Task] = []

    def generate_schedule(self) -> list[Task]:
        """Build an ordered task list that fits within the owner's available time."""
        pass

    def explain_schedule(self) -> str:
        """Return a human-readable explanation of why tasks were chosen and ordered."""
        pass

    def get_total_duration(self) -> int:
        """Return the total duration (in minutes) of all scheduled tasks."""
        pass
