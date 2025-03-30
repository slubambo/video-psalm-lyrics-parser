# To run this script, first install demjson3 if you haven't:
# pip install demjson3

import re
import demjson3
import json

# Filenames
json_file = "Songbook.json"
fixed_json_file = "SongbookFixedSongs.json"
output_file = "Songbook.txt"

# Step 1: Read raw content
with open(json_file, "r", encoding="utf-8") as f:
    raw = f.read()

# Step 2: Escape only *real* newlines inside quotes (not double-escape)
def escape_linebreaks_in_quotes(text):
    result = []
    in_string = False
    buffer = ''
    for char in text:
        if char == '"':
            in_string = not in_string
        if in_string and char == '\n':
            buffer += '\\n'
        elif in_string and char == '\r':
            buffer += '\\r'
        else:
            buffer += char
    return buffer

raw = escape_linebreaks_in_quotes(raw)

# Step 3: Parse using demjson3
try:
    data = demjson3.decode(raw)
except Exception as e:
    print("❌ Failed to parse using demjson3.")
    print(f"Error: {e}")
    exit(1)

# Step 4: Save a fixed version
with open(fixed_json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Step 5: Convert to readable text
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

# Step 6: Write final text output
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"\n✅ Success! {len(songs)} songs written to '{output_file}'.")
