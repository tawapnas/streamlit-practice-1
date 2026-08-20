import time
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

st.set_page_config(page_title="Timer App", page_icon="⏱️")

MODE_COUNTDOWN = "Countdown"
MODE_COUNT_UP = "Count up"
MODE_POMODORO = "Pomodoro"
POMODORO_WORK = "Work"
POMODORO_BREAK = "Break"
DEFAULT_POMODORO_WORK_MINUTES = 25
DEFAULT_POMODORO_BREAK_MINUTES = 5
TIMER_THEMES = [
    "Classic",
    "Neon",
    "Sunset",
    "Forest",
    "Ocean",
    "Lavender",
    "Rose",
    "Midnight",
]
TIMEZONE_OPTIONS = [
    "UTC",
    "Asia/Bangkok",
    "Asia/Singapore",
    "Asia/Tokyo",
    "Europe/London",
    "America/New_York",
    "America/Los_Angeles",
    "Australia/Sydney",
]

THEME_COLORS = {
    "Classic": {"accent": "#4f46e5", "background": "#eef2ff", "surface": "#ffffff"},
    "Neon": {"accent": "#22d3ee", "background": "#0f172a", "surface": "#111827"},
    "Sunset": {"accent": "#f97316", "background": "#fff7ed", "surface": "#fff5f0"},
    "Forest": {"accent": "#10b981", "background": "#ecfdf5", "surface": "#f0fdf4"},
    "Ocean": {"accent": "#0ea5e9", "background": "#eff6ff", "surface": "#f8fbff"},
    "Lavender": {"accent": "#8b5cf6", "background": "#f5f3ff", "surface": "#faf5ff"},
    "Rose": {"accent": "#ec4899", "background": "#fff1f2", "surface": "#fff7f8"},
    "Midnight": {"accent": "#a78bfa", "background": "#111827", "surface": "#1f2937"},
}
THEME_MODES = ["Light", "Dark"]
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 1.6
DEFAULT_FONT_SCALE = 1.0

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
if "pomodoro_phase" not in st.session_state:
    st.session_state.pomodoro_phase = POMODORO_WORK
if "pomodoro_round" not in st.session_state:
    st.session_state.pomodoro_round = 1
if "pomodoro_completed" not in st.session_state:
    st.session_state.pomodoro_completed = 0
if "pomodoro_work_duration" not in st.session_state:
    st.session_state.pomodoro_work_duration = DEFAULT_POMODORO_WORK_MINUTES * 60
if "pomodoro_break_duration" not in st.session_state:
    st.session_state.pomodoro_break_duration = DEFAULT_POMODORO_BREAK_MINUTES * 60
if "theme" not in st.session_state:
    st.session_state.theme = TIMER_THEMES[0]
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = THEME_MODES[0]
if "font_scale" not in st.session_state:
    st.session_state.font_scale = DEFAULT_FONT_SCALE
if "timezone" not in st.session_state:
    st.session_state.timezone = "UTC"
if "scratchpad_note" not in st.session_state:
    st.session_state.scratchpad_note = ""


def get_total_seconds(minutes: int, seconds: int) -> int:
    return minutes * 60 + seconds


def clamp_font_scale(value: float) -> float:
    numeric_value = float(value)
    return min(MAX_FONT_SCALE, max(MIN_FONT_SCALE, numeric_value))


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
    st.session_state.pomodoro_phase = POMODORO_WORK
    st.session_state.pomodoro_round = 1
    st.session_state.pomodoro_completed = 0


def get_timer_message(remaining_seconds: int, total_seconds: int) -> str:
    if total_seconds <= 0:
        return "Ready, set, go!"
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


def advance_pomodoro_phase() -> None:
    if st.session_state.pomodoro_phase == POMODORO_WORK:
        st.session_state.pomodoro_phase = POMODORO_BREAK
        st.session_state.countdown_duration = st.session_state.pomodoro_break_duration
    else:
        st.session_state.pomodoro_phase = POMODORO_WORK
        st.session_state.pomodoro_round += 1
        st.session_state.countdown_duration = st.session_state.pomodoro_work_duration
    st.session_state.end_time = time.time() + st.session_state.countdown_duration
    st.session_state.timer_running = True
    st.session_state.timer_paused = False
    st.session_state.paused_remaining = 0


