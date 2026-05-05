import winsound
import os
import time
import logging

# --- КОНФІГУРАЦІЯ ШЛЯХІВ ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = r"C:\kyiv_alert\silence_moment"

SOUNDS = {
    "alarm": os.path.join(AUDIO_DIR, "alarm.wav"),
    "cancel": os.path.join(AUDIO_DIR, "cancel.wav"),
    "moment": os.path.join(AUDIO_DIR, "moment.wav")
}

FLAGS = {
    "alarm": os.path.join(SCRIPT_DIR, "alarm_active.flag"),
    "cancel": os.path.join(SCRIPT_DIR, "cancel_active.flag"),
    "moment": os.path.join(SCRIPT_DIR, "moment_active.flag")
}

# --- НАЛАШТУВАННЯ ЛОГУВАННЯ ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, "player.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def stop_all_audio():
    """Зупиняє будь-яке поточне відтворення winsound."""
    try:
        winsound.PlaySound(None, winsound.SND_ASYNC)
    except:
        pass

def safe_remove(path):
    """Безпечне видалення файлу-прапорця."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logging.debug(f"Не вдалося видалити флаг {path}: {e}")

def play_event(name, loop=False):
    """Запускає відтворення звуку за іменем."""
    sound_path = SOUNDS.get(name)
    if not sound_path or not os.path.exists(sound_path):
        logging.error(f"❌ Файл для '{name}' не знайдено за шляхом: {sound_path}")
        return False
    
    flags = winsound.SND_FILENAME | winsound.SND_ASYNC
    if loop:
        flags |= winsound.SND_LOOP
    
    try:
        stop_all_audio()
        winsound.PlaySound(sound_path, flags)
        logging.info(f"▶️ ВІДТВОРЕННЯ: {name.upper()} {'(зациклено)' if loop else ''}")
        return True
    except Exception as e:
        logging.error(f"❌ Помилка winsound: {e}")
        return False

def main():
    logging.info("🔊 Player Service успішно запущено")
    current_state = None
    
    while True:
        try:
            # 1. НАЙВИЩИЙ ПРІОРИТЕТ: ХВИЛИНА МОВЧАННЯ
            if os.path.exists(FLAGS["moment"]):
                logging.info("🕯️ Отримано сигнал: Хвилина мовчання")
                if play_event("moment", loop=False):
                    current_state = 'moment'
                
                # НОВА ЛОГІКА: чекаємо 65 секунд, але перевіряємо флаг кожну секунду
                # (щоб Emergency Stop спрацював миттєво)
                start_wait = time.time()
                while time.time() - start_wait < 65:
                    if not os.path.exists(FLAGS["moment"]):
                        logging.info("🛑 Emergency Stop виявлено під час хвилини мовчання — зупиняю звук")
                        stop_all_audio()
                        break
                    time.sleep(1)
                
                safe_remove(FLAGS["moment"])
                current_state = None
                continue

            # 2. ПРІОРИТЕТ: ВІДБІЙ ТРИВОГИ
            if os.path.exists(FLAGS["cancel"]):
                logging.info("✅ Отримано сигнал: Відбій")
                play_event("cancel", loop=False)
                
                safe_remove(FLAGS["cancel"])
                safe_remove(FLAGS["alarm"])
                
                current_state = 'cancel'
                time.sleep(10)
                current_state = None
                continue

            # 3. ПРІОРИТЕТ: ПОВІТРЯНА ТРИВОГА
            if os.path.exists(FLAGS["alarm"]):
                if current_state != 'alarm':
                    if play_event("alarm", loop=True):
                        current_state = 'alarm'
            else:
                if current_state == 'alarm':
                    logging.info("⏹️ Флаг тривоги видалено, зупиняю сирену")
                    stop_all_audio()
                    current_state = None

            time.sleep(1)

        except Exception as e:
            logging.error(f"⚠️ Критична помилка у головному циклі плеєра: {e}")
            time.sleep(2)

if __name__ == "__main__":
    stop_all_audio()
    main()