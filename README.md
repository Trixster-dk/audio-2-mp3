# Audio 2 MP3

Version 1.1.1 - see [CHANGELOG.md](CHANGELOG.md).

A small Python desktop app with a graphical interface for converting audio files to MP3.

The program supports several common audio formats and lets you:

- select individual files
- select an entire folder with supported audio files
- save MP3 files in the same folder or in a custom output folder
- choose the bitrate
- switch between multiple UI languages
- switch between light and dark theme
- view the log directly in the main window
- keep existing files safe: an existing MP3 is never overwritten, a numbered copy such as `song (1).mp3` is created instead

## Features

- Tkinter-based desktop GUI
- English as the default language
- translations stored in `languages/*.json`, one file per language
- folder import with automatic scanning for supported audio files
- About button with project info and supported input formats
- light and dark theme
- MP3 conversion via `pydub`
- support for formats such as `m4a`, `flac`, `wav`, `ogg`, `wma`, `aac`, and more

## Requirements

- Python 3
- `pydub`
- `ffmpeg` (including `ffprobe`) installed and available in PATH

On Python 3.13 and newer, `requirements.txt` also installs `audioop-lts`, which pydub needs.

## Installation

```bash
pip install -r requirements.txt
```

Then install `ffmpeg`:

- Windows: download it from [ffmpeg.org](https://ffmpeg.org/download.html)
- make sure `ffmpeg` is added to your PATH

## Run the project

```bash
py convert.py
```

Or use the batch file:

```bash
AudioConverter.bat
```

## Project files

- `convert.py` - main program with GUI, theme, language switching, and conversion logic
- `languages/` - language folder with one JSON file per language, for example `en.json`, `dk.json`, `de.json`, and `no.json`
- `AudioConverter.bat` - simple Windows launcher
- `requirements.txt` - Python dependencies
- `CHANGELOG.md` - version history
- `DOKUMENTATION.md` - technical documentation

## Author

Coded by Trixster, 2026.

## Note

`converter_log.txt` is intentionally not tracked in Git because it contains local log data.
