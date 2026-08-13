import app


def test_get_total_seconds():
    assert app.get_total_seconds(1, 30) == 90


def test_timer_modes_are_defined():
    assert app.MODE_COUNTDOWN == "Countdown"
    assert app.MODE_COUNT_UP == "Count up"
