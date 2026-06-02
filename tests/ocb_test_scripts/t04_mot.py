import subprocess
import sys

result = subprocess.run(
    [sys.executable, "mcc_full_mot.py"],
    capture_output=True, text=True, timeout=180,
)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
