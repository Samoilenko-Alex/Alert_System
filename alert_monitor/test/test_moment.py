import os
import time
import logging

# --- КОНФИГУРАЦИЯ ---
BASE_DIR = r"C:\kyiv_alert\alert_monitor"
FLAG_MOMENT = os.path.join(BASE_DIR, "moment_active.flag")

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [TEST_MOMENT] %(message)s'
)

def run_test():
    logging.info("🚀 ЗАПУСК ТЕСТА: Хвилина мовчання")
    
    # 1. Проверяем, запущен ли плеер (визуально)
    logging.info("Убедитесь, что player_service.py запущен в соседнем окне!")
    
    # 2. Создаем флаг
    logging.info(f"Создаю флаг: {os.path.basename(FLAG_MOMENT)}")
    try:
        with open(FLAG_MOMENT, "w", encoding="utf-8") as f:
            f.write("test_start")
        logging.info("✅ Флаг создан. Слушайте звук...")
    except Exception as e:
        logging.error(f"❌ Не удалось создать флаг: {e}")
        return

    # 3. Ожидание реакции плеера
    logging.info("Ожидание 15 секунд (плеер должен подхватить флаг и начать играть)...")
    time.sleep(15)

    # 4. Проверка, удалил ли плеер флаг
    if not os.path.exists(FLAG_MOMENT):
        logging.info("🎊 УСПЕХ: Плеер обнаружил и удалил флаг.")
    else:
        logging.warning("⚠️ ВНИМАНИЕ: Флаг все еще на месте. Проверьте логи player_service.py!")

    logging.info("🏁 Тест завершен.")

if __name__ == "__main__":
    run_test()