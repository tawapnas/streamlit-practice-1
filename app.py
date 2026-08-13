import time

import streamlit as st

st.set_page_config(page_title="Timer App", page_icon="⏱️")

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "end_time" not in st.session_state:
    st.session_state.end_time = None


def format_seconds(total_seconds: int) -> str:
    minutes, seconds = divmod(max(0, total_seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


st.title("⏱️ Timer App")

with st.form("timer_form"):
    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input("Minutes", min_value=0, max_value=120, value=1, step=1)
    with col2:
        seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)
    submitted = st.form_submit_button("Set timer")

if submitted:
    total_seconds = minutes * 60 + seconds
    if total_seconds > 0:
        st.session_state.end_time = time.time() + total_seconds
        st.session_state.timer_running = True
    else:
        st.session_state.timer_running = False
        st.session_state.end_time = None

if st.button("Reset"):
    st.session_state.timer_running = False
    st.session_state.end_time = None

if st.session_state.timer_running and st.session_state.end_time is not None:
    remaining = max(0, int(st.session_state.end_time - time.time()))
    st.metric("Remaining time", format_seconds(remaining))

    progress = 1 - (remaining / max(1, int(st.session_state.end_time - time.time() + remaining)))
    st.progress(progress if progress > 0 else 0)

    if remaining == 0:
        st.session_state.timer_running = False
        st.session_state.end_time = None
        st.balloons()
        st.success("Time is up!")
    else:
        time.sleep(0.2)
        st.rerun()
else:
    default_seconds = (minutes * 60 + seconds) if "minutes" in locals() and "seconds" in locals() else 60
    st.metric("Remaining time", format_seconds(default_seconds))
    st.progress(0.0)

st.caption("Use the timer to count down from a chosen duration.")