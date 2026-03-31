import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# Streamlit reruns this entire file on every interaction. We keep the Owner
# object in st.session_state so data persists across reruns without being
# reset. The first time the app loads, "owner" won't exist in the vault yet,
# so we create a default one and store it there.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.header("1. Owner Profile")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Owner name", value=owner.name)
    with col2:
        available = st.number_input(
            "Available minutes today", min_value=10, max_value=480, value=owner.available_minutes
        )
    if st.form_submit_button("Save owner"):
        owner.name = owner_name
        owner.set_availability(available)
        st.success(f"Profile saved — {owner.name}, {owner.available_minutes} min available.")

# ---------------------------------------------------------------------------
# Section 2 — Add a pet
# ---------------------------------------------------------------------------
st.header("2. Your Pets")

with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    if st.form_submit_button("Add pet"):
        # Prevent duplicates by name
        existing_names = [p.name for p in owner.pets]
        if pet_name in existing_names:
            st.warning(f"{pet_name} is already in your pet list.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, age=age))
            st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Registered pets:**")
    for pet in owner.pets:
        st.markdown(f"- **{pet.name}** ({pet.species}, age {pet.age}) — {len(pet.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3 — Add a task to a pet
# ---------------------------------------------------------------------------
st.header("3. Pet Care Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col4:
            category = st.selectbox("Category", ["exercise", "feeding", "grooming", "medication", "enrichment", "hygiene", "general"])

        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(
                Task(title=task_title, duration_minutes=int(duration), priority=priority, category=category)
            )
            st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # Show all current tasks grouped by pet
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks (sorted by priority):**")
        st.table([t.to_dict() for t in all_tasks])
    else:
        st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("4. Today's Schedule")

if st.button("Generate schedule", type="primary"):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler(owner)
        scheduler.generate_schedule()
        st.success(f"Scheduled {len(scheduler.schedule)} task(s) — {scheduler.get_total_duration()} min total.")
        st.code(scheduler.explain_schedule(), language=None)
