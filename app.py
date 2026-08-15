import time

import streamlit as st

st.set_page_config(page_title="Timer App", page_icon="⏱️")

MODE_COUNTDOWN = "Countdown"
MODE_COUNT_UP = "Count up"
TIMER_THEMES = ["Classic", "Neon", "Sunset"]

THEME_COLORS = {
    "Classic": {"accent": "#4f46e5", "background": "#eef2ff", "surface": "#ffffff"},
    "Neon": {"accent": "#22d3ee", "background": "#0f172a", "surface": "#111827"},
    "Sunset": {"accent": "#f97316", "background": "#fff7ed", "surface": "#fff5f0"},
}

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_paused" not in st.session_state:
    st.session_state.timer_paused = False
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "mode" not in st.session_state:
    st.session_state.mode = MODE_COUNTDOWN
if "countdown_duration" not in st.session_state:
    st.session_state.countdown_duration = 0
if "count_up_started_at" not in st.session_state:
    st.session_state.count_up_started_at = None
if "paused_remaining" not in st.session_state:
    st.session_state.paused_remaining = 0
if "paused_elapsed" not in st.session_state:
    st.session_state.paused_elapsed = 0
if "theme" not in st.session_state:
    st.session_state.theme = TIMER_THEMES[0]


def get_total_seconds(minutes: int, seconds: int) -> int:
    return minutes * 60 + seconds


def format_seconds(total_seconds: int) -> str:
    total_seconds = max(0, total_seconds)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def reset_timer_state() -> None:
    st.session_state.timer_running = False
    st.session_state.timer_paused = False
    st.session_state.end_time = None
    st.session_state.count_up_started_at = None
    st.session_state.countdown_duration = 0
    st.session_state.paused_remaining = 0
    st.session_state.paused_elapsed = 0


def get_timer_message(remaining_seconds: int, total_seconds: int) -> str:
    if total_seconds <= 0:
        return "Ready, set, go\!"
    if remaining_seconds <= 0:
        return "Time to celebrate"
    progress = 1 - (remaining_seconds / total_seconds)
    if progress >= 0.75:
        return "Final sprint"
    if progress >= 0.5:
        return "Halfway"
    if progress >= 0.25:
        return "Steady pace"
    return "Nice start"


st.title("⏱️ Timer App for Streamlit")

