with open(r"C:\Users\Connor Nesbit\.convokit\saved-corpora\downloads\downloaded.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

for i, line in enumerate(lines, 1):
    parts = line.strip().split("$#$")
    if len(parts) != 3:
        print(f"Malformed line {i}: {repr(line)} and {len(parts)}")