import time

import streamlit as st

st.set_page_config(page_title="Timer App", page_icon="⏱️")

MODE_COUNTDOWN = "Countdown"
MODE_COUNT_UP = "Count up"

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "mode" not in st.session_state:
    st.session_state.mode = MODE_COUNTDOWN
if "countdown_duration" not in st.session_state:
    st.session_state.countdown_duration = 0
if "count_up_started_at" not in st.session_state:
    st.session_state.count_up_started_at = None


def get_total_seconds(minutes: int, seconds: int) -> int:
    return minutes * 60 + seconds


def format_seconds(total_seconds: int) -> str:
    total_seconds = max(0, total_seconds)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


st.title("⏱️ Timer App for Streamlit")

mode_options = [MODE_COUNTDOWN, MODE_COUNT_UP]
selected_mode = st.selectbox(
    "Timer mode",
    mode_options,
    index=mode_options.index(st.session_state.mode),
)

if selected_mode != st.session_state.mode:
    st.session_state.mode = selected_mode
    st.session_state.timer_running = False
    st.session_state.end_time = None
    st.session_state.count_up_started_at = None
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
            st.session_state.count_up_started_at = None
        else:
            st.session_state.timer_running = False
            st.session_state.end_time = None
    else:
        st.session_state.timer_running = True
        st.session_state.end_time = None
        st.session_state.count_up_started_at = time.time()

if st.button("Reset Timer"):
    st.session_state.timer_running = False
    st.session_state.end_time = None
    st.session_state.count_up_started_at = None
    st.session_state.countdown_duration = 0

if st.session_state.timer_running:
    if st.session_state.mode == MODE_COUNTDOWN and st.session_state.end_time is not None:
        remaining = max(0, int(st.session_state.end_time - time.time()))
        st.metric("Remaining time", format_seconds(remaining))

        duration = max(1, st.session_state.countdown_duration)
        progress = 1 - (remaining / duration)
        st.progress(max(0.0, min(progress, 1.0)))

        if remaining == 0:
            st.session_state.timer_running = False
            st.session_state.end_time = None
            st.balloons()
            st.success("Time is up!")
        else:
            time.sleep(0.2)
            st.rerun()
    elif st.session_state.mode == MODE_COUNT_UP and st.session_state.count_up_started_at is not None:
        elapsed = max(0, int(time.time() - st.session_state.count_up_started_at))
        st.metric("Elapsed time", format_seconds(elapsed))
        st.progress(min(elapsed / 60, 1.0))
        time.sleep(0.2)
        st.rerun()
else:
    if st.session_state.mode == MODE_COUNT_UP:
        st.metric("Elapsed time", format_seconds(0))
        st.progress(0.0)
    else:
        default_seconds = get_total_seconds(minutes, seconds) if "minutes" in locals() and "seconds" in locals() else 60
        st.metric("Remaining time", format_seconds(default_seconds))
        st.progress(0.0)

st.caption("Use the timer to count down from a chosen duration or switch to stopwatch mode to count up.")