import os
import requests
import time
import logging
import json
import sys
import tempfile
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- ІНІЦІАЛІЗАЦІЯ ШЛЯХІВ ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = SCRIPT_DIR
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

HISTORY_FILE = os.path.join(SCRIPT_DIR, "alerts_history.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "monitor.log")
FLAG_ALARM = os.path.join(SCRIPT_DIR, "alarm_active.flag")
FLAG_CANCEL = os.path.join(SCRIPT_DIR, "cancel_active.flag")

# --- НАЛАШТУВАННЯ ЛОГУВАННЯ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- КОНФІГУРАЦІЯ ---
ALERTS_TOKEN = os.getenv("ALERTS_TOKEN", "e422d401:f7fae9e16602c92d41aec965a92d02e3")
ALERTS_API_URL = os.getenv("ALERTS_API_URL", "https://api.ukrainealarm.com/api/v3/alerts/31")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))

def create_session():
    """Створює нову сесію з налаштуваннями повторних спроб."""
    s = requests.Session()
    # Додаємо адаптер для автоматичних ретраїв при помилках мережі
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount("https://", adapter)
    s.headers.update({
        "Authorization": ALERTS_TOKEN.strip(),
        "Accept": "application/json",
        "User-Agent": "KyivAlertMonitor/5.0 (Windows NT 10.0; Win64; x64)"
    })
    return s

session = create_session()

def show_daily_report():
    """Виводить коротке зведення останніх подій."""
    if not os.path.exists(HISTORY_FILE):
        return
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data or not isinstance(data, list): return
        
        day_ago = datetime.now() - timedelta(days=1)
        recent = []
        for e in data:
            try:
                # Надійний парсинг дати
                event_dt = datetime.strptime(f"{e['date']} {e['start']}", "%Y-%m-%d %H:%M:%S")
                if event_dt > day_ago:
                    recent.append(e)
            except (KeyError, ValueError):
                continue
        
        print("\n" + "═"*60)
        logging.info(f"СВОДКА: За останні 24 години виявлено {len(recent)} тривог.")
        if recent:
            last = recent[-1]
            logging.info(f"ПОСЛЕДНЯЯ: {last['start']} -> {last.get('end', '???')} ({last.get('duration_human', 'N/A')})")
        print("═"*60 + "\n")
    except Exception as e:
        logging.error(f"Помилка при читанні звіту: {e}")

def save_alert_to_history(start_time, end_time):
    """Атомарне збереження історії з валідацією даних."""
    if not start_time or not end_time: return
    
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
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    data = json.loads(content) if content else []
            except (json.JSONDecodeError, IOError):
                data = []
        
        if not isinstance(data, list): data = []
        data.append(new_entry)
        data = data[-100:] # Обмежуємо глибину історії

        # Атомарний запис
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(HISTORY_FILE))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
                json.dump(data, tmp, indent=4, ensure_ascii=False)
            os.replace(temp_path, HISTORY_FILE)
        except Exception:
            if os.path.exists(temp_path): os.remove(temp_path)
            raise
        
    except Exception as e:
        logging.error(f"Критична помилка збереження JSON: {e}")

def check_alert_status():
    """Запит статусу з покращеною обробкою відповідей."""
    global session
    try:
        response = session.get(ALERTS_API_URL, timeout=20)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if not data:
                    return False, "Clear (Empty)"
                
                # Обробка списку або об'єкта
                region = data[0] if isinstance(data, list) and len(data) > 0 else data
                
                # Перевірка наявності саме повітряної тривоги (AIR)
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
        
    except (requests.exceptions.RequestException):
        logging.warning("⚠️ Помилка з'єднання. Оновлення сесії...")
        session = create_session()
        return None, "Reconnecting..."
    except Exception as e:
        return None, f"Err: {type(e).__name__}"

if __name__ == "__main__":
    show_daily_report()
    
    # Очищення прапорців при запуску
    for f in [FLAG_ALARM, FLAG_CANCEL]:
        if os.path.exists(f):
            try: os.remove(f)
            except Exception as e: logging.debug(f"Could not remove {f}: {e}")

    logging.info(f"🚀 МОНІТОРИНГ ЗАПУЩЕН. Інтервал: {CHECK_INTERVAL}с")
    print(f"{'Час':<10} | {'Статус':<12} | {'API відповідь':<15}")
    print("-" * 45)

    is_active = False
    alert_start = None

    try:
        while True:
            status, api_msg = check_alert_status()
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')

            # ЛОГІКА ТРИВОГИ
            if status is True and not is_active:
                alert_start = now
                logging.warning("🚨 [START] ТРИВОГА! Створюю флаг.")
                try:
                    with open(FLAG_ALARM, "w") as f: f.write(now.isoformat())
                    if os.path.exists(FLAG_CANCEL): os.remove(FLAG_CANCEL)
                except IOError as e:
                    logging.error(f"Помилка створення флага: {e}")
                is_active = True
            
            elif status is False and is_active:
                logging.info(f"✅ [STOP] ВІДБІЙ ТРИВОГИ.")
                try:
                    if os.path.exists(FLAG_ALARM): os.remove(FLAG_ALARM)
                    with open(FLAG_CANCEL, "w") as f: f.write(now.isoformat())
                except IOError as e:
                    logging.error(f"Помилка видалення/створення флага: {e}")
                
                save_alert_to_history(alert_start, now)
                is_active = False
                alert_start = None
            
            # Візуальне відображення
            tag = "🔴 ТРИВОГА" if is_active else "⚪ ЧИСТО"
            sys.stdout.write(f"\r{time_str:<10} | {tag:<12} | {api_msg:<15}")
            sys.stdout.flush()
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        logging.info("Моніторинг зупинено.")
        sys.exit(0)