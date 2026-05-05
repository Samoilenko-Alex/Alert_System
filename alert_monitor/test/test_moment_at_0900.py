import logging
from datetime import datetime

from alert_monitor import moment_scheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TEST_MOMENT_0900] %(message)s'
)


def run_test():
    logging.info("🚀 Починаю тест для хвилини мовчання о 09:00")

    cases = [
        ("2026-04-09 08:59:00", False),
        ("2026-04-09 09:00:00", True),
        ("2026-04-09 09:00:30", False),
        ("2026-04-09 09:01:00", False),
        ("2026-04-10 09:00:00", True),
    ]

    last_played_date = ""
    for ts, expected in cases:
        now = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        result = moment_scheduler.should_create_moment_flag(now, last_played_date)
        logging.info(f"Тест {ts}: очікується={expected}, отримано={result}")
        if result != expected:
            logging.error("❌ Результат не співпадає")
            return False
        if result:
            last_played_date = now.strftime('%Y-%m-%d')

    logging.info("✅ Тест пройдено. Логіка створення флага 09:00 працює.")
    return True


if __name__ == '__main__':
    success = run_test()
    exit(0 if success else 1)