def get_current_time_in_timezone(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


st.title("⏱️ Timer App for Streamlit")

app_theme = st.radio(
    "App appearance",
    THEME_MODES,
    index=THEME_MODES.index(st.session_state.theme_mode),
    horizontal=True,
    key="theme_mode",
)
st.session_state.theme_mode = app_theme

font_controls = st.columns([1, 1, 2])
with font_controls[0]:
    if st.button("A−", key="decrease_font", use_container_width=True):
        st.session_state.font_scale = clamp_font_scale(st.session_state.font_scale - 0.1)
with font_controls[1]:
    if st.button("A+", key="increase_font", use_container_width=True):
        st.session_state.font_scale = clamp_font_scale(st.session_state.font_scale + 0.1)
with font_controls[2]:
    st.caption(f"Font size: {st.session_state.font_scale:.1f}x")

st.session_state.font_scale = clamp_font_scale(st.session_state.font_scale)

selected_theme = st.selectbox(
    "Timer vibe",
    TIMER_THEMES,
    index=TIMER_THEMES.index(st.session_state.theme),
    key="theme",
)
st.session_state.theme = selected_theme
current_theme = THEME_COLORS.get(selected_theme, THEME_COLORS["Classic"])

selected_timezone = st.selectbox(
    "Display timezone",
    TIMEZONE_OPTIONS,
    index=TIMEZONE_OPTIONS.index(st.session_state.timezone),
    key="timezone",
)
st.session_state.timezone = selected_timezone

now_in_timezone = get_current_time_in_timezone(st.session_state.timezone)
st.caption(
    f"Current time in {st.session_state.timezone}: "
    f"{now_in_timezone.strftime('%Y-%m-%d %H:%M:%S %Z')}"
)

app_background = "#0f172a" if app_theme == "Dark" else "#f8fafc"
app_surface = "#111827" if app_theme == "Dark" else "#ffffff"
app_text = "#e2e8f0" if app_theme == "Dark" else "#0f172a"
app_muted = "#cbd5e1" if app_theme == "Dark" else "#475569"

st.markdown(
    f"""
    <style>
    :root {{
        --app-font-scale: {st.session_state.font_scale};
    }}
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
        background: {app_background};
        color: {app_text};
    }}
    .stApp, .stMarkdown, .stCaption, .stSelectbox, .stNumberInput, .stButton > button {{
        font-size: calc(1rem * var(--app-font-scale));
    }}
    .stApp div[data-testid="stVerticalBlock"] {{
        color: {app_text};
    }}
    div[data-testid="stMetricValue"] {{
        color: {current_theme['accent']};
        font-weight: 700;
    }}
    div[data-testid="stProgressBar"] > div > div {{
        background: linear-gradient(90deg, {current_theme['accent']}, #facc15);
    }}
    .stAlert, .stInfo, .stWarning, .stSuccess {{
        border-radius: 0.75rem;
    }}
    .stButton > button {{
        border-radius: 999px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

mode_options = [MODE_COUNTDOWN, MODE_COUNT_UP, MODE_POMODORO]
selected_mode = st.selectbox(
    "Timer mode",
    mode_options,
    index=mode_options.index(st.session_state.mode),
)

if selected_mode != st.session_state.mode:
    st.session_state.mode = selected_mode
    reset_timer_state()
    st.session_state.countdown_duration = 0

with st.form("timer_form"):
    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input(
            "Work minutes" if st.session_state.mode == MODE_POMODORO else "Minutes",
            min_value=0,
            max_value=120,
            value=DEFAULT_POMODORO_WORK_MINUTES if st.session_state.mode == MODE_POMODORO else 1,
            step=1,
        )
    with col2:
        seconds = st.number_input(
            "Break minutes" if st.session_state.mode == MODE_POMODORO else "Seconds",
            min_value=0,
            max_value=59 if st.session_state.mode != MODE_POMODORO else 60,
            value=0 if st.session_state.mode != MODE_POMODORO else DEFAULT_POMODORO_BREAK_MINUTES,
            step=1,
        )
    submitted = st.form_submit_button("Set timer")

if submitted:
    if st.session_state.mode == MODE_POMODORO:
        st.session_state.pomodoro_phase = POMODORO_WORK
        st.session_state.pomodoro_round = 1
        st.session_state.pomodoro_completed = 0
        total_seconds = get_total_seconds(minutes, 0)
        st.session_state.pomodoro_work_duration = total_seconds
        st.session_state.pomodoro_break_duration = get_total_seconds(seconds, 0)
    else:
        total_seconds = get_total_seconds(minutes, seconds)
    st.session_state.countdown_duration = total_seconds

    if st.session_state.mode in (MODE_COUNTDOWN, MODE_POMODORO):
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
    if st.session_state.mode in (MODE_COUNTDOWN, MODE_POMODORO) and st.session_state.end_time is not None:
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
    if st.session_state.mode in (MODE_COUNTDOWN, MODE_POMODORO):
        st.session_state.end_time = time.time() + st.session_state.paused_remaining
        st.session_state.timer_running = True
        st.session_state.timer_paused = False
    elif st.session_state.mode == MODE_COUNT_UP:
        st.session_state.count_up_started_at = time.time() - st.session_state.paused_elapsed
        st.session_state.timer_running = True
        st.session_state.timer_paused = False

if st.session_state.mode == MODE_POMODORO:
    skip_button = st.button("Skip phase")
    if skip_button and st.session_state.timer_running:
        advance_pomodoro_phase()

if st.button("Reset Timer"):
    reset_timer_state()
    st.session_state.countdown_duration = 0

if st.session_state.timer_running:
    if st.session_state.mode in (MODE_COUNTDOWN, MODE_POMODORO) and st.session_state.end_time is not None:
        remaining = max(0, int(st.session_state.end_time - time.time()))
        duration = max(1, st.session_state.countdown_duration)
        progress = 1 - (remaining / duration)
        metric_label = (
            f"{st.session_state.pomodoro_phase} time"
            if st.session_state.mode == MODE_POMODORO
            else "Remaining time"
        )
        st.metric(metric_label, format_seconds(remaining))
        st.progress(max(0.0, min(progress, 1.0)))
        st.info(get_timer_message(remaining, duration))

        if remaining == 0:
            if st.session_state.mode == MODE_POMODORO:
                if st.session_state.pomodoro_phase == POMODORO_WORK:
                    st.session_state.pomodoro_completed += 1
                advance_pomodoro_phase()
                st.success(f"{st.session_state.pomodoro_phase} phase started")
            else:
                st.session_state.timer_running = False
                st.session_state.timer_paused = False
                st.session_state.end_time = None
                st.balloons()
                st.success("Time is up! 🎉")
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
            remaining = 60
        metric_label = (
            f"{st.session_state.pomodoro_phase} time"
            if st.session_state.mode == MODE_POMODORO
            else "Remaining time"
        )
        st.metric(metric_label, format_seconds(remaining))
        st.progress(0.0)
        if st.session_state.mode == MODE_POMODORO:
            stats_col1, stats_col2 = st.columns(2)
            with stats_col1:
                st.caption(f"Round {st.session_state.pomodoro_round}")
            with stats_col2:
                st.caption(f"Focus sessions: {st.session_state.pomodoro_completed}")
        if st.session_state.timer_paused:
            st.warning("Timer paused. Hit resume when you're ready.")

st.subheader("📝 Scratchpad")
notes_col, clear_col = st.columns([5, 1])
with notes_col:
    st.text_area(
        "Quick note",
        key="scratchpad_note",
        height=150,
        placeholder="Jot a short note here...",
    )
with clear_col:
    if st.button("Clear", use_container_width=True):
        st.session_state.scratchpad_note = ""

st.caption("Use the timer to count down from a chosen duration, switch to stopwatch mode, and enjoy a little extra personality while you focus.")