selected_theme = st.selectbox(
    "Timer vibe",
    TIMER_THEMES,
    index=TIMER_THEMES.index(st.session_state.theme),
    key="theme",
)
st.session_state.theme = selected_theme
current_theme = THEME_COLORS.get(selected_theme, THEME_COLORS["Classic"])
st.markdown(
    f"""
    <style>
    div[data-testid="stMetricValue"] {{
        color: {current_theme['accent']};
        font-weight: 700;
    }}
    div[data-testid="stProgressBar"] > div > div {{
        background: linear-gradient(90deg, {current_theme['accent']}, #facc15);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

mode_options = [MODE_COUNTDOWN, MODE_COUNT_UP]
selected_mode = st.selectbox(
    "Timer mode",
    mode_options,
    index=mode_options.index(st.session_state.mode),
)

if selected_mode \!= st.session_state.mode:
    st.session_state.mode = selected_mode
    reset_timer_state()
    st.session_state.countdown_duration = 0

with st.form("timer_form"):
    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input("Minutes", min_value=0, max_value=120, value=1, step=1)
    with col2:
        seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)
    submitted = st.form_submit_button("Set timer")

if submitted:
    total_seconds = get_total_seconds(minutes, seconds)
    st.session_state.countdown_duration = total_seconds

    if st.session_state.mode == MODE_COUNTDOWN:
        if total_seconds > 0:
            st.session_state.end_time = time.time() + total_seconds
            st.session_state.timer_running = True
            st.session_state.timer_paused = False
            st.session_state.count_up_started_at = None
            st.session_state.paused_remaining = 0
            st.session_state.paused_elapsed = 0
        else:
            reset_timer_state()
    else:
        st.session_state.timer_running = True
        st.session_state.timer_paused = False
        st.session_state.end_time = None
        st.session_state.count_up_started_at = time.time()
        st.session_state.paused_remaining = 0
        st.session_state.paused_elapsed = 0

st.markdown("### Quick countdown presets")
preset_cols = st.columns(3)
for idx, minutes in enumerate((3, 5, 10)):
    with preset_cols[idx]:
        if st.button(f"🍅 {minutes} min", key=f"preset_{minutes}_minutes"):
            st.session_state.mode = MODE_COUNTDOWN
            st.session_state.countdown_duration = minutes * 60
            st.session_state.end_time = time.time() + (minutes * 60)
            st.session_state.timer_running = True
            st.session_state.timer_paused = False
            st.session_state.count_up_started_at = None
            st.session_state.paused_remaining = 0
            st.session_state.paused_elapsed = 0

pause_button = st.button("Pause Timer")
if pause_button and st.session_state.timer_running:
    if st.session_state.mode == MODE_COUNTDOWN and st.session_state.end_time is not None:
        st.session_state.paused_remaining = max(0, int(st.session_state.end_time - time.time()))
        st.session_state.end_time = None
        st.session_state.timer_running = False
        st.session_state.timer_paused = True
    elif st.session_state.mode == MODE_COUNT_UP and st.session_state.count_up_started_at is not None:
        st.session_state.paused_elapsed = max(0, int(time.time() - st.session_state.count_up_started_at))
        st.session_state.count_up_started_at = None
        st.session_state.timer_running = False
        st.session_state.timer_paused = True

resume_button = st.button("Resume Timer")
if resume_button and st.session_state.timer_paused:
    if st.session_state.mode == MODE_COUNTDOWN:
        st.session_state.end_time = time.time() + st.session_state.paused_remaining
        st.session_state.timer_running = True
        st.session_state.timer_paused = False
    elif st.session_state.mode == MODE_COUNT_UP:
        st.session_state.count_up_started_at = time.time() - st.session_state.paused_elapsed
        st.session_state.timer_running = True
        st.session_state.timer_paused = False

if st.button("Reset Timer"):
    reset_timer_state()
    st.session_state.countdown_duration = 0

if st.session_state.timer_running:
    if st.session_state.mode == MODE_COUNTDOWN and st.session_state.end_time is not None:
        remaining = max(0, int(st.session_state.end_time - time.time()))
        duration = max(1, st.session_state.countdown_duration)
        progress = 1 - (remaining / duration)
        st.metric("Remaining time", format_seconds(remaining))
        st.progress(max(0.0, min(progress, 1.0)))
        st.info(get_timer_message(remaining, duration))

        if remaining == 0:
            st.session_state.timer_running = False
            st.session_state.timer_paused = False
            st.session_state.end_time = None
            st.balloons()
            st.success("Time is up\! 🎉")
        else:
            time.sleep(0.2)
            st.rerun()
    elif st.session_state.mode == MODE_COUNT_UP and st.session_state.count_up_started_at is not None:
        elapsed = max(0, int(time.time() - st.session_state.count_up_started_at))
        st.metric("Elapsed time", format_seconds(elapsed))
        st.progress(min(elapsed / 60, 1.0))
        st.info(get_timer_message(max(0, min(60, 60 - elapsed)), 60))
        time.sleep(0.2)
        st.rerun()
else:
    if st.session_state.mode == MODE_COUNT_UP:
        elapsed = st.session_state.paused_elapsed if st.session_state.timer_paused else 0
        st.metric("Elapsed time", format_seconds(elapsed))
        st.progress(0.0)
    else:
        remaining = st.session_state.paused_remaining if st.session_state.timer_paused else st.session_state.countdown_duration
        if st.session_state.countdown_duration <= 0:
            default_seconds = get_total_seconds(minutes, seconds) if "minutes" in locals() and "seconds" in locals() else 60
            remaining = default_seconds
        st.metric("Remaining time", format_seconds(remaining))
        st.progress(0.0)
        if st.session_state.timer_paused:
            st.warning("Timer paused. Hit resume when you're ready.")

st.caption("Use the timer to count down from a chosen duration, switch to stopwatch mode, and enjoy a little extra personality while you focus.")
