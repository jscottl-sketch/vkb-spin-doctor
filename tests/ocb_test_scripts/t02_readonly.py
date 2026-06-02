with open("STATUS.md", "r", encoding="utf-8") as f:
    n = sum(1 for _ in f)
print(f"Lines: {n}")
