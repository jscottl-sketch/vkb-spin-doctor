import pathlib

# Step 1: read INDEX.md line count
index_path = pathlib.Path("INDEX.md")
if index_path.exists():
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    first_line = lines[0] if lines else ""
else:
    lines = ["INDEX.md not found"]
    first_line = lines[0]
print(f"Step 1: INDEX.md has {len(lines)} lines")

# Step 2: uppercase first line
upper_first = first_line.upper()
print(f"Step 2: {upper_first}")

# Step 3: write only to temp_output.txt
out_path = pathlib.Path("tests/ocb_test_scripts/temp_output.txt")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(upper_first, encoding="utf-8")
print(f"Step 3: Written to {out_path}")

print("All 3 steps done")
