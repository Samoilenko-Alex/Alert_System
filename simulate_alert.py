#!/usr/bin/env python3
"""
Скрипт для имитации тревоги через флаги
Использование: python simulate_alert.py <alarm|cancel|moment|clear>
"""

import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent / "alert_monitor"

FLAGS = {
    "alarm": BASE_DIR / "alarm_active.flag",
    "cancel": BASE_DIR / "cancel_active.flag",
    "moment": BASE_DIR / "moment_active.flag"
}

def set_flag(flag_type, message="simulation"):
    """Установить флаг"""
    if flag_type not in FLAGS:
        print(f"Error: Unknown flag type '{flag_type}'. Use: alarm, cancel, moment, clear")
        return False

    if flag_type == "clear":
        # Очистить все флаги
        for path in FLAGS.values():
            if path.exists():
                try:
                    os.remove(path)
                    print(f"Cleared {path.name}")
                except Exception as e:
                    print(f"Error clearing {path.name}: {e}")
        return True

    # Установить флаг
    flag_path = FLAGS[flag_type]

    # Для alarm - очистить cancel, для cancel - очистить alarm и moment
    if flag_type == "alarm" and FLAGS["cancel"].exists():
        try:
            os.remove(FLAGS["cancel"])
            print("Cleared cancel flag (alarm priority)")
        except:
            pass
    elif flag_type == "cancel":
        for f in ["alarm", "moment"]:
            if FLAGS[f].exists():
                try:
                    os.remove(FLAGS[f])
                    print(f"Cleared {f} flag (cancel priority)")
                except:
                    pass

    # Создать флаг
    try:
        with open(flag_path, "w", encoding="utf-8") as f:
            f.write(f"{message}_{time.time()}")
        print(f"Set {flag_type} flag: {flag_path}")
        return True
    except Exception as e:
        print(f"Error setting {flag_type} flag: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python simulate_alert.py <alarm|cancel|moment|clear>")
        print("Examples:")
        print("  python simulate_alert.py alarm    # Simulate air raid alarm")
        print("  python simulate_alert.py cancel   # Simulate alarm cancellation")
        print("  python simulate_alert.py moment   # Simulate minute of silence")
        print("  python simulate_alert.py clear    # Clear all flags")
        sys.exit(1)

    action = sys.argv[1].lower()
    success = set_flag(action)

    if success:
        print(f"Simulation {action} completed successfully")
        sys.exit(0)
    else:
        print(f"Simulation {action} failed")
        sys.exit(1)

if __name__ == "__main__":
    main()