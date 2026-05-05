"""
Flag manager for Kyiv Alert system.
Provides centralized flag management with priorities and safe file operations.
"""

import os
import logging
from pathlib import Path
from datetime import datetime

class FlagManager:
    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent

        self.base_dir = Path(base_dir)
        self.flags = {
            "alarm":  self.base_dir / "alarm_active.flag",
            "cancel": self.base_dir / "cancel_active.flag",
            "moment": self.base_dir / "moment_active.flag",
        }
        self.logger = logging.getLogger("FlagManager")

    def _safe_write(self, flag_path: Path, content: str = "") -> bool:
        temp_path = None
        try:
            temp_path = flag_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content or datetime.now().isoformat())

            os.replace(str(temp_path), str(flag_path))
            return True
        except Exception as e:
            self.logger.error(f"Flag write error {flag_path.name}: {e}")
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            return False

    def set_flag(self, name: str, content: str = "") -> bool:
        """
        Set flag with priorities: cancel > alarm > moment
        """
        if name not in self.flags:
            self.logger.error(f"Невідомий флаг: {name}")
            return False

        # Пріоритетна логіка
        if name == "alarm":
            self.clear_flag("cancel")           # Відбій не може бути разом з тривогою
        elif name == "cancel":
            self.clear_flag("alarm")
            self.clear_flag("moment")           # Відбій скидає все
        elif name == "moment":
            if self.is_set("alarm"):
                self.logger.info("🚨 Активна тривога — хвилина мовчання не створюється")
                return False

        success = self._safe_write(self.flags[name], content)

        if success:
            self.logger.info(f"✅ Флаг встановлено: {name.upper()}")
        else:
            self.logger.warning(f"❌ Не вдалося встановити флаг: {name}")

        return success

    def clear_flag(self, name: str) -> bool:
        """Видаляє флаг."""
        if name not in self.flags:
            return False

        try:
            if self.flags[name].exists():
                self.flags[name].unlink()
                self.logger.debug(f"🗑️ Флаг видалено: {name}")
            return True
        except Exception as e:
            self.logger.debug(f"Не вдалося видалити флаг {name}: {e}")
            return False

    def is_set(self, name: str) -> bool:
        """Перевіряє, чи встановлений флаг."""
        if name not in self.flags:
            return False
        return self.flags[name].exists()

    def clear_all(self) -> None:
        """Очищає всі флаги."""
        for name in list(self.flags.keys()):
            self.clear_flag(name)
        self.logger.info("🧹 Всі флаги очищено")

    def get_status(self) -> dict:
        """Повертає статус усіх флагів (для веб-дашборду)."""
        return {
            "alarm":  self.is_set("alarm"),
            "cancel": self.is_set("cancel"),
            "moment": self.is_set("moment"),
        }


# Глобальна інстанція (імпортується в інших модулях)
flag_manager = FlagManager()