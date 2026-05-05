import os
import time
import logging

# --- ПУТИ ---
BASE_DIR = r"C:\kyiv_alert\alert_monitor"
FLAG_ALARM = os.path.join(BASE_DIR, "alarm_active.flag")
FLAG_CANCEL = os.path.join(BASE_DIR, "cancel_active.flag")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TEST_ALARM] %(message)s')

def run_alarm_test():
    logging.info("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА ТРЕВОГИ")
    
    # 1. ВКЛЮЧАЕМ ТРЕВОГУ
    logging.info("🚨 ШАГ 1: Создаю FLAG_ALARM. Сирена должна зациклиться.")
    with open(FLAG_ALARM, "w") as f:
        f.write("test_active")
    
    logging.info("Слушайте сирену 15 секунд...")
    time.sleep(15)

    # 2. ВЫКЛЮЧАЕМ ТРЕВОГУ
    logging.info("🛑 ШАГ 2: Удаляю FLAG_ALARM. Сирена должна мгновенно смолкнуть.")
    if os.path.exists(FLAG_ALARM):
        os.remove(FLAG_ALARM)
    else:
        logging.warning("Флаг тревоги не найден (возможно, плеер его удалил сам? Проверьте логи).")
    
    time.sleep(2) # Пауза перед отбоем

    # 3. ВКЛЮЧАЕМ ОТБОЙ
    logging.info("✅ ШАГ 3: Создаю FLAG_CANCEL. Должен прозвучать сигнал отбоя.")
    with open(FLAG_CANCEL, "w") as f:
        f.write("test_cancel")
    
    logging.info("Ожидание реакции плеера (5 секунд)...")
    time.sleep(5)

    if not os.path.exists(FLAG_CANCEL):
        logging.info("🎊 УСПЕХ: Плеер подхватил отбой и удалил флаг.")
    else:
        logging.warning("⚠️ Флаг отбоя все еще на месте.")

    logging.info("🏁 ТЕСТ ЗАВЕРШЕН.")

if __name__ == "__main__":
    run_alarm_test()