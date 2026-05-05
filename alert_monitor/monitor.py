import os
import requests
import time
import logging
import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from core.flag_manager import flag_manager

# --- ІНІЦІАЛІЗАЦІЯ ШЛЯХІВ ---
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = SCRIPT_DIR

load_dotenv(SCRIPT_DIR / ".env")

HISTORY_FILE = SCRIPT_DIR / "alerts_history.json"
LOG_FILE = SCRIPT_DIR / "monitor.log"

# --- НАЛАШТУВАННЯ ЛОГУВАННЯ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MONITOR] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- КОНФІГУРАЦІЯ ---
ALERTS_TOKEN = os.getenv("ALERTS_TOKEN", "e422d401:f7fae9e16602c92d41aec965a92d02e3")
ALERTS_API_URL = os.getenv("ALERTS_API_URL", "https://api.ukrainealarm.com/api/v3/alerts/31")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))

# Глобальна змінна для збереження часу початку тривоги (між циклами)
CURRENT_ALERT_START_FILE = SCRIPT_DIR / "current_alert_start.tmp"


def get_api_info():
    source = "official UkraineAlarm API" if "ukrainealarm.com" in ALERTS_API_URL else "public wrapper"
    token_state = "present" if ALERTS_TOKEN.strip() else "missing"
    return source, token_state


def build_authorization_header(token):
    token = (token or "").strip()
    if not token:
        return {}
    normalized = token.lower()
    if normalized.startswith(("bearer ", "token ", "basic ")):
        return {"Authorization": token}
    return {"Authorization": token}


def create_session():
    """Створює сесію з ретраями."""
    s = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount("https://", adapter)
    headers = {
        **build_authorization_header(ALERTS_TOKEN),
        "Accept": "application/json",
        "User-Agent": "KyivAlertMonitor/5.0 (Windows NT 10.0; Win64; x64)"
    }
    s.headers.update(headers)
    return s


session = create_session()


def load_alert_start() -> datetime | None:
    """Завантажує час початку тривоги з файлу (щоб не губити при рестарті)."""
    if not CURRENT_ALERT_START_FILE.exists():
        return None
    try:
        with open(CURRENT_ALERT_START_FILE, "r", encoding="utf-8") as f:
            dt_str = f.read().strip()
            return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def save_alert_start(start_time: datetime):
    """Зберігає час початку тривоги у файл."""
    try:
        with open(CURRENT_ALERT_START_FILE, "w", encoding="utf-8") as f:
            f.write(start_time.isoformat())
    except Exception as e:
        logging.error(f"Не вдалося зберегти час початку тривоги: {e}")


def clear_alert_start():
    """Видаляє тимчасовий файл початку тривоги."""
    try:
        if CURRENT_ALERT_START_FILE.exists():
            CURRENT_ALERT_START_FILE.unlink()
    except Exception:
        pass


def show_daily_report():
    """Виводить зведення за останні 24 години."""
    if not HISTORY_FILE.exists():
        return
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data or not isinstance(data, list):
            return

        day_ago = datetime.now() - timedelta(days=1)
        recent = []
        for e in data:
            try:
                event_dt = datetime.strptime(f"{e['date']} {e['start']}", "%Y-%m-%d %H:%M:%S")
                if event_dt > day_ago:
                    recent.append(e)
            except (KeyError, ValueError):
                continue

        print("\n" + "═" * 60)
        logging.info(f"СВОДКА: За останні 24 години виявлено {len(recent)} тривог.")
        if recent:
            last = recent[-1]
            logging.info(f"ОСТАННЯ: {last['start']} → {last.get('end', '???')} ({last.get('duration_human', 'N/A')})")
        print("═" * 60 + "\n")
    except Exception as e:
        logging.error(f"Помилка читання звіту: {e}")


