# Church Song Lyrics Exporter

This project helps church media teams preserve, search, clean, and move song lyrics between worship-presentation tools.

It takes song libraries exported from VideoPsalm, EasyWorship, and related formats, then turns them into clean `.txt` files that are easy to read, search, share, and import into FreeShow or another lyrics/presentation system.

The current export is in `FreeShowSongs/` and contains one text file per song.

## Who This Is For

- Church projection and media teams moving songs into FreeShow.
- Worship leaders looking for a searchable folder of church lyrics.
- Anyone cleaning old VideoPsalm or EasyWorship song exports.
- Teams that want each song as its own `.txt` file instead of one large file.

## What You Get

- `FreeShowSongs/` - ready-to-use folder of individual song text files.
- `FreeShowSongs/index.csv` - searchable index with filename, title, source file, metadata, and review flags.
- `FreeShowSongs/README.md` - import notes for the generated song folder.
- `export_freeshow_txt.py` - the main exporter for FreeShow-friendly text files.
- `convert.py` - older converter that creates one combined text file.

Each generated song file follows this simple format:

```text
Song Title

Verse or slide block 1

Verse or slide block 2

Chorus or next slide block
```

This format keeps the title at the top and separates original verse/slide blocks with blank lines, which makes the files suitable for importing or copying into presentation software.

## Current Export

The current `FreeShowSongs/` export was generated from the included song sources:

- `EasyWorship.json` - used first because it has the largest usable song set.
- `Songs.json` - used to add songs not already found in the EasyWorship export.
- `Songbook.json` - used to add more unique songs from the songbook library.

The exporter removes common presentation clutter such as VideoPsalm font tags and clear chord tokens like `[D/F#]`, so the files are cleaner for screen lyrics.

## Using the Lyrics Folder

To find a song, open `FreeShowSongs/` and search by song title. The filename is normally the song title, for example:

```text
Amazing Grace.txt
Above All.txt
Goodness of God.txt
```

If there are several versions of the same song title, the exporter keeps them all and adds a suffix:

```text
24-7 I will praise you Jehovah.txt
24-7 I will praise you Jehovah (2).txt
```

Use `FreeShowSongs/index.csv` when you need more detail, such as the original source, author, copyright text, key, or entries that may need manual review.

## Importing Into FreeShow

FreeShow versions may label the import menu differently, but the workflow is usually:

1. Open FreeShow.
2. Go to the Songs or Library area.
3. Choose the import option.
4. Select text/plain-text import if FreeShow asks for a format.
5. Choose files from `FreeShowSongs/`, or select the whole folder if your FreeShow version supports folder import.
6. After import, check a few songs to confirm verse breaks and titles imported as expected.

If a song imports as one long block, open the `.txt` file and split the lyrics inside FreeShow, or adjust that file's blank lines before importing again.

## Regenerating the FreeShow Folder

Requirements:

- Python 3.7 or newer.
- No external Python packages are required.

Run:

```bash
python3 export_freeshow_txt.py
```

This recreates `FreeShowSongs/` from the source JSON files. The folder contains a marker file so the script can safely replace its own generated output.

## Source Files

- `EasyWorship.json` - largest source used by the FreeShow exporter.
- `Songs.json` - raw VideoPsalm-style export.
- `Songbook.json` - songbook export.
- `FixedSongs.json` and `SongbookFixedSongs.json` - older intermediate cleaned files.
- `Songs.txt` - older combined text output.

The JSON exports are not strict JSON. They contain JavaScript-style keys, raw multiline strings, and occasional control characters. The exporter handles those issues before creating the final `.txt` files.

## Quality Notes

The exporter is conservative. It does not silently delete unusual entries. Items that look like announcements, themes, phone-number notices, or non-song content are kept but flagged in `FreeShowSongs/index.csv` for manual review.

Before using the full library in a live service, review:

- Songs with duplicate titles.
- Songs with `review_flags` in `index.csv`.
- Copyright-sensitive songs where your church needs reporting or licensing details.
- Any song whose source title was generic, such as `New song`.

## Older Combined Text Export

The older script still exists:

```bash
python3 convert.py
```

It creates one combined text file instead of individual files. For FreeShow imports, use `export_freeshow_txt.py` and the `FreeShowSongs/` folder.

## License

Use this project freely for church song library cleanup and migration. Make sure your church follows the licensing requirements for the songs you display.
