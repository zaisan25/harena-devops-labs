import logging
import json
import sys
import os
from datetime import datetime
from core.config import LOG_LEVEL


class CustomFilter(logging.Filter):
	def filter(self, record):
		if hasattr(record, 'extra_data') and record.extra_data:
			record.msg = record.msg + " | extras: " + json.dumps(record.extra_data)
		return True


class JSONFormatter(logging.Formatter):
	def format(self, record):
		log_entry = {
			"timestamp": datetime.utcnow().isoformat(),
			"level": record.levelname,
			"message": record.getMessage(),
			"module": record.module
		}
		if hasattr(record, 'extra_data') and record.extra_data:
			log_entry["extras"] = record.extra_data
		return json.dumps(log_entry)


logger = logging.getLogger("control_plane")
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)

log_path = "/app/logs/app.json.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)
file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

logger.addFilter(CustomFilter())


def struct_log(level, msg, **kwargs):
	extra = {"extra_data": kwargs} if kwargs else {}
	getattr(logger, level.lower())(msg, extra=extra)
