import psutil


def get_cpu(interval=0.1):
	return psutil.cpu_percent(interval=interval)


def get_ram():
	return psutil.virtual_memory().percent


def get_disk():
	return psutil.disk_usage('/').percent
