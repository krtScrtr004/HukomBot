import calendar
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class DateTimeRange:
    start: datetime | None
    end: datetime | None


class DateRange(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_6_MONTHS = "last_6_months"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    ALL_TIME = "all_time"

    def to_range(self, now: datetime | None = None) -> DateTimeRange:
        now = now or datetime.now()

        today_start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if self is DateRange.ALL_TIME:
            return DateTimeRange(None, None)

        if self is DateRange.TODAY:
            return DateTimeRange(
                today_start,
                now,
            )

        if self is DateRange.YESTERDAY:
            return DateTimeRange(
                today_start - timedelta(days=1),
                today_start,
            )

        if self is DateRange.THIS_WEEK:
            start = today_start - timedelta(days=today_start.weekday())

            return DateTimeRange(
                start,
                now,
            )

        if self is DateRange.LAST_WEEK:
            this_week_start = today_start - timedelta(days=today_start.weekday())

            return DateTimeRange(
                this_week_start - timedelta(weeks=1),
                this_week_start,
            )

        if self is DateRange.THIS_MONTH:
            return DateTimeRange(
                today_start.replace(day=1),
                now,
            )

        if self is DateRange.LAST_MONTH:
            this_month_start = today_start.replace(day=1)

            return DateTimeRange(
                _shift_months(this_month_start, -1),
                this_month_start,
            )

        if self is DateRange.LAST_7_DAYS:
            return DateTimeRange(
                now - timedelta(days=7),
                now,
            )

        if self is DateRange.LAST_30_DAYS:
            return DateTimeRange(
                now - timedelta(days=30),
                now,
            )

        if self is DateRange.LAST_90_DAYS:
            return DateTimeRange(
                now - timedelta(days=90),
                now,
            )

        if self is DateRange.LAST_6_MONTHS:
            return DateTimeRange(
                _shift_months(now, -6),
                now,
            )

        if self is DateRange.THIS_YEAR:
            return DateTimeRange(
                today_start.replace(month=1, day=1),
                now,
            )

        if self is DateRange.LAST_YEAR:
            this_year_start = today_start.replace(
                month=1,
                day=1,
            )

            return DateTimeRange(
                this_year_start.replace(year=this_year_start.year - 1),
                this_year_start,
            )

        raise NotImplementedError(f"No datetime mapping defined for {self!r}")


def _shift_months(dt: datetime, months: int) -> datetime:
    """Shift `dt` by `months`, clamping the day to the target month's length."""
    total = dt.month - 1 + months
    year = dt.year + total // 12
    month = total % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)
