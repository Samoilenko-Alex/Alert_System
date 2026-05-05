import os
import time
import logging
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_MOMENT = os.path.join(SCRIPT_DIR, "moment_active.flag")
LOG_FILE = os.path.join(SCRIPT_DIR, "scheduler.log")

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [MOMENT_SCHEDULER] %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
)

def start_scheduler():
    logging.info("--- ПЛАНУВАЛЬНИК ЗАПУЩЕНО (Очікування 09:00) ---")
    last_played_date = ""

    try:
        while True:
            now = datetime.now()
            today_str = now.strftime('%Y-%m-%d')

            # Реальна бойова логіка — тільки о 09:00 один раз на день
            if now.hour == 9 and now.minute == 0:
                if last_played_date != today_str:
                    logging.info(f"🕯️ 09:00! Створюю флаг хвилини мовчання для {today_str}...")
                    with open(FLAG_MOMENT, "w", encoding="utf-8") as f:
                        f.write(f"start_{today_str}_{now.strftime('%H:%M:%S')}")
                    last_played_date = today_str
                    logging.info("✅ Флаг створено. Очікуємо завтра.")
            
            # Оптимізований сон
            if now.hour == 8 and now.minute == 59:
                time.sleep(5)
            else:
                time.sleep(30)
            
    except KeyboardInterrupt:
        logging.info("Планувальник зупинено.")
    except Exception as e:
        logging.critical(f"Критична помилка: {e}")

if __name__ == "__main__":
    if os.path.exists(FLAG_MOMENT):
        try:
            os.remove(FLAG_MOMENT)
            logging.info("🗑️ Старий флаг видалено при запуску.")
        except:
            pass
    start_scheduler()