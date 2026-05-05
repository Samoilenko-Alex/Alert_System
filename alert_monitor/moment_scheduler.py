import os
import time
import logging
from datetime import datetime
from pathlib import Path

from core.flag_manager import flag_manager

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
FLAG_MOMENT = SCRIPT_DIR / "moment_active.flag"   # для сумісності, хоча краще через manager
LOG_FILE = SCRIPT_DIR / "scheduler.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MOMENT_SCHEDULER] %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
)

def should_create_moment(now: datetime, last_played_date: str) -> bool:
    today = now.strftime('%Y-%m-%d')
    return now.hour == 9 and now.minute == 0 and last_played_date != today


def start_scheduler():
    logging.info("--- ПЛАНУВАЛЬНИК ХВИЛИНИ МОВЧАННЯ ЗАПУЩЕНО ---")
    last_played_date = ""

    try:
        while True:
            now = datetime.now()

            if should_create_moment(now, last_played_date):
                logging.info(f"🕯️ 09:00 — Спроба створити флаг хвилини мовчання для {now.strftime('%Y-%m-%d')}")

                # Використовуємо FlagManager з пріоритетною логікою
                if flag_manager.set_flag("moment"):
                    last_played_date = now.strftime('%Y-%m-%d')
                    logging.info("✅ Флаг хвилини мовчання створено")
                else:
                    logging.info("⏭️ Флаг не створено (ймовірно активна тривога)")

            # Оптимізований сон
            if now.hour == 8 and now.minute >= 59:
                time.sleep(5)
            else:
                time.sleep(30)

    except KeyboardInterrupt:
        logging.info("Планувальник зупинено.")
    except Exception as e:
        logging.critical(f"Критична помилка: {e}")


if __name__ == "__main__":
    # Очищення старого флага при запуску
    flag_manager.clear_flag("moment")
    logging.info("🗑️ Старий флаг хвилини мовчання видалено при запуску")
    start_scheduler()