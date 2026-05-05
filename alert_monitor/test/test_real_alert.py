import os
import time
import logging
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
BASE_DIR = r"C:\kyiv_alert\alert_monitor"
FLAG_ALARM = os.path.join(BASE_DIR, "alarm_active.flag")
FLAG_CANCEL = os.path.join(BASE_DIR, "cancel_active.flag")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TEST_REAL_ALERT] %(message)s'
)

def simulate_real_alert():
    logging.info("🚨 ЗАПУСК ИМИТАЦИИ РЕАЛЬНОЙ ТРЕВОГИ")

    # 1. ИМИТАЦИЯ НАЧАЛА ТРЕВОГИ (как monitor.py)
    logging.info("🚨 ШАГ 1: Имитирую начало тревоги от API. Создаю FLAG_ALARM.")
    with open(FLAG_ALARM, "w") as f:
        f.write(datetime.now().isoformat())
    logging.info("✅ Флаг тревоги создан. Система должна воспроизвести сирену один раз.")

    # Ждем 30 секунд (имитируя длительность тревоги)
    logging.info("⏳ Ожидание 30 секунд (имитация реальной тревоги)...")
    time.sleep(30)

    # 2. ИМИТАЦИЯ ОТБОЯ ТРЕВОГИ (как monitor.py)
    logging.info("✅ ШАГ 2: Имитирую отбой тревоги. Удаляю FLAG_ALARM и создаю FLAG_CANCEL.")
    if os.path.exists(FLAG_ALARM):
        os.remove(FLAG_ALARM)
    with open(FLAG_CANCEL, "w") as f:
        f.write(datetime.now().isoformat())
    logging.info("✅ Флаг отбоя создан. Система должна воспроизвести сигнал отбоя.")

    # Ждем 10 секунд (время воспроизведения отбоя)
    logging.info("⏳ Ожидание 10 секунд (время воспроизведения отбоя)...")
    time.sleep(10)

    # 3. ОЧИСТКА
    if os.path.exists(FLAG_CANCEL):
        os.remove(FLAG_CANCEL)
    logging.info("🧹 Флаги очищены.")

    logging.info("🏁 ИМИТАЦИЯ РЕАЛЬНОЙ ТРЕВОГИ ЗАВЕРШЕНА.")

if __name__ == "__main__":
    simulate_real_alert()