def save_alert_to_history(start_time: datetime, end_time: datetime):
    """Атомарне збереження історії тривог."""
    if not start_time or not end_time:
        return

    duration = end_time - start_time
    total_sec = int(duration.total_seconds())
    duration_str = f"{total_sec // 3600:02}:{(total_sec % 3600) // 60:02}:{total_sec % 60:02}"

    new_entry = {
        "date": start_time.strftime("%Y-%m-%d"),
        "start": start_time.strftime("%H:%M:%S"),
        "end": end_time.strftime("%H:%M:%S"),
        "duration_human": duration_str
    }

    try:
        data = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    data = json.loads(content) if content else []
            except (json.JSONDecodeError, IOError):
                data = []

        if not isinstance(data, list):
            data = []

        data.append(new_entry)
        data = data[-100:]  # обмежуємо історію

        # Атомарний запис
        fd, temp_path = tempfile.mkstemp(dir=str(HISTORY_FILE.parent))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
                json.dump(data, tmp, indent=4, ensure_ascii=False)
            os.replace(temp_path, str(HISTORY_FILE))
            logging.info(f"Збережено в історію: {duration_str}")
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    except Exception as e:
        logging.error(f"Критична помилка збереження історії: {e}")


def check_alert_status():
    """Запит до API UkraineAlarm."""
    global session
    try:
        response = session.get(ALERTS_API_URL, timeout=20)

        if response.status_code == 200:
            try:
                data = response.json()
                if not data:
                    return False, "Clear (Empty)"

                region = data[0] if isinstance(data, list) and len(data) > 0 else data
                alerts = region.get("activeAlerts", [])
                is_active = any(a.get("type") == "AIR" for a in alerts) if alerts else False

                return is_active, "OK"
            except (json.JSONDecodeError, TypeError, IndexError):
                return None, "JSON Error"

        if response.status_code == 401:
            return None, "401 (Auth Error)"
        if response.status_code == 429:
            return None, "429 (Too Many Requests)"

        return None, f"HTTP {response.status_code}"

    except requests.exceptions.RequestException:
        logging.warning("⚠️ Помилка з'єднання з API. Перестворюємо сесію...")
        session = create_session()
        return None, "Reconnecting..."
    except Exception as e:
        return None, f"Err: {type(e).__name__}"


if __name__ == "__main__":
    show_daily_report()

    api_source, token_state = get_api_info()
    logging.info(f"API: {ALERTS_API_URL} ({api_source}), token: {token_state}")

    if "ukrainealarm.com" in ALERTS_API_URL and not ALERTS_TOKEN.strip():
        logging.warning("Офіційний API без токена — можливий 401.")

    # Очищення флагів при запуску через FlagManager
    flag_manager.clear_flag("alarm")
    flag_manager.clear_flag("cancel")
    clear_alert_start()

    logging.info(f"🚀 МОНІТОРИНГ ЗАПУЩЕНО. Інтервал: {CHECK_INTERVAL}с")
    print(f"{'Час':<10} | {'Статус':<12} | {'API':<15}")
    print("-" * 45)

    is_active = False
    alert_start: datetime | None = None

    try:
        while True:
            status, api_msg = check_alert_status()
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')

            # === ЛОГІКА ТРИВОГИ ===
            if status is True and not is_active:
                alert_start = now
                save_alert_start(alert_start)                    # зберігаємо на випадок рестарту
                logging.warning("🚨 [START] ПОВІТРЯНА ТРИВОГА")

                flag_manager.set_flag("alarm", alert_start.isoformat())
                flag_manager.clear_flag("cancel")

                is_active = True

            elif status is False and is_active:
                logging.info("✅ [STOP] ВІДБІЙ ТРИВОГИ")

                flag_manager.clear_flag("alarm")
                flag_manager.set_flag("cancel")                  # створюємо флаг відбою

                if alert_start:
                    save_alert_to_history(alert_start, now)

                clear_alert_start()
                is_active = False
                alert_start = None

            # Візуальне відображення в консолі
            tag = "🔴 ТРИВОГА" if is_active else "⚪ ЧИСТО"
            sys.stdout.write(f"\r{time_str:<10} | {tag:<12} | {api_msg:<15}")
            sys.stdout.flush()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        sys.stdout.write("\n")
        logging.info("Моніторинг зупинено користувачем.")
        # При зупинці теж зберігаємо поточний стан
        if is_active and alert_start:
            save_alert_start(alert_start)
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Критична помилка в моніторі: {e}", exc_info=True)