import re
import json

# Filenames
json_file = "Songs.json"
fixed_json_file = "FixedSongs.json"
output_file = "Songs.txt"

# Step 1: Read raw content
with open(json_file, "r", encoding="utf-8") as f:
    raw = f.read().strip()

# Step 2: Wrap root key with quotes if needed (e.g. Songs:[...] → {"Songs":[...]})
if raw.startswith("{") and not raw.startswith('{"'):
    raw = re.sub(r'^{(\s*\w+\s*):', r'{"\1":', raw, 1)

# Step 3: Fix unquoted keys inside the JSON
raw = re.sub(r'([{,])\s*(\w+)\s*:', r'\1"\2":', raw)

# Step 4: Escape control characters and bad quotes
raw = raw.replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')

# Escape quotes inside strings
def escape_inner_quotes(match):
    content = match.group(0)
    # Don't touch the outer quotes, just escape internal ones
    return '"' + content[1:-1].replace('"', '\\"') + '"'

raw = re.sub(r'"[^"]*"', escape_inner_quotes, raw)

# Step 5: Add missing commas between objects
raw = re.sub(r'\}\s*\{', '},{', raw)
raw = re.sub(r'\]\s*\[', '],[', raw)

# Step 6: Save fixed content for debugging
with open(fixed_json_file, "w", encoding="utf-8") as f:
    f.write(raw)

# Step 7: Try parsing JSON
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print("❌ Still failed to decode JSON after cleaning.")
    print(f"Error: {e}")
    print(f"Check '{fixed_json_file}' to manually inspect.")
    exit(1)

# Step 8: Process songs
songs = data.get("Songs", [])
output_lines = []

for idx, song in enumerate(songs, 1):
    title = song.get("Text", "Untitled Song")
    author = song.get("Author", "Unknown Author")
    copyright_info = song.get("Copyright", "")
    theme = song.get("Theme", "")
    sequence = song.get("Sequence", "")

    output_lines.append("=" * 60)
    output_lines.append(f"{idx}. {title}")
    if author or copyright_info or theme or sequence:
        output_lines.append(f"   Author: {author}")
        if copyright_info:
            output_lines.append(f"   Copyright: {copyright_info}")
        if theme:
            output_lines.append(f"   Theme: {theme}")
        if sequence:
            output_lines.append(f"   Sequence: {sequence}")
    output_lines.append("")

    for verse in song.get("Verses", []):
        text = verse.get("Text", "").strip().replace('\\n', '\n')
        if text:
            output_lines.append(text)
            output_lines.append("")

# Step 9: Write output
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"\n✅ Success! {len(songs)} songs written to '{output_file}'.")
