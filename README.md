# 🚨 Kyiv Alert Monitor System

**Automated air raid alert monitoring system for Kyiv** with siren playback, all-clear signal, and minute of silence.

The system is designed for use on computers, speakers, and audio systems in public places, offices, bomb shelters, and other facilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Key Features

- Real-time monitoring of air raid alerts via official `ukrainealarm.com` API
- Siren plays **once** at alert start (not looped)
- Automatic minute of silence daily at **09:00** precisely
- All-clear signal when alert ends
- Convenient web control panel (accessible from any device on the network)
- Support for simultaneous operation on multiple PCs
- Alert history and detailed logging
- Testing and simulation tools

---

## Project Structure
```
kyiv_alert/
├── alert_monitor/
│   ├── monitor.py                  # UkraineAlarm API monitoring
│   ├── player_service.py           # Audio player (main sound service)
│   ├── moment_scheduler.py         # Minute of silence scheduler
│   ├── web_app.py                  # Flask web server + management
│   ├── alerts_history.json         # Alert history
│   └── *.log                       # Logs
├── silence_moment/
│   ├── alarm.wav
│   ├── cancel.wav
│   └── moment.wav
├── templates/
│   └── index.html                  # Web control panel
├── simulate_alert.py               # Alert simulator
├── start_all.bat                   # Auto-start entire system
├── test_system.py                  # Full system test
├── requirements.txt
└── README.md
```

---

## Event Priorities

**Highest priority — Air raid alert** (human life is most valuable).

1. **Air raid alert** (highest priority)  
   Flag file: `alarm_active.flag`  
   Sound: `alarm.wav` (plays **once**)

2. **All-clear signal**  
   Flag file: `cancel_active.flag`  
   Sound: `cancel.wav` (one-time signal)

3. **Minute of silence** (lower priority)  
   Flag file: `moment_active.flag`  
   Sound: `moment.wav` (plays once)

**Operating rules:**
- Alert can interrupt minute of silence
- New siren starts only after all-clear of previous alert
- All-clear has priority over minute of silence

---

## Installation & Setup

### 1. Environment Setup
```bash
cd C:\kyiv_alert
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. System Launch
Recommended method (simplest):
```bash
start_all.bat
```
(Run as administrator)

Or manually in separate PowerShell windows:
```bash
python alert_monitor\player_service.py
python alert_monitor\monitor.py
python alert_monitor\moment_scheduler.py
python web_app.py
```

After launch, open in browser:
http://localhost:5000

---

## Development

### Prerequisites
- Python 3.8 or higher
- Git
- Windows PowerShell

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kyiv-alert.git
cd kyiv-alert
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### Code Quality

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Pre-commit** for automated checks

Run code quality checks:
```bash
pre-commit run --all-files
```

### Testing

Run the test suite:
```bash
python test_system.py
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## CI/CD

This project uses GitHub Actions for continuous integration:

- **Automated Testing**: Runs on every push and PR
- **Code Quality**: Flake8 linting and Black formatting checks
- **Multi-platform**: Tests on Windows (primary), Linux, and macOS

[![CI](https://github.com/yourusername/kyiv-alert/workflows/CI/badge.svg)](https://github.com/yourusername/kyiv-alert/actions)

### Control
Via web panel:
- Enable/disable scripts (Monitor, Player, Scheduler)
- Run tests (alert, all-clear, minute of silence)
- Emergency stop
- Real-time log viewing

Via command line:
```bash
python simulate_alert.py alarm      # Simulate alert
python simulate_alert.py cancel     # Simulate all-clear
python simulate_alert.py moment     # Simulate minute of silence
python simulate_alert.py clear      # Clear all flags
```

### Testing
```bash
python test_system.py               # Full system test
```

---

## Important Technical Notes

- System operates via flag file mechanism
- `player_service.py` protected against double launch (`player_lock.lock`)
- Recommended to disable computer sleep mode
- For stable operation, run scripts as administrator

## Log Files

- `alert_monitor/player.log` — audio player
- `alert_monitor/monitor.log` — API monitoring
- `alert_monitor/scheduler.log` — scheduler
- `alert_monitor/web_app.log` — web server

---

## Project Status
MVP version ready for use.
Future plans: priority changes, flexible settings, and functionality expansion.

**Author:** Oleksandr Samoilenko  
**Version:** 2.0 (2026)  
**Goal:** Reliable notification of Kyiv population about air threats and minute of silence

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

2. **Відбій тривоги**  
   Файл-флаг: `cancel_active.flag`  
   Звук: `cancel.wav` (одноразовий сигнал)

3. **Хвилина мовчання** (нижчий пріоритет)  
   Файл-флаг: `moment_active.flag`  
   Звук: `moment.wav` (відтворюється один раз)

**Правила роботи:**
- Тривога може перервати хвилину мовчання.
- Нова сирена запускається тільки після отримання відбою попередньої тривоги.
- Відбій має пріоритет над хвилиною мовчання.

---

## Встановлення та запуск

### 1. Підготовка середовища
```powershell
cd C:\kyiv_alert
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
2. Запуск системи
Рекомендований спосіб (найпростіший):
PowerShell.\start_all.bat
(Запускати від імені адміністратора)
Або вручну в окремих вікнах PowerShell:
PowerShell.\venv\Scripts\python.exe .\alert_monitor\player_service.py
.\venv\Scripts\python.exe .\alert_monitor\monitor.py
.\venv\Scripts\python.exe .\alert_monitor\moment_scheduler.py
.\venv\Scripts\python.exe .\web_app.py
Після запуску відкрийте в браузері:
http://localhost:5000

Керування
Через веб-панель

Вмикання / вимикання скриптів (Monitor, Player, Scheduler)
Запуск тестів (тривога, відбій, хвилина мовчання)
Аварійна зупинка (Emergency Stop)
Перегляд логів у реальному часі

Через командний рядок
PowerShellpython simulate_alert.py alarm      # Імітувати тривогу
python simulate_alert.py cancel     # Імітувати відбій
python simulate_alert.py moment     # Імітувати хвилину мовчання
python simulate_alert.py clear      # Очистити всі флаги

Тестування
PowerShellpython test_system.py               # Повний тест системи

Важливі технічні моменти

Система працює через механізм файлів-флагів
player_service.py захищений від подвійного запуску (player_lock.lock)
Рекомендується вимкнути сплячий режим комп’ютера
Для стабільної роботи запускати скрипти від імені адміністратора


Файли логів

alert_monitor/player.log — аудіоплеєр
alert_monitor/monitor.log — моніторинг API
alert_monitor/scheduler.log — планувальник
alert_monitor/web_app.log — веб-сервер


Статус проекту
MVP версія готова до використання.
У подальшому планується зміна пріоритезації, гнучкі налаштування та розширення функціоналу.

Автор: Oleksandr Samoilenko
Версія: 0.2 MVP (2026)
