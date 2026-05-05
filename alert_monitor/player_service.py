import winsound
import os
import time
import logging
from pathlib import Path

from core.flag_manager import flag_manager

# --- КОНФІГУРАЦІЯ ---
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = Path(r"C:\kyiv_alert\silence_moment")

SOUNDS = {
    "alarm": AUDIO_DIR / "alarm.wav",
    "cancel": AUDIO_DIR / "cancel.wav",
    "moment": AUDIO_DIR / "moment.wav"
}

LOCK_FILE = SCRIPT_DIR / "player_lock.lock"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [PLAYER] %(message)s',
    handlers=[
        logging.FileHandler(SCRIPT_DIR / "player.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def stop_all_audio():
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except:
        pass


def play_event(name: str) -> bool:
    """Відтворює звук асинхронно (alarm більше не блокує цикл)."""
    sound_path = SOUNDS.get(name)
    if not sound_path or not sound_path.exists():
        logging.error(f"❌ Файл {name}.wav не знайдено")
        return False

    flags = winsound.SND_FILENAME | winsound.SND_ASYNC

    try:
        stop_all_audio()
        winsound.PlaySound(str(sound_path), flags)
        logging.info(f"▶️ Відтворення: {name.upper()}")
        return True
    except Exception as e:
        logging.error(f"Помилка відтворення {name}: {e}")
        return False


def main():
    logging.info("🔊 Player Service запущено")

    # Перевірка lock
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            logging.error("❌ Player вже запущений. Вихід.")
            return
        except (OSError, ValueError):
            try: LOCK_FILE.unlink()
            except: pass

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    try:
        alarm_played = False
        logging.info("🔄 Головний цикл плеєра активний")

        while True:
            # 1. Найвищий пріоритет — ВІДБІЙ
            if flag_manager.is_set("cancel"):
                logging.info("✅ Відбій тривоги")
                play_event("cancel")
                flag_manager.clear_flag("cancel")
                flag_manager.clear_flag("alarm")
                flag_manager.clear_flag("moment")
                alarm_played = False
                time.sleep(8)
                continue

            # 2. ТРИВОГА
            if flag_manager.is_set("alarm"):
                if not alarm_played:
                    if play_event("alarm"):
                        alarm_played = True
                        logging.info("🚨 Сирена запущена (асинхронно)")
                time.sleep(1)
                continue

            # 3. ХВИЛИНА МОВЧАННЯ
            if flag_manager.is_set("moment"):
                if flag_manager.is_set("alarm"):
                    logging.info("🚨 Тривога активна — пропускаємо хвилину мовчання")
                    flag_manager.clear_flag("moment")
                    time.sleep(1)
                    continue

                logging.info("🕯️ Хвилина мовчання")
                play_event("moment")
                start = time.time()

                while time.time() - start < 65:
                    if not flag_manager.is_set("moment"):
                        break
                    if flag_manager.is_set("alarm") or flag_manager.is_set("cancel"):
                        logging.info("⚠️ Перервано тривогою/відбоєм")
                        stop_all_audio()
                        break
                    time.sleep(1)

                flag_manager.clear_flag("moment")
                alarm_played = False
                continue

            # Якщо флаг тривоги зник зовні
            if alarm_played and not flag_manager.is_set("alarm"):
                logging.info("⏹️ Тривогу скасовано зовні — зупиняємо звук")
                stop_all_audio()
                alarm_played = False

            time.sleep(0.8)

    except KeyboardInterrupt:
        logging.info("Player Service зупинено користувачем")
    except Exception as e:
        logging.critical(f"Критична помилка: {e}", exc_info=True)
    finally:
        stop_all_audio()
        try: LOCK_FILE.unlink()
        except: pass
        logging.info("Player Service завершено")


if __name__ == "__main__":
    main()