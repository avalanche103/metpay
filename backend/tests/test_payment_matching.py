from app.services.payment_matching import name_variants, normalize_full_name


def test_format_full_name_title_cases_parts() -> None:
    from app.services.payment_matching import format_full_name

    assert format_full_name("иванов иван иванович") == "Иванов Иван Иванович"
    assert format_full_name("  МАСКАЛЬЧУК   илья ") == "Маскальчук Илья"
    assert format_full_name("петров-сидоров петр") == "Петров-Сидоров Петр"


def test_normalize_full_name_removes_noise() -> None:
    assert normalize_full_name("  Иванов   Пётр-Сергеевич! ") == "иванов петр сергеевич"


def test_name_variants_include_reordered_parts() -> None:
    variants = name_variants("Иванов Петр")

    assert "иванов петр" in variants
    assert "петр иванов" in variants
