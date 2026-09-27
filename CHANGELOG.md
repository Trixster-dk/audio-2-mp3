# Changelog

All notable changes to Audio 2 MP3 are documented in this file.
The project uses [Semantic Versioning](https://semver.org/).

## [1.1.1] - 2026-09-27

### Fixed
- Danish, Norwegian and German texts now use the proper letters (æ, ø, å,
  ä, ö, ü) instead of ASCII replacements such as "Vaelg", "Stottede" and
  "wahlen".
- The About button in Danish now says "Om" instead of "About".
- The footer credit line is translated in Danish, Norwegian and German.
- Danish: "output mappe" is written as "output-mappe".

## [1.1.0] - 2026-09-27

### Fixed
- Existing MP3 files are never overwritten. If `name.mp3` already exists, the
  output is saved as `name (1).mp3`, `name (2).mp3`, and so on. The rename is
  written to the log.
- Source files with the same name no longer overwrite each other
  (`song.flac` + `song.wav`, or files with the same name in different
  subfolders when converting to one output folder).
- A failed conversion no longer leaves an empty or broken MP3 behind. Output is
  written to a temporary `.part` file and only moved into place on success.
- The pydub check now works: a missing pydub no longer crashes the program at
  import time, it shows an error message instead.
- If pydub or FFmpeg is missing, the Convert button is disabled and the status
  line says why, instead of failing on every file.
- An invalid language in `settings.json` can no longer crash the startup.
- The FFmpeg check encodes to memory and no longer needs write access to the
  program folder.
- File buttons, output settings and "Clear list" are locked while a conversion
  runs, so the progress display cannot be reset mid-conversion.
- The progress bar now shows completed files and only reaches 100% when the
  last file is done.
- Changing language during a conversion no longer resets the progress counter.
- Duplicate detection follows the platform's case rules instead of always
  ignoring case.
- `AudioConverter.bat` now works when started from another folder.
- Python 3.13+: added `audioop-lts` to `requirements.txt`, because pydub needs
  the `audioop` module that was removed from Python 3.13.

### Added
- Version number, shown in the About dialog.
- Missing keys in a language file fall back to English instead of crashing.
- Errors while saving `settings.json` are written to the log.
- New translation keys: `dependencies_unavailable`, `output_renamed`,
  `settings_save_failed`, `about_version`.

### Changed
- The log view only loads the newest 2000 lines at startup. The full log stays
  in `converter_log.txt`.
- Log writes are serialized with a lock, so the conversion thread and the UI
  never write to the log at the same time.
- The legacy `translations.json` fallback now uses the language code `dk`, the
  same as `languages/dk.json`. An old `da` setting is mapped to `dk`.

## [1.0.0] - 2026

### Added
- Tkinter GUI for converting audio files to MP3 with pydub and FFmpeg.
- File and folder import, output folder selection and bitrate selection.
- Languages in `languages/*.json` (English, Danish, German, Norwegian).
- Light and dark theme, About dialog and a log view.
