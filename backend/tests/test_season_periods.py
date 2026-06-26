from app.services.season_periods import payment_for_label, payment_for_options


def test_payment_for_options_include_tournament() -> None:
    options = payment_for_options("2025/2026")

    assert options[-1].value == "tournament"
    assert options[-1].label == "Турнир"
    assert len(options) == 12


def test_payment_for_label() -> None:
    assert payment_for_label("2025-09") == "Сентябрь 2025"
    assert payment_for_label("tournament") == "Турнир"
