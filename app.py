from datetime import time

try:
    import streamlit as st
except ImportError:
    class _FallbackSessionState(dict):
        def __getattr__(self, key: str):
            try:
                return self[key]
            except KeyError as exc:
                raise AttributeError(key) from exc

        def __setattr__(self, key: str, value):
            self[key] = value


    class _FallbackContext:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False


    class _FallbackStreamlit:
        def __init__(self):
            self.session_state = _FallbackSessionState()

        def set_page_config(self, *args, **kwargs):
            return None

        def title(self, *args, **kwargs):
            return None

        def markdown(self, *args, **kwargs):
            return None

        def divider(self):
            return None

        def subheader(self, *args, **kwargs):
            return None

        def text_input(self, _label, value=""):
            return value

        def selectbox(self, _label, options, index=0):
            return options[index]

        def time_input(self, _label, value):
            return value

        def number_input(self, _label, *, min_value=None, max_value=None, value=0, step=1):
            return value

        def caption(self, *args, **kwargs):
            return None

        def columns(self, count):
            return tuple(_FallbackContext() for _ in range(count))

        def form(self, *args, **kwargs):
            return _FallbackContext()

        def form_submit_button(self, *args, **kwargs):
            return False

        def button(self, *args, **kwargs):
            return False

        def write(self, *args, **kwargs):
            return None

        def table(self, *args, **kwargs):
            return None

        def info(self, *args, **kwargs):
            return None

        def success(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def expander(self, *args, **kwargs):
            return _FallbackContext()


    st = _FallbackStreamlit()

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

st.session_state.owner.name = owner_name

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    existing_pet_names = {pet.name for pet in st.session_state.owner.pets}
    if pet_name and pet_name not in existing_pet_names:
        st.session_state.owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} to {st.session_state.owner.name}'s pets.")
    elif pet_name in existing_pet_names:
        st.warning(f"{pet_name} is already on the list.")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table([
        {"Name": pet.name, "Species": pet.species, "Tasks": len(pet.tasks)}
        for pet in st.session_state.owner.pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if st.session_state.owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Assign to pet", [pet.name for pet in st.session_state.owner.pets])
        task_description = st.text_input("Task description", value="Morning walk")
        task_time = st.time_input("Task time", value=time(8, 0))
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        add_task = st.form_submit_button("Add Task")

    if add_task:
        selected_pet = next((pet for pet in st.session_state.owner.pets if pet.name == selected_pet_name), None)
        if selected_pet is not None:
            selected_pet.add_task(Task(description=task_description, time=task_time, frequency=frequency))
            st.success(f"Added '{task_description}' to {selected_pet_name}.")
else:
    st.caption("Add a pet first, then you can assign tasks to it.")

if st.session_state.owner.pets:
    st.write("Current tasks:")
    task_rows = []
    for pet in st.session_state.owner.pets:
        for task in pet.tasks:
            task_rows.append(
                {
                    "Pet": pet.name,
                    "Task": task.description,
                    "Time": task.time.strftime("%H:%M"),
                    "Frequency": task.frequency,
                    "Done": task.completion_status,
                }
            )

    if task_rows:
        st.table(task_rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")
st.caption("Tasks are automatically sorted by time. Use filters and conflict detection below.")

scheduler = Scheduler()

if st.session_state.owner.pets:
    col1, col2 = st.columns(2)

    with col1:
        filter_pet = st.selectbox(
            "Filter by pet",
            ["All"] + [pet.name for pet in st.session_state.owner.pets],
            key="pet_filter"
        )

    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed"],
            key="status_filter"
        )

    pet_name_filter = None if filter_pet == "All" else filter_pet
    completion_filter = None
    if filter_status == "Pending":
        completion_filter = False
    elif filter_status == "Completed":
        completion_filter = True

    filtered_tasks = scheduler.filter_tasks(
        st.session_state.owner,
        pet_name=pet_name_filter,
        completion_status=completion_filter
    )

    sorted_tasks = scheduler.sort_by_time(filtered_tasks)

    if sorted_tasks:
        st.success(f"Showing {len(sorted_tasks)} task(s) for {st.session_state.owner.name}")
        st.table(
            [
                {
                    "Time": task.time.strftime("%H:%M"),
                    "Pet": pet.name,
                    "Task": task.description,
                    "Frequency": task.frequency,
                    "Status": "✓ Done" if task.completion_status else "⏳ Pending",
                }
                for pet, task in sorted_tasks
            ]
        )
    else:
        st.info("No tasks match the current filters.")

st.divider()

st.subheader("Conflict Detection")
st.caption("Identifies when multiple pending tasks are scheduled for the same time.")

if st.session_state.owner.pets:
    warnings = scheduler.detect_conflicts(st.session_state.owner)

    if warnings:
        st.warning("⚠️ Scheduling conflicts detected!")
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("✅ No scheduling conflicts.")
else:
    st.info("Add a pet and tasks to check for conflicts.")

st.divider()

st.subheader("Mark Task Complete")
st.caption("Complete a task and generate its next recurring occurrence if applicable.")

if st.session_state.owner.pets:
    col1, col2, col3 = st.columns(3)

    with col1:
        pet_to_complete = st.selectbox(
            "Select pet",
            [pet.name for pet in st.session_state.owner.pets],
            key="complete_pet_select"
        )

    selected_pet = next((pet for pet in st.session_state.owner.pets if pet.name == pet_to_complete), None)
    pending_tasks = [task for task in selected_pet.tasks if not task.completion_status] if selected_pet else []

    with col2:
        task_to_complete = st.selectbox(
            "Select pending task",
            [task.description for task in pending_tasks] if pending_tasks else ["No pending tasks"],
            key="complete_task_select"
        )

    with col3:
        if st.button("Mark Complete", key="mark_complete_btn"):
            if pending_tasks and task_to_complete != "No pending tasks":
                next_task = scheduler.mark_task_complete(st.session_state.owner, pet_to_complete, task_to_complete)
                if next_task:
                    st.success(f"✓ Completed '{task_to_complete}'. Next occurrence scheduled for {next_task.due_date.isoformat()}.")
                else:
                    st.success(f"✓ Completed '{task_to_complete}'.")
                st.rerun()
            else:
                st.warning("Select a pending task to mark complete.")
else:
    st.caption("Add a pet and tasks first.")
