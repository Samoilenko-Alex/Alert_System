import os
import subprocess
import time
import atexit
from datetime import datetime
from urllib.parse import unquote  # Важливо для кирилиці
from flask import Flask, render_template, jsonify, send_from_directory, make_response

app = Flask(__name__)

# --- КОНФІГУРАЦІЯ ---
PYTHON_EXE = r"C:\kyiv_alert\venv\Scripts\python.exe"
BASE_DIR = r"C:\kyiv_alert\alert_monitor"
AUDIO_DIR = r"C:\kyiv_alert\silence_moment"

os.makedirs(BASE_DIR, exist_ok=True)

SCRIPTS = {
    "monitor": os.path.join(BASE_DIR, "monitor.py"),
    "player": os.path.join(BASE_DIR, "player_service.py"),
    "scheduler": os.path.join(BASE_DIR, "moment_scheduler.py")
}

FLAGS = {
    "alarm": os.path.join(BASE_DIR, "alarm_active.flag"),
    "cancel": os.path.join(BASE_DIR, "cancel_active.flag"),
    "moment": os.path.join(BASE_DIR, "moment_active.flag")
}

active_resources = {name: {"proc": None, "file": None} for name in SCRIPTS}

def get_tail(name, lines_count=20):
    path = os.path.join(BASE_DIR, f"{name}.log")
    if not os.path.exists(path): return "📡 Очікування ініціалізації логів..."
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            return "".join(lines[-lines_count:])
    except Exception as e:
        return f"⚠️ Помилка доступу: {e}"

def stop_script(name):
    res = active_resources[name]
    if res["proc"] and res["proc"].poll() is None:
        try:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(res["proc"].pid)], 
                           capture_output=True, check=False)
            res["proc"].wait(timeout=1)
        except:
            if res["proc"]: res["proc"].kill()
    
    if res["file"]:
        try: res["file"].close()
        except: pass
    
    active_resources[name] = {"proc": None, "file": None}

def start_script(name):
    if name not in SCRIPTS or not os.path.exists(SCRIPTS[name]):
        print(f"❌ Помилка: Файл {SCRIPTS.get(name)} не знайдено!")
        return
    
    stop_script(name)
    log_path = os.path.join(BASE_DIR, f"{name}.log")
    log_file = open(log_path, "a", encoding="utf-8")
    
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.Popen(
        [PYTHON_EXE, "-u", SCRIPTS[name]],
        stdout=log_file,
        stderr=log_file,
        cwd=BASE_DIR,
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    active_resources[name] = {"proc": proc, "file": log_file}
    print(f"✅ Скрипт запущен: {name} (PID: {proc.pid})")

@atexit.register
def cleanup_on_exit():
    for name in SCRIPTS:
        stop_script(name)

def clear_all_flags():
    for path in FLAGS.values():
        if os.path.exists(path):
            try: os.remove(path)
            except: pass

# --- РОУТИНГ ---

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    # Декодуємо ім'я файлу (виправляє проблему з кирилицею та пробілами)
    decoded_name = unquote(filename)
    print(f"🔊 Запит аудіо: {decoded_name}")
    
    response = make_response(send_from_directory(AUDIO_DIR, decoded_name))
    
    # Допомагаємо браузеру зрозуміти, що це аудіо-потік
    if decoded_name.endswith('.wav'):
        response.headers['Content-Type'] = 'audio/wav'
    elif decoded_name.endswith('.mp3'):
        response.headers['Content-Type'] = 'audio/mpeg'
        
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    states = {n: ("RUNNING" if r["proc"] and r["proc"].poll() is None else "STOPPED") 
              for n, r in active_resources.items()}
    
    is_alarm = os.path.exists(FLAGS["alarm"])
    is_moment = os.path.exists(FLAGS["moment"])
    
    status_text = "⚪ ЧИСТО"
    if is_moment: status_text = "🕯️ ХВИЛИНА МОВЧАННЯ"
    elif is_alarm: status_text = "🚨 ПОВІТРЯНА ТРИВОГА"
    
    return jsonify({
        "status_text": status_text,
        "is_alarm": is_alarm,
        "is_moment": is_moment,
        "scripts": states,
        "logs": {name: get_tail(name) for name in SCRIPTS},
        "server_time": datetime.now().strftime("%H:%M:%S")
    })

@app.route('/toggle/<name>')
def toggle_script(name):
    res = active_resources.get(name)
    if not res: return "Error", 400
    
    if res["proc"] and res["proc"].poll() is None:
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
    
    if key in FLAGS:
        # Пріоритетність: якщо тривога — видаляємо відбій, якщо відбій — видаляємо тривогу
        if key == "alarm": 
            if os.path.exists(FLAGS["cancel"]): os.remove(FLAGS["cancel"])
        if key == "cancel": 
            if os.path.exists(FLAGS["alarm"]): os.remove(FLAGS["alarm"])
            if os.path.exists(FLAGS["moment"]): os.remove(FLAGS["moment"])

        with open(FLAGS[key], "w", encoding="utf-8") as f:
            f.write(f"manual_{datetime.now().isoformat()}")
            
    return jsonify({"status": "ok"})

@app.route('/clear_logs')
def clear_logs():
    for name in SCRIPTS:
        was_running = active_resources[name]["proc"] is not None
        stop_script(name)
        log_path = os.path.join(BASE_DIR, f"{name}.log")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"--- Log Reset {datetime.now()} ---\n")
        except: pass
        if was_running: start_script(name)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    clear_all_flags()
    # Автозапуск фонових процесів
    for name in SCRIPTS: 
        start_script(name)
    
    # host='0.0.0.0' дозволяє доступ з будь-якого пристрою в мережі
    app.run(host='0.0.0.0', port=5000, debug=False)