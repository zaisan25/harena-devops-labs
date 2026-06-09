import subprocess
import shlex


def run_cmd(cmd, timeout=5):
	try:
		result = subprocess.run(
			shlex.split(cmd),
			capture_output=True,
			text=True,
			timeout=timeout
		)
		return result.stdout.strip(), result.stderr.strip(), result.returncode
	except subprocess.TimeoutExpired:
		return "", "Command timed out", 124
