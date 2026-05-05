import os
import time
import logging

# --- ЖЕСТКАЯ ПРИВЯЗКА ПУТЕЙ (должна совпадать с player_service.py) ---
BASE_DIR = r"C:\kyiv_alert\alert_monitor"
FLAG_ALARM = os.path.join(BASE_DIR, "alarm_active.flag")
FLAG_CANCEL = os.path.join(BASE_DIR, "cancel_active.flag")
FLAG_MOMENT = os.path.join(BASE_DIR, "moment_active.flag")

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def run_test():
    print("\n" + "═"*60)
    logging.info("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА")
    logging.info(f"📁 Папка мониторинга: {BASE_DIR}")
    print("═"*60 + "\n")

    try:
        # Тест 1: Тревога (Сирена)
        logging.info("🚨 ШАГ 1: Создаю FLAG_ALARM (Сирена должна прозвучать один раз)")
        with open(FLAG_ALARM, "w") as f: f.write("1")
        time.sleep(20)

        # Тест 2: Отбой
        logging.info("✅ ШАГ 2: Удаляю FLAG_ALARM и создаю FLAG_CANCEL (Звук отбоя)")
        if os.path.exists(FLAG_ALARM): os.remove(FLAG_ALARM)
        with open(FLAG_CANCEL, "w") as f: f.write("1")
        time.sleep(5)

        # Тест 3: Минута молчания
        logging.info("🕯️ ШАГ 3: Создаю FLAG_MOMENT (Должна начаться минута молчания)")
        with open(FLAG_MOMENT, "w") as f: f.write("1")
        time.sleep(10)

        logging.info("🏁 ТЕСТ ЗАВЕРШЕН.")
        
    except Exception as e:
        logging.error(f"❌ Ошибка теста: {e}")

if __name__ == "__main__":
    run_test()