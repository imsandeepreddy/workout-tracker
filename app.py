import streamlit as st

# =========================
# 🔐 PIN Authentication
# =========================
APP_PIN = st.secrets["APP_PIN"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Enter PIN")

    pin_input = st.text_input(
        "4-digit PIN",
        type="password",
        max_chars=4
    )

    if st.button("Unlock", use_container_width=True):
        if pin_input == APP_PIN:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect PIN")

    st.stop()

# =========================
# Imports (after auth)
# =========================
import psycopg2
import pandas as pd
from datetime import date, timedelta

# =========================
# Page Config (Mobile-first)
# =========================
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Supabase Connection
# =========================
def get_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        dbname=st.secrets["database"]["dbname"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        sslmode="require",
        connect_timeout=10
    )

conn = get_connection()
cursor = conn.cursor()

# =========================
# Workout Definitions
# =========================
workout_data = {
    "Chest & Triceps": {
        "Warm up": ["Cycle"],
        "Circuit set": ["High Knees", "Prone Walkout", "Deltoid Circles", "Kettlebell Halo"],
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

# =========================
# Helper Functions
# =========================
def get_last_exercise(exercise):
    cursor.execute("""
        SELECT sets, reps, weight
        FROM workouts
        WHERE exercise = %s
        ORDER BY workout_date DESC, created_at DESC
        LIMIT 1
    """, (exercise,))
    row = cursor.fetchone()
    return row if row else (0, 0, 0.0)

def save_workout(workout_date, workout_type, data):
    cursor.execute("""
        DELETE FROM workouts
        WHERE workout_date = %s AND workout_type = %s
    """, (workout_date, workout_type))

    for section, exercises in data.items():
        for ex, vals in exercises.items():
            cursor.execute("""
                INSERT INTO workouts
                (workout_date, workout_type, section, exercise, sets, reps, weight)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                workout_date,
                workout_type,
                section,
                ex,
                vals["sets"],
                vals["reps"],
                vals["weight"]
            ))
    conn.commit()

def get_exercise_video(exercise_name):
    slug = exercise_name.lower().replace(" ", "_")
    return f"https://raw.githubusercontent.com/<username>/<repo>/main/exercises/{slug}.mp4"

# =========================
# 🏋️ UI
# =========================
st.title("🏋️ Workout Tracker")

st.markdown("### 🗓️ Workout Setup")

selected_date = st.date_input("Date", date.today())
workout_type = st.selectbox("Workout Type", workout_data.keys())

workout_input = {}

# =========================
# Workout Entry (Mobile)
# =========================
for section, exercises in workout_data[workout_type].items():
    expanded = section == "Workout"

    with st.expander(section, expanded=expanded):
        workout_input[section] = {}

        for exercise in exercises:
            last_sets, last_reps, last_weight = get_last_exercise(exercise)

            st.markdown(f"**{exercise}**")

            gif_url = get_exercise_gif(exercise)

            if gif_url:
                show_demo = st.toggle(
                    "Show demo",
                    key=f"demo_{selected_date}_{exercise}"
                )

                if show_demo:
                    st.video(gif_url)

            sets = st.number_input(
                "Sets",
                min_value=0,
                value=last_sets,
                key=f"{selected_date}_{exercise}_sets"
            )

            reps = st.number_input(
                "Reps",
                min_value=0,
                value=last_reps,
                key=f"{selected_date}_{exercise}_reps"
            )

            weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                step=0.5,
                value=last_weight,
                key=f"{selected_date}_{exercise}_weight"
            )

            workout_input[section][exercise] = {
                "sets": sets,
                "reps": reps,
                "weight": weight
            }

            st.divider()

# =========================
# Save Workout
# =========================
if st.button("💾 Save Workout", use_container_width=True):
    save_workout(selected_date, workout_type, workout_input)
    st.success("Workout saved")

# =========================
# 📊 Weekly Daily Summary (Mobile cards)
# =========================
st.markdown("---")
st.subheader("📊 Weekly Summary")

week_date = st.date_input("Select week", selected_date)
start_week = week_date - timedelta(days=week_date.weekday())
end_week = start_week + timedelta(days=6)

cursor.execute("""
    SELECT workout_date,
           workout_type,
           COUNT(DISTINCT exercise),
           SUM(sets),
           SUM(reps),
           SUM(sets * reps * weight)
    FROM workouts
    WHERE workout_date BETWEEN %s AND %s
    GROUP BY workout_date, workout_type
    ORDER BY workout_date, workout_type
""", (start_week, end_week))

rows = cursor.fetchall()

if rows:
    df = pd.DataFrame(rows, columns=[
        "Date", "Workout Type", "Exercises", "Sets", "Reps", "Volume"
    ])

    for _, r in df.iterrows():
        st.markdown(
            f"""
            **📅 {r['Date']} — {r['Workout Type']}**  
            • Exercises: {r['Exercises']}  
            • Sets: {r['Sets']}  
            • Reps: {r['Reps']}  
            • Volume: {round(r['Volume'], 1)}
            """
        )
        st.divider()
else:
    st.info("No workouts logged for this week")
