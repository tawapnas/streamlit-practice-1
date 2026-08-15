import app


def test_get_total_seconds():
    assert app.get_total_seconds(1, 30) == 90


def test_timer_modes_are_defined():
    assert app.MODE_COUNTDOWN == "Countdown"
    assert app.MODE_COUNT_UP == "Count up"


def test_get_timer_message_uses_milestones():
    assert "Final sprint" in app.get_timer_message(30, 120)
    assert "Halfway" in app.get_timer_message(60, 120)
    assert "Time to celebrate" in app.get_timer_message(0, 120)


def test_get_timer_theme_has_style_names():
    assert "Classic" in app.TIMER_THEMES
    assert "Neon" in app.TIMER_THEMES
