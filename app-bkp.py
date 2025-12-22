import streamlit as st
from datetime import date

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="Workout App",
    page_icon="💪",
    layout="centered"
)

# -------------------------
# Session State Init
# -------------------------
if "workout_history" not in st.session_state:
    st.session_state.workout_history = []

# -------------------------
# Workout Data
# -------------------------
workout_data = {
    "Chest & Triceps": {
        "Warm up": ["Cycle"],
        "Circuit set": [
            "High Knees", "Prone Walkout", "Deltoid Circles", "Kettlebell Halo"
        ],
        "Workout": [
            "Pushups", "Incline Dumbbell Chest Press", "Dumbbell Chest Press",
            "Dumbbell Chest Flyes", "Bench Dips",
            "Dumbbell Tricep Extension", "Low Plank", "Crunches"
        ],
        "Stretch": [
            "Sphinx Stretch", "Child's Pose",
            "Shoulder Extension Pec Stretch",
            "Shoulder Archer Stretch Left",
            "Shoulder Archer Stretch Right"
        ]
    },
    "Back & Biceps": {
        "Warm up": ["Treadmill"],
        "Circuit set": [
            "World's Greatest Stretch Left",
            "World's Greatest Stretch Right",
            "Bent Over Y Raise",
            "Alternate Toe Touches",
            "Prone Swimmers"
        ],
        "Workout": [
            "Lat Pull Down", "Machine Seated Row",
            "Dumbbell Bent-over Row",
            "Dumbbell Seated Bicep Curl",
            "Close Grip Bicep Curl",
            "Side Plank Left", "Side Plank Right",
            "Bicycle Crunches"
        ],
        "Stretch": [
            "Sphinx Stretch", "Thread the Needle Left",
            "Thread the Needle Right", "Child's Pose"
        ]
    },
    "Legs": {
        "Warm up": ["Cycle"],
        "Circuit set": [
            "Dynamic Pigeon Stretch Left",
            "Dynamic Pigeon Stretch Right",
            "Half Wipers - Scale Down",
            "Table Top Up and Down",
            "Side to Side Shuffle"
        ],
        "Workout": [
            "Body Weight Squat", "Leg Press",
            "Machine Hamstring Curls",
            "Seated Machine Calf Raise",
            "Bird Dog", "Alternate Leg Raise"
        ],
        "Stretch": [
            "Hamstring Stretch", "Child's Pose",
            "Prone Quad Stretch Left",
            "Prone Quad Stretch Right",
            "Butterfly Stretch"
        ]
    },
    "Shoulders": {
        "Warm up": ["Cross Trainer"],
        "Circuit set": [
            "World's Greatest Stretch Left",
            "World's Greatest Stretch Right",
            "Cat Camel", "Deltoid Circles", "Footfires"
        ],
        "Workout": [
            "Machine Shoulder Press",
            "1-arm Dumbbell Lateral Raise Left",
            "1-arm Dumbbell Lateral Raise Right",
            "Dumbbell Alternating Front Raise",
            "Machine Reverse Flyes",
            "Prone YTW",
            "Shoulder Taps",
            "Hollow Hold",
            "Side Plank Left",
            "Side Plank Right"
        ],
        "Stretch": [
            "Sphinx Stretch",
            "Lateral Neck Stretch Left",
            "Lateral Neck Stretch Right",
            "Pec Stretch",
            "Downward Dog"
        ]
    }
}

# -------------------------
# Helper: get last workout
# -------------------------
def get_last_workout(workout_type):
    history = [
        h for h in st.session_state.workout_history
        if h["workout_type"] == workout_type
    ]
    return history[-1] if history else None

# -------------------------
# UI
# -------------------------
st.title("🏋️ Workout Tracker")

selected_date = st.date_input("Workout Date", date.today())
workout_type = st.selectbox("Workout Type", workout_data.keys())

last_workout = get_last_workout(workout_type)
current_workout = {}

st.markdown("---")

# -------------------------
# Workout Input
# -------------------------
for section, exercises in workout_data[workout_type].items():
    with st.expander(section, expanded=True):
        for exercise in exercises:
            prev = (
                last_workout["data"].get(exercise, {})
                if last_workout else {}
            )

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(exercise)

            sets = col2.number_input(
                "Sets",
                min_value=0,
                value=prev.get("sets", 0),
                key=f"{selected_date}_{workout_type}_{exercise}_sets"
            )
            reps = col3.number_input(
                "Reps",
                min_value=0,
                value=prev.get("reps", 0),
                key=f"{selected_date}_{workout_type}_{exercise}_reps"
            )
            weight = col4.number_input(
                "Weight",
                min_value=0.0,
                step=0.5,
                value=prev.get("weight", 0.0),
                key=f"{selected_date}_{workout_type}_{exercise}_weight"
            )

            current_workout[exercise] = {
                "sets": sets,
                "reps": reps,
                "weight": weight
            }

# -------------------------
# Save Workout
# -------------------------
if st.button("💾 Save Workout"):
    st.session_state.workout_history.append({
        "date": selected_date,
        "workout_type": workout_type,
        "data": current_workout
    })
    st.success("Workout saved")

# -------------------------
# Workout History Table
# -------------------------
st.markdown("---")
st.subheader("📊 Workout History")

if st.session_state.workout_history:
    history_rows = [
        {
            "Date": h["date"],
            "Workout Type": h["workout_type"],
            "Exercises Logged": len(h["data"])
        }
        for h in st.session_state.workout_history
    ]

    history_rows.sort(key=lambda x: x["Date"])
    st.dataframe(history_rows, use_container_width=True)
else:
    st.info("No workout history yet")
