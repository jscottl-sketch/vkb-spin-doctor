import subprocess

result = subprocess.run(["git", "stash", "list"], capture_output=True, text=True)
output = result.stdout.strip()
print(output if output else "(no stash entries)")
