import logging
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler
import sys

# Color codes
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[31;1m',  # Bright red
    'RESET': '\033[0m',      # Reset
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt = None, datefmt = None, style = "%", validate = True, *, defaults = None):
        self.fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.datefmt = '%Y-%m-%d %H:%M:%S'
        super().__init__(self.fmt, self.datefmt, style, validate, defaults=defaults)
    
    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        return f"{COLORS.get(levelname, '')}{message}{COLORS['RESET']}"


class AppLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name="app", log_level=logging.INFO, log_file="app.log", max_bytes=5*1024*1024, backup_count=5):
        if not hasattr(self, 'logger'):  # Prevent re-initialization
            self.logger = logging.getLogger(name)
            self.logger.setLevel(log_level)

            # Clear existing handlers
            self.logger.handlers.clear()

            # Formatters
            self.standard_formatter = ColoredFormatter()

            # Handlers
            self._setup_console_handler()
            self._setup_file_handler(log_file, max_bytes, backup_count)

    def _setup_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.standard_formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self, log_file, max_bytes, backup_count):
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
    
    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        return f"{COLORS.get(levelname, '')}{message}{COLORS['RESET']}"
            

# Singleton logger instance
logger = AppLogger().get_logger()
