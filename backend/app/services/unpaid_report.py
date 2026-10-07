from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Group, Payment, Student, StudentMonthSkip
from app.services.season_periods import TOURNAMENT_KEY, payment_for_label


def payment_period_key(payment: Payment) -> str | None:
    if payment.payment_for and payment.payment_for != TOURNAMENT_KEY:
        return payment.payment_for
    if payment.paid_at is None:
        return None
    return payment.paid_at.strftime("%Y-%m")


def effective_monthly_fee(student: Student) -> Decimal | None:
    """Per-student fee overrides group fee when set (discount / custom price)."""
    if student.monthly_fee is not None:
        return Decimal(str(student.monthly_fee))
    group: Group | None = student.group
    if group and group.monthly_fee is not None:
        return Decimal(str(group.monthly_fee))
    return None


def build_unpaid_by_month_report(
    db: Session,
    *,
    period: str,
    group_id: int | None = None,
    status_filter: str = "not_full",
) -> dict:
    if status_filter not in {"not_full", "unpaid", "partial"}:
        raise ValueError("Некорректный фильтр статуса")

    students_query = (
        select(Student)
        .options(joinedload(Student.group))
        .where(Student.active.is_(True), Student.group_id.is_not(None))
        .order_by(Student.full_name)
    )
    if group_id is not None:
        students_query = students_query.where(Student.group_id == group_id)
    students = list(db.scalars(students_query).unique())

    skipped_ids = {
        skip.student_id
        for skip in db.scalars(
            select(StudentMonthSkip).where(StudentMonthSkip.period == period)
        )
    }

    payments = list(
        db.scalars(select(Payment).where(Payment.student_id.is_not(None)).order_by(Payment.id))
    )
    paid_by_student: dict[int, Decimal] = {}
    full_credit: set[int] = set()
    for payment in payments:
        if payment.student_id is None:
            continue
        if payment_period_key(payment) != period:
            continue
        paid_by_student[payment.student_id] = paid_by_student.get(
            payment.student_id, Decimal("0.00")
        ) + Decimal(str(payment.amount))
        if payment.counts_as_full:
            full_credit.add(payment.student_id)

    items: list[dict] = []
    unpaid_count = 0
    partial_count = 0
    expected_total = Decimal("0.00")

    for student in students:
        if student.id in skipped_ids or student.id in full_credit:
            continue

        group: Group | None = student.group
        fee = effective_monthly_fee(student)
        paid = paid_by_student.get(student.id, Decimal("0.00")).quantize(Decimal("0.01"))

        if fee is not None and paid + Decimal("0.001") >= fee:
            continue
        if fee is None and paid > 0:
            continue

        if fee is None:
            status = "unpaid"
            expected = Decimal("0.00")
        elif paid <= 0:
            status = "unpaid"
            expected = fee
        else:
            status = "partial"
            expected = (fee - paid).quantize(Decimal("0.01"))

        if status_filter == "unpaid" and status != "unpaid":
            continue
        if status_filter == "partial" and status != "partial":
            continue

        if status == "unpaid":
            unpaid_count += 1
        else:
            partial_count += 1

        expected_total += expected
        items.append(
            {
                "student_id": student.id,
                "student_full_name": student.full_name,
                "group_id": group.id if group else None,
                "group_name": group.name if group else None,
                "monthly_fee": str(fee) if fee is not None else None,
                "paid_amount": str(paid),
                "expected_amount": str(expected),
                "status": status,
            }
        )

    items.sort(
        key=lambda item: (
            item["group_name"] or "",
            item["student_full_name"] or "",
        )
    )

    return {
        "period": period,
        "period_label": payment_for_label(period) or period,
        "status_filter": status_filter,
        "unpaid_count": unpaid_count,
        "partial_count": partial_count,
        "expected_total": str(expected_total.quantize(Decimal("0.01"))),
        "items": items,
    }
