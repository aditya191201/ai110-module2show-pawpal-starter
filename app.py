import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your smart pet care planner — priority scheduling, conflict detection, and recurring tasks.")

# ---------------------------------------------------------------------------
# Session state bootstrap — persists Owner across Streamlit reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1 — Owner Profile
# ---------------------------------------------------------------------------
st.header("1. Owner Profile")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Owner name", value=owner.name)
    with col2:
        available = st.number_input(
            "Available minutes today", min_value=0, max_value=480, value=owner.available_minutes
        )
    if st.form_submit_button("Save profile"):
        owner.name = owner_name
        owner.set_availability(int(available))
        st.success(f"Saved — {owner.name}, {owner.available_minutes} min available today.")

# ---------------------------------------------------------------------------
# Section 2 — Pets
# ---------------------------------------------------------------------------
st.header("2. Your Pets")

with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    if st.form_submit_button("Add pet"):
        if pet_name in [p.name for p in owner.pets]:
            st.warning(f"'{pet_name}' is already registered.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
            st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    for pet in owner.pets:
        pending = sum(1 for t in pet.tasks if not t.completed)
        st.markdown(f"- **{pet.name}** ({pet.species}, age {pet.age}) — {pending} pending task(s)")
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3 — Tasks
# ---------------------------------------------------------------------------
st.header("3. Pet Care Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    # --- Add task form ---
    with st.form("task_form"):
        st.subheader("Add a task")
        pet_names = [p.name for p in owner.pets]
        col1, col2 = st.columns(2)
        with col1:
            selected_pet_name = st.selectbox("Assign to pet", pet_names)
            task_title = st.text_input("Task title", value="Morning walk")
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            category = st.selectbox(
                "Category",
                ["exercise", "feeding", "grooming", "medication", "enrichment", "hygiene", "general"],
            )
            start_time = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 08:00")
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(
                Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                    start_time=start_time.strip() or None,
                    frequency=frequency,
                )
            )
            st.success(f"Added '{task_title}' ({frequency}) to {selected_pet_name}.")

    # --- Filter and view tasks ---
    st.subheader("View tasks")
    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox("Filter by pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    # Build filtered list using Scheduler.filter_tasks
    _sched_for_filter = Scheduler(owner)
    filter_pet_arg = None if filter_pet == "All pets" else filter_pet
    filter_done_arg = None if filter_status == "All" else (filter_status == "Completed")
    filtered = _sched_for_filter.filter_tasks(pet_name=filter_pet_arg, completed=filter_done_arg)

    if filtered:
        st.dataframe(
            [t.to_dict() for t in filtered],
            use_container_width=True,
        )
    else:
        st.info("No tasks match the current filter.")

    # --- Mark task complete ---
    all_pending = [t for t in owner.get_all_tasks() if not t.completed]
    if all_pending:
        st.subheader("Mark a task complete")
        task_to_complete = st.selectbox(
            "Select task",
            [t.title for t in all_pending],
            key="complete_selector",
        )
        if st.button("Mark complete"):
            for pet in owner.pets:
                titles = [t.title for t in pet.tasks if not t.completed]
                if task_to_complete in titles:
                    pet.mark_task_complete(task_to_complete)
                    # Check if a recurring next instance was appended
                    next_instances = [t for t in pet.tasks if t.title == task_to_complete and not t.completed]
                    if next_instances:
                        st.success(
                            f"'{task_to_complete}' marked complete. "
                            f"Next occurrence added for {next_instances[0].due_date}."
                        )
                    else:
                        st.success(f"'{task_to_complete}' marked complete.")
                    break

# ---------------------------------------------------------------------------
# Section 4 — Today's Schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("4. Today's Schedule")

if st.button("Generate schedule", type="primary"):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler(owner)
        scheduler.generate_schedule()

        # --- Conflict warnings — shown first so the owner sees them immediately ---
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.error(f"⚠️ {len(conflicts)} scheduling conflict(s) detected — please review before the day starts:")
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success(
                f"Schedule ready — {len(scheduler.schedule)} task(s), "
                f"{scheduler.get_total_duration()} min total. No conflicts."
            )

        # --- Sorted schedule table ---
        sorted_tasks = scheduler.sort_by_time()
        if sorted_tasks:
            st.subheader("Schedule (sorted by start time)")
            rows = []
            for t in sorted_tasks:
                rows.append({
                    "Start time": t.start_time or "(flexible)",
                    "Task": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Category": t.category,
                    "Frequency": t.frequency,
                })
            st.dataframe(rows, use_container_width=True)

        # --- Plain-English explanation ---
        with st.expander("See full explanation"):
            st.code(scheduler.explain_schedule(), language=None)

        # --- Skipped tasks ---
        skipped = [t for t in owner.get_all_tasks() if t not in scheduler.schedule and not t.completed]
        if skipped:
            with st.expander(f"Skipped tasks ({len(skipped)} — not enough time)"):
                for t in skipped:
                    st.markdown(
                        f"- **{t.title}** — {t.duration_minutes} min, priority: {t.priority}"
                    )
