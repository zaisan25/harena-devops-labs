import os
import time


_last_readiness_check = 0
_readiness_cache = True


def readiness():
	global _last_readiness_check, _readiness_cache
	now = time.time()
	if now - _last_readiness_check < 2:
		return _readiness_cache

	try:
		test_path = "/app/logs/readiness.test"
		with open(test_path, "w") as f:
			f.write("ok")
		_readiness_cache = os.path.exists(test_path)
		_last_readiness_check = now
		return _readiness_cache
	except:
		_readiness_cache = False
		_last_readiness_check = now
		return False


def liveness():
	try:
		import streamlit
		return True
	except:
		return False
