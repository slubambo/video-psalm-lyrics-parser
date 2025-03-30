# No external libraries needed

import re
import json

json_file = "Songbook.json"
fixed_json_file = "SongbookFixedSongs.json"
output_file = "Songbook.txt"

# Step 1: Read raw content
with open(json_file, "r", encoding="utf-8") as f:
    raw = f.read()

# Step 2: Fix unquoted keys and missing top-level quotes
# Add quotes to top-level "Songs"
if raw.startswith("{Songs:"):
    raw = raw.replace("{Songs:", '{"Songs":', 1)

# Fix all keys (even nested ones)
raw = re.sub(r'([{,])(\s*)([A-Za-z_][\w]*)(\s*):', r'\1\2"\3"\4:', raw)

# Escape line breaks inside quotes
def fix_multiline_strings(text):
    def replacer(match):
        content = match.group(0)
        return content.replace('\n', '\\n').replace('\r', '\\r')
    return re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', replacer, text)

raw = fix_multiline_strings(raw)

# Add missing commas between objects
raw = re.sub(r'\}\s*\{', '},{', raw)
raw = re.sub(r'\]\s*\[', '],[', raw)

# Optional: Save cleaned version
with open(fixed_json_file, "w", encoding="utf-8") as f:
    f.write(raw)

# Step 3: Try parsing using built-in json
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print("❌ Failed to parse even after all cleaning.")
    print(f"Error: {e}")
    exit(1)

# Step 4: Convert to readable text
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

# Step 5: Write final output
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"\n✅ Success! {len(songs)} songs written to '{output_file}'.")
