import os
import subprocess
import time
import atexit
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

from flask import Flask, render_template, jsonify, send_from_directory, make_response
from flask_cors import CORS

from alert_monitor.core.flag_manager import flag_manager

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [WEB] %(message)s',
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__, 
            template_folder='templates',      # явно вказуємо папку шаблонів
            static_folder='templates',        # статичні файли тепер з templates/
            static_url_path='/static')        # URL буде /static/...

CORS(app, resources={r"/*": {"origins": "*"}})

# --- КОНФІГУРАЦІЯ ---
PYTHON_EXE = r"C:\kyiv_alert\venv\Scripts\python.exe"
BASE_DIR = Path(r"C:\kyiv_alert\alert_monitor")
AUDIO_DIR = Path(r"C:\kyiv_alert\silence_moment")

SCRIPTS = {
    "monitor":   str(BASE_DIR / "monitor.py"),
    "player":    str(BASE_DIR / "player_service.py"),
    "scheduler": str(BASE_DIR / "moment_scheduler.py")
}

active_resources = {name: {"proc": None, "file": None} for name in SCRIPTS}


def get_tail(name: str, lines_count: int = 20) -> str:
    log_path = BASE_DIR / f"{name}.log"
    if not log_path.exists():
        return "📡 Очікування ініціалізації логів..."

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            return "".join(lines[-lines_count:])
    except Exception as e:
        return f"⚠️ Помилка доступу до логу: {e}"


def is_running(name: str) -> bool:
    res = active_resources.get(name)
    if not res:
        return False

    if res["proc"] and res["proc"].poll() is None:
        return True

    if name == "player":
        lock_file = BASE_DIR / "player_lock.lock"
        if lock_file.exists():
            try:
                with open(lock_file, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                return True
            except (OSError, ValueError):
                return False
    return False


def stop_script(name: str):
    res = active_resources[name]
    stopped = False

    if res["proc"] and res["proc"].poll() is None:
        try:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(res["proc"].pid)],
                           capture_output=True, check=False)
            res["proc"].wait(timeout=2)
            stopped = True
        except:
            if res["proc"]:
                res["proc"].kill()
            stopped = True

    if name == "player":
        lock_file = BASE_DIR / "player_lock.lock"
        if lock_file.exists():
            try:
                with open(lock_file, "r") as f:
                    pid = int(f.read().strip())
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True)
            except:
                pass
            try:
                lock_file.unlink()
            except:
                pass
            stopped = True

    if res["file"]:
        try:
            res["file"].close()
        except:
            pass

    if stopped:
        logging.info(f"⏹️ Скрипт зупинено: {name}")

    active_resources[name] = {"proc": None, "file": None}


def start_script(name: str):
    if name not in SCRIPTS or not os.path.exists(SCRIPTS[name]):
        logging.error(f"Файл не знайдено: {SCRIPTS.get(name)}")
        return

    if name == "player":
        lock_file = BASE_DIR / "player_lock.lock"
        if lock_file.exists():
            try:
                with open(lock_file, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                logging.info("✅ Player вже запущений (lock-файл)")
                return
            except (OSError, ValueError):
                try:
                    lock_file.unlink()
                except:
                    pass

    stop_script(name)

    log_path = BASE_DIR / f"{name}.log"
    log_file = open(log_path, "a", encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.Popen(
        [PYTHON_EXE, "-u", SCRIPTS[name]],
        stdout=log_file,
        stderr=log_file,
        cwd=str(BASE_DIR),
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )

    active_resources[name] = {"proc": proc, "file": log_file}
    logging.info(f"✅ Запущено скрипт: {name} (PID: {proc.pid})")


@atexit.register
def cleanup_on_exit():
    logging.info("Виконується cleanup при завершенні веб-сервера...")
    for name in SCRIPTS:
        stop_script(name)
    flag_manager.clear_all()


def clear_all_flags():
    flag_manager.clear_all()


# ====================== СТАТИЧНІ ФАЙЛИ ======================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Обслуговування CSS, JS та інших статичних файлів"""
    return send_from_directory('templates', filename)


@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    """Обслуговування аудіофайлів"""
    decoded_name = unquote(filename)
    logging.info(f"🔊 Запит аудіо: {decoded_name}")
    
    response = make_response(send_from_directory(str(AUDIO_DIR), decoded_name))
    
    if decoded_name.endswith('.wav'):
        response.headers['Content-Type'] = 'audio/wav'
    
    return response


# ====================== РОУТИ ======================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def get_status():
    states = {n: ("ПРАЦЮЄ" if is_running(n) else "ЗУПИНЕНО") for n in SCRIPTS}

    status_text = "ЧИСТО"
    if flag_manager.is_set("moment"):
        status_text = "🕯️ ХВИЛИНА МОВЧАННЯ"
    elif flag_manager.is_set("alarm"):
        status_text = "🚨 ПОВІТРЯНА ТРИВОГА"

    return jsonify({
        "status_text": status_text,
        "is_alarm": flag_manager.is_set("alarm"),
        "is_moment": flag_manager.is_set("moment"),
        "scripts": states,
        "logs": {name: get_tail(name) for name in SCRIPTS},
        "server_time": datetime.now().strftime("%H:%M:%S")
    })


@app.route('/toggle/<name>')
def toggle_script(name):
    if name not in SCRIPTS:
        return jsonify({"error": "Unknown script"}), 400

    if is_running(name):
        stop_script(name)
    else:
        start_script(name)

    return jsonify({"status": "ok"})


@app.route('/manual/<action>')
def manual_trigger(action):
    if action == "stop_all":
        clear_all_flags()
        return jsonify({"status": "ok"})

    key = action.replace("test_", "")

    if key in ["alarm", "cancel", "moment"]:
        success = flag_manager.set_flag(key)
        if success:
            logging.info(f"Manual trigger: {key.upper()}")
        return jsonify({"status": "ok"})

    return jsonify({"error": "Unknown action"}), 400


@app.route('/test')
def test():
    return 'test'


if __name__ == '__main__':
    try:
        logging.info("🚀 Запуск веб-сервера Kyiv Alert")
        clear_all_flags()

        for name in SCRIPTS:
            start_script(name)

        print(app.url_map)
        app.run(host='0.0.0.0', port=5000, debug=False)

    except Exception as e:
        logging.critical(f"Критична помилка запуску: {e}")
        import traceback
        traceback.print_exc()