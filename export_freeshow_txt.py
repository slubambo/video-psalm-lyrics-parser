#!/usr/bin/env python3
"""Export the available song libraries into FreeShow-friendly text files."""

from __future__ import annotations

import csv
import html
import json
import re
import shutil
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_PRIORITY = ["EasyWorship.json", "Songs.json", "Songbook.json"]
OUTPUT_DIR = Path("FreeShowSongs")
MARKER_FILE = ".generated_by_export_freeshow_txt"

GENERIC_TITLES = {
    "",
    "n",
    "ne",
    "new song",
    "song",
    "theme",
    "themes",
    "untitled",
    "untitled song",
}

CHORD_TOKEN_RE = re.compile(
    r"\[(?:"
    r"N\.?C\.?"
    r"|[A-G](?:#|b)?(?:m|maj|min|dim|aug|sus|add)?\d*(?:/[A-G](?:#|b)?)?"
    r")\]"
)
FONT_TAG_RE = re.compile(r"</?f[^>]*>", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
FILENAME_UNSAFE_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class ExportSong:
    title: str
    original_title: str
    lyric_blocks: list[str]
    source: str
    source_index: int
    author: str
    composer: str
    copyright: str
    key: str
    guid: str
    review_flags: list[str]


def quote_keys_outside_strings(text: str) -> str:
    """Quote JavaScript-style bare keys without touching lyric strings."""
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False

    while i < len(text):
        char = text[i]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue

        if char in "{,":
            out.append(char)
            i += 1
            start = i

            while start < len(text) and text[start].isspace():
                out.append(text[start])
                start += 1

            end = start
            if end < len(text) and (text[end].isalpha() or text[end] == "_"):
                end += 1
                while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                    end += 1

                colon = end
                while colon < len(text) and text[colon].isspace():
                    colon += 1

                if colon < len(text) and text[colon] == ":":
                    out.append(f'"{text[start:end]}"')
                    i = end
                    continue

            i = start
            continue

        out.append(char)
        i += 1

    return "".join(out)


def escape_controls_inside_strings(text: str) -> str:
    """Make raw multiline/control-character strings valid JSON strings."""
    out: list[str] = []
    in_string = False
    escaped = False

    for char in text:
        if in_string:
            if escaped:
                out.append(char)
                escaped = False
                continue
            if char == "\\":
                out.append(char)
                escaped = True
                continue
            if char == '"':
                out.append(char)
                in_string = False
                continue

            if char == "\n":
                out.append(r"\n")
            elif char == "\r":
                out.append(r"\r")
            elif char == "\t":
                out.append(r"\t")
            elif ord(char) < 32:
                out.append(f"\\u{ord(char):04x}")
            else:
                out.append(char)
        else:
            out.append(char)
            if char == '"':
                in_string = True

    return "".join(out)


def parse_videopsalm_export(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8-sig")
    raw = quote_keys_outside_strings(raw)
    raw = escape_controls_inside_strings(raw)
    raw = re.sub(r"}\s*{", "},{", raw)
    raw = re.sub(r"]\s*\[", "],[", raw)
    return json.loads(raw)


def normalize_line(line: str) -> str:
    line = CHORD_TOKEN_RE.sub("", line)
    line = line.replace("|", " ")
    line = WHITESPACE_RE.sub(" ", line)
    return line.strip()


def clean_lyric_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\x0b", "\n").replace("\f", "\n")
    text = FONT_TAG_RE.sub("", text)
    text = HTML_TAG_RE.sub("", text)
    text = html.unescape(text)

    lines = [normalize_line(line) for line in text.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        if line:
            cleaned.append(line)
            previous_blank = False
        elif not previous_blank:
            cleaned.append("")
            previous_blank = True

    return "\n".join(cleaned).strip()


def clean_title(value: Any) -> str:
    return WHITESPACE_RE.sub(" ", clean_lyric_text(value)).strip()


def title_is_generic(title: str) -> bool:
    normalized = title.casefold().strip()
    return normalized in GENERIC_TITLES or len(normalized) <= 2


def first_usable_lyric_line(blocks: list[str]) -> str:
    for block in blocks:
        for line in block.splitlines():
            line = clean_title(line)
            if 3 <= len(line) <= 90:
                return line
    return ""


def choose_title(song: dict[str, Any], blocks: list[str]) -> tuple[str, str]:
    original = clean_title(song.get("Text"))
    if not title_is_generic(original):
        return original, original

    for field in ("Alias", "Theme", "Reference", "Composer", "Author"):
        candidate = clean_title(song.get(field))
        if candidate and not title_is_generic(candidate):
            return candidate[:90].rstrip(), original

    first_line = first_usable_lyric_line(blocks)
    if first_line:
        return first_line[:90].rstrip(), original

    return original or "Untitled Song", original


def review_flags_for(title: str, blocks: list[str]) -> list[str]:
    haystack = f"{title}\n{' '.join(blocks)}".casefold()
    flags: list[str] = []

    if title.casefold() in {"announcement", "theme", "themes", "mobile line", "missing child"}:
        flags.append("non_song_title")
    if re.search(r"\b(today's theme|merchant code|marchant code|missing child)\b", haystack):
        flags.append("non_song_content")
    if re.search(r"\b0[237]\d{8}\b", haystack):
        flags.append("phone_number")
    if "*165*3#" in haystack or "mobile money" in haystack or "momo" in haystack:
        flags.append("money_notice")

    return flags


def normalized_key(text: str) -> str:
    return re.sub(r"\W+", "", text.casefold())


def dedupe_key(title: str, blocks: list[str]) -> tuple[str, ...]:
    lyrics_key = normalized_key("\n".join(blocks))
    if len(lyrics_key) >= 80:
        return ("lyrics", lyrics_key)
    return ("title_lyrics", normalized_key(title), lyrics_key)


def safe_filename_base(title: str) -> str:
    base = FILENAME_UNSAFE_RE.sub(" - ", title)
    base = WHITESPACE_RE.sub(" ", base).strip(" .")
    return (base or "Untitled Song")[:140].rstrip(" .")


def filename_key(filename: str) -> str:
    return unicodedata.normalize("NFC", filename).casefold()


def unique_filename(title: str, used_names: Counter[str]) -> str:
    base = safe_filename_base(title)
    suffix_number = 1

    while True:
        if suffix_number == 1:
            filename = f"{base}.txt"
        else:
            suffix = f" ({suffix_number})"
            trimmed = base[: 140 - len(suffix)].rstrip(" .")
            filename = f"{trimmed}{suffix}.txt"

        key = filename_key(filename)
        if not used_names[key]:
            used_names[key] += 1
            return filename

        suffix_number += 1


def build_song(song: dict[str, Any], source: str, source_index: int) -> ExportSong | None:
    blocks = [clean_lyric_text(verse.get("Text")) for verse in song.get("Verses", [])]
    blocks = [block for block in blocks if block]
    if not blocks:
        return None

    title, original_title = choose_title(song, blocks)
    if not title:
        return None

    return ExportSong(
        title=title,
        original_title=original_title,
        lyric_blocks=blocks,
        source=source,
        source_index=source_index,
        author=clean_title(song.get("Author")),
        composer=clean_title(song.get("Composer")),
        copyright=clean_title(song.get("Copyright")),
        key=clean_title(song.get("Key")),
        guid=clean_title(song.get("Guid")),
        review_flags=review_flags_for(title, blocks),
    )


def prepare_output_dir() -> None:
    if OUTPUT_DIR.exists():
        marker = OUTPUT_DIR / MARKER_FILE
        if not marker.exists():
            raise SystemExit(
                f"{OUTPUT_DIR} already exists and was not generated by this script. "
                "Move it aside before exporting."
            )
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir()
    (OUTPUT_DIR / MARKER_FILE).write_text(
        "Generated by export_freeshow_txt.py. Re-running the script recreates this folder.\n",
        encoding="utf-8",
    )


def write_song_file(path: Path, song: ExportSong) -> None:
    body = "\n\n".join(song.lyric_blocks)
    path.write_text(f"{song.title}\n\n{body}".rstrip() + "\n", encoding="utf-8")


def write_readme(rows: list[dict[str, str]], stats: Counter[str]) -> None:
    flagged = sum(1 for row in rows if row["review_flags"])
    readme = f"""# FreeShow Song Lyrics Folder

This folder contains one UTF-8 `.txt` file per song. It is designed for church media teams, worship leaders, and anyone who needs a searchable lyrics folder or a simple import source for FreeShow.

Each file is named after the song title and starts with the title on the first line.

Example:

```text
Song Title

Verse or slide block 1

Verse or slide block 2
```

## How To Use This Folder

- Search this folder by song title when you need lyrics quickly.
- Open any `.txt` file to copy lyrics into FreeShow, another presentation app, a document, or a service plan.
- Use `index.csv` to audit all songs in a spreadsheet.
- Review files with duplicate title suffixes such as `(2)` because they may be different versions of the same song.

## Importing Into FreeShow

FreeShow versions may label import menus differently. These generated files use a simple layout:

1. The first line is the song title.
2. A blank line follows the title.
3. Original verse or slide blocks are separated by blank lines.

In FreeShow:

1. Open the Songs or Library area.
2. Choose the import option.
3. Select text/plain-text import if FreeShow asks for a format.
4. Choose one or more files from this folder, or select the whole folder if your FreeShow version supports folder import.
5. Check a few imported songs to confirm titles and verse breaks imported correctly.

If a song imports as one long block, open that `.txt` file and adjust the blank lines before importing again.

## Source Choice

The exporter builds this folder from the best available local sources:

- `EasyWorship.json` is used first because it contains the largest usable song set.
- `Songs.json` and `Songbook.json` are then used only for unique songs not already exported.
- Clear chord tokens such as `[D/F#]` and old VideoPsalm font tags are removed so the files are cleaner for screen lyrics.

## Review Before Live Use

Some exports contain non-song items such as announcements, themes, phone-number notices, or giving information. Those entries are not deleted automatically. They are kept and flagged in `index.csv`.

Before using the library in a service, review:

- Songs with `review_flags` in `index.csv`.
- Songs with duplicate titles.
- Songs whose original title was generic, such as `New song`.
- Copyright-sensitive songs that need reporting or licensing details.

## Export Summary

- Songs exported: {len(rows)}
- Songs added from `EasyWorship.json`: {stats['from_EasyWorship.json']}
- Songs added from `Songs.json`: {stats['from_Songs.json']}
- Songs added from `Songbook.json`: {stats['from_Songbook.json']}
- Empty entries skipped: {stats['skipped_empty']}
- Duplicate entries skipped: {stats['skipped_duplicates']}
- Generic titles improved from lyrics/metadata: {stats['improved_titles']}
- Entries flagged for manual review in `index.csv`: {flagged}

This folder was generated by `export_freeshow_txt.py`.
"""
    (OUTPUT_DIR / "README.md").write_text(readme, encoding="utf-8")


def export() -> None:
    prepare_output_dir()

    rows: list[dict[str, str]] = []
    used_files: Counter[str] = Counter()
    seen: set[tuple[str, ...]] = set()
    stats: Counter[str] = Counter()

    for source in SOURCE_PRIORITY:
        data = parse_videopsalm_export(Path(source))
        songs = data.get("Songs", [])

        for index, raw_song in enumerate(songs, 1):
            song = build_song(raw_song, source, index)
            if song is None:
                stats["skipped_empty"] += 1
                continue

            key = dedupe_key(song.title, song.lyric_blocks)
            if key in seen:
                stats["skipped_duplicates"] += 1
                continue
            seen.add(key)

            if song.original_title != song.title:
                stats["improved_titles"] += 1

            filename = unique_filename(song.title, used_files)
            write_song_file(OUTPUT_DIR / filename, song)
            stats[f"from_{source}"] += 1

            rows.append(
                {
                    "file_name": filename,
                    "title": song.title,
                    "original_title": song.original_title,
                    "source": song.source,
                    "source_index": str(song.source_index),
                    "verse_blocks": str(len(song.lyric_blocks)),
                    "lyric_lines": str(sum(len(block.splitlines()) for block in song.lyric_blocks)),
                    "author": song.author,
                    "composer": song.composer,
                    "copyright": song.copyright,
                    "key": song.key,
                    "guid": song.guid,
                    "review_flags": ";".join(song.review_flags),
                }
            )

    with (OUTPUT_DIR / "index.csv").open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    write_readme(rows, stats)

    print(f"Exported {len(rows)} songs to {OUTPUT_DIR}/")
    print(f"Skipped {stats['skipped_empty']} empty entries and {stats['skipped_duplicates']} duplicates.")


if __name__ == "__main__":
    export()
