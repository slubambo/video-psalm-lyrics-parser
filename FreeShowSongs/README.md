# FreeShow Songs Text Export

This folder contains one UTF-8 `.txt` file per exported song.

Format used for every song:

1. The first line is the song title.
2. A blank line follows the title.
3. Each original verse/slide block is separated by one blank line.

Source choice:

- `EasyWorship.json` is used first because it contains the largest usable song set.
- `Songs.json` and `Songbook.json` are then used only for unique songs not already exported.
- Clear chord tokens such as `[D/F#]` are removed so the files are ready for screen lyrics.

Export summary:

- Songs exported: 3810
- Songs added from `EasyWorship.json`: 1711
- Songs added from `Songs.json`: 1019
- Songs added from `Songbook.json`: 1080
- Empty entries skipped: 24
- Duplicate entries skipped: 255
- Generic titles improved from lyrics/metadata: 22
- Entries flagged for manual review in `index.csv`: 8

Use `index.csv` to audit source, title, filename, metadata, and review flags.
