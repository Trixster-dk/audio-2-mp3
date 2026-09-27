# Audio 2 MP3 - Documentation

Version 1.1.0 - 2026-09-27

## What it is

A Windows-oriented Tkinter desktop app that converts audio files to MP3 using
pydub and FFmpeg. Single file program: `convert.py`.

## Structure

| Path | Purpose |
|------|---------|
| `convert.py` | GUI, settings, translations, conversion logic |
| `languages/*.json` | One UI language per file (`en`, `dk`, `de`, `no`) |
| `translations.json` | Legacy fallback, only used if `languages/` is empty |
| `AudioConverter.bat` | Windows launcher |
| `requirements.txt` | Python dependencies |
| `settings.json` | Created at runtime, not tracked in Git |
| `converter_log.txt` | Created at runtime, not tracked in Git |

## Requirements

- Python 3 with Tkinter
- `pip install -r requirements.txt`
- FFmpeg (`ffmpeg` and `ffprobe`) in PATH

## Run

```bash
py convert.py
```

or double-click `AudioConverter.bat`.

## Behaviour

- **Output name:** `<source name>.mp3`. If that file already exists, or another
  file in the same batch already uses the name, ` (1)`, ` (2)`, ... is added.
  Existing files are never overwritten.
- **Atomic write:** each MP3 is written to `<target>.part` first and renamed
  when the export succeeds. A failed file leaves nothing behind.
- **Dependencies:** checked at startup. If pydub or FFmpeg is missing, an error
  is shown, logged, and the Convert button is disabled.
- **Locked controls:** file selection, clear list and output settings are
  disabled while a conversion runs.
- **Settings** (`settings.json`): `language`, `theme`, `output_location`
  (`same`/`other`), `output_folder`, `bitrate` (`128k`/`192k`/`256k`/`320k`).
  Invalid values are reset to defaults at startup.

## Adding a language

1. Copy `languages/en.json` to `languages/<code>.json`.
2. Translate the values, keep the keys and `{placeholders}` unchanged.
3. Set `language_name`. Missing keys fall back to English.

## Known limitations

- A relative output folder typed manually is resolved from the working
  directory.
- Converting the same files again creates new numbered copies, because
  existing MP3 files are never overwritten.

## Rollback

All changes are in Git. To go back to the previous version:

```bash
git checkout 695a970 -- .
```
