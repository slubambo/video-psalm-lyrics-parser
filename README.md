# 🎵 Video Psalm Lyrics JSON to Text Converter

This tool helps convert messy or non-standard JSON exports (e.g., from **Video Psalm**) into clean, readable `.txt` files — each song well-formatted, separated, and labeled with title and metadata. Ideal for worship leaders, church tech teams, or anyone working with digital song archives.

---

## 📁 Sample Files Included

- `Songs.json` – A raw JSON file exported from Video Psalm (non-standard format)
- `Songs.txt` – The clean, human-readable text file generated from the tool
- `FixedSongs.json` – An intermediate fixed version of the JSON, cleaned for parsing

---

## 💻 How It Works

The script:
1. Fixes unquoted keys (`Text:` → `"Text":`)
2. Escapes bad characters (like newlines, tabs, and quotes inside lyrics)
3. Adds missing commas between objects (`}{` → `},{`)
4. Parses the cleaned JSON
5. Outputs a `.txt` file where each song is:
   - Numbered
   - Titled
   - Includes author/theme info (if available)
   - Lists all verses in order

---

## 🚀 Usage

### Requirements
- Python 3.7+
- No external libraries needed

### Steps
1. Clone this repo:
    ```bash
    git clone https://github.com/your-username/video-psalm-lyrics-parser.git
    cd video-psalm-lyrics-parser
    ```

2. Place your raw `Songs.json` file in the project root.

3. Run the script:
    ```bash
    python convert.py
    ```

4. Find your output in:
    - `Songs.txt` (readable format)
    - `FixedSongs.json` (debug-friendly fixed version)

---

## ⚠️ Challenges Addressed

- ✅ **Malformed JSON**: Handles missing quotes, broken objects, unescaped characters
- ✅ **Line Breaks**: Replaces raw line breaks/tabs with safe escaped versions
- ✅ **Verse Formatting**: Cleans up verses and maintains song structure
- ✅ **Missing Commas**: Smart detection and fixing of syntax like `}{` or `][`
- ✅ **Quoting Issues**: Escapes rogue `"` in lyrics without breaking strings

---

## 📚 For Contributors

If you're working on enhancing this tool:
- Consider adding a GUI version
- Allow exporting to `.docx` or `.pdf`
- Add support for other lyric export formats

---

## 🙏 Acknowledgments

This was created to help church worship teams preserve and organize their digital song collections, especially those exported from tools like Video Psalm.

---

## 📃 License

MIT License. Use it freely.
