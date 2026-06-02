with open("aafl_core.py", "r", encoding="utf-8") as f:
    first_line = f.readline().rstrip()
print(f"# TEST COMMENT READ: {first_line}")
