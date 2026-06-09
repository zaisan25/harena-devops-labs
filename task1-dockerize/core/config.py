import os
from dotenv import load_dotenv


load_dotenv()


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
try:
	REFRESH_RATE = int(os.getenv("REFRESH_RATE", "5"))
except ValueError:
	REFRESH_RATE = 5
