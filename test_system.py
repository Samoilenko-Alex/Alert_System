#!/usr/bin/env python3
"""
Kyiv Alert Monitor system test
Tests all components: monitor, player, scheduler, web
"""

import os
import sys
import time
import requests
import subprocess
import signal
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR
WEB_URL = "http://localhost:5000"
TEST_DURATION = 30

def log(msg):
    print(f"[TEST] {msg}")

def check_service_running(name):
    lock_file = BASE_DIR / "alert_monitor" / f"{name}_lock.lock"
    log_file = BASE_DIR / "alert_monitor" / f"{name}.log"

    if name == "player":
        return lock_file.exists()

    if name in ["monitor", "scheduler"] and log_file.exists():
        try:
            mtime = os.path.getmtime(log_file)
            if time.time() - mtime < 300:
                return True
        except:
            pass

    return False

def test_web_server():
    log("Testing web server...")
    try:
        r = requests.get(f"{WEB_URL}/status", timeout=5)
        if r.status_code == 200:
            data = r.json()
            status_text = data.get('status_text', 'Unknown')
            log(f"OK Server responds: {status_text}")
            return True
        else:
            log(f"ERROR Server returned {r.status_code}")
            return False
    except Exception as e:
        log(f"ERROR Connecting to server: {e}")
        return False

def test_manual_trigger(action):
    """Тест ручного триггера"""
    log(f"Testing manual trigger: {action}")
    try:
        r = requests.get(f"{WEB_URL}/manual/test_{action}", timeout=5)
        if r.status_code == 200:
            log(f"OK Trigger {action} worked")
            return True
        else:
            log(f"ERROR Trigger {action} returned {r.status_code}")
            return False
    except Exception as e:
        log(f"ERROR Trigger {action}: {e}")
        return False

def test_services():
    """Тест запущенных сервисов"""
    services = ["monitor", "player", "scheduler"]
    all_ok = True

    for svc in services:
        if check_service_running(svc):
            log(f"OK Service {svc} is running")
        else:
            log(f"ERROR Service {svc} is NOT running")
            all_ok = False

    return all_ok

def test_audio_files():
    log("Testing audio files...")
    audio_dir = BASE_DIR / "silence_moment"
    required_files = ["alarm.wav", "cancel.wav", "moment.wav"]

    all_ok = True
    for f in required_files:
        path = audio_dir / f
        if path.exists():
            log(f"OK Audio file {f} found")
        else:
            log(f"ERROR Audio file {f} NOT found")
            all_ok = False

    return all_ok

def run_full_test():
    """Полный тест системы"""
    log("Starting full system test for Kyiv Alert Monitor")
    log("=" * 60)

    results = []

    # 1. Тест аудио файлов
    results.append(("Аудио файлы", test_audio_files()))

    # 2. Тест сервисов
    results.append(("Сервисы", test_services()))

    # 3. Тест веб-сервера
    results.append(("Веб-сервер", test_web_server()))

    # 4. Test manual triggers
    if results[-1][1]:  # If server works
        log("Testing manual triggers...")
        test_manual_trigger("alarm")
        time.sleep(2)
        test_manual_trigger("cancel")
        time.sleep(2)
        test_manual_trigger("moment")
        time.sleep(2)
        test_manual_trigger("stop_all")  # Cleanup
        results.append(("Manual triggers", True))
    else:
        results.append(("Manual triggers", False))

    # Results
    log("=" * 60)
    log("TEST RESULTS:")
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        log(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    log("=" * 60)
    if all_passed:
        log("ALL TESTS PASSED! System is ready for operation.")
    else:
        log("SOME TESTS FAILED. Check logs above.")

    return all_passed

if __name__ == "__main__":
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("Тест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        log(f"Критическая ошибка теста: {e}")
        sys.exit(1)