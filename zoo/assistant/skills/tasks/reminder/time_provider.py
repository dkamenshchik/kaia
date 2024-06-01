from datetime import datetime, timedelta


class TimeProvider:
    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def time_to_timedelta(time_str: str) -> timedelta:
        h, m = map(int, time_str.split(":"))
        return timedelta(hours=h, minutes=m)

    def is_time_within_delta(self, time: timedelta, delta_minutes: int) -> bool:
        now = self.now()
        now_time = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        diff = (now_time - time).total_seconds() / 60
        return 0 <= diff <= delta_minutes
