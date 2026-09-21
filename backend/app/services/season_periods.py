from dataclasses import dataclass
from datetime import datetime

TOURNAMENT_KEY = "tournament"
TOURNAMENT_LABEL = "Турнир"

SEASON_PERIODS: dict[str, list[tuple[str, str]]] = {
    "2025/2026": [
        ("2025-08", "Август 2025"),
        ("2025-09", "Сентябрь 2025"),
        ("2025-10", "Октябрь 2025"),
        ("2025-11", "Ноябрь 2025"),
        ("2025-12", "Декабрь 2025"),
        ("2026-01", "Январь 2026"),
        ("2026-02", "Февраль 2026"),
        ("2026-03", "Март 2026"),
        ("2026-04", "Апрель 2026"),
        ("2026-05", "Май 2026"),
        ("2026-06", "Июнь 2026"),
    ],
    "2026/2027": [
        ("2026-08", "Август 2026"),
        ("2026-09", "Сентябрь 2026"),
        ("2026-10", "Октябрь 2026"),
        ("2026-11", "Ноябрь 2026"),
        ("2026-12", "Декабрь 2026"),
        ("2027-01", "Январь 2027"),
        ("2027-02", "Февраль 2027"),
        ("2027-03", "Март 2027"),
        ("2027-04", "Апрель 2027"),
        ("2027-05", "Май 2027"),
        ("2027-06", "Июнь 2027"),
    ],
}


@dataclass(frozen=True)
class PaymentForOption:
    value: str
    label: str


def current_calendar_period(now: datetime | None = None) -> str:
    current = now or datetime.now()
    return current.strftime("%Y-%m")


def payment_for_options(season: str | None = None) -> list[PaymentForOption]:
    options: list[PaymentForOption] = []
    if season and season in SEASON_PERIODS:
        options.extend(
            PaymentForOption(value=key, label=label) for key, label in SEASON_PERIODS[season]
        )
    else:
        seen: set[str] = set()
        for period_list in SEASON_PERIODS.values():
            for key, label in period_list:
                if key in seen:
                    continue
                seen.add(key)
                options.append(PaymentForOption(value=key, label=label))
    options.append(PaymentForOption(value=TOURNAMENT_KEY, label=TOURNAMENT_LABEL))
    return options


def payment_for_label(value: str | None) -> str | None:
    if not value:
        return None
    if value == TOURNAMENT_KEY:
        return TOURNAMENT_LABEL
    for period_list in SEASON_PERIODS.values():
        for key, label in period_list:
            if key == value:
                return label
    return value


def is_valid_payment_for(value: str | None, season: str | None = None) -> bool:
    if value is None:
        return True
    allowed = {item.value for item in payment_for_options(season)}
    return value in allowed
