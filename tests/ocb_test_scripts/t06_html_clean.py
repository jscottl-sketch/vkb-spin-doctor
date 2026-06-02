with open("mission_control.html", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 50:
            break
        print(line, end="")
print("HTML sample read OK")
