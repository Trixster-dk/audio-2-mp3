# Audio 2 MP3 - TODO

## Done (1.1.0)
- [x] Never overwrite existing MP3 files
- [x] Handle source files with the same name in one batch
- [x] Atomic write via `.part` file
- [x] Working pydub/FFmpeg check, Convert disabled when missing
- [x] Safe startup with invalid `settings.json`
- [x] Lock file controls during conversion
- [x] Translation fallback to English
- [x] Version number and changelog
- [x] Python 3.13+ support (`audioop-lts`)

## Ideas
- [ ] Setting for existing files: rename / skip / overwrite
- [ ] Keep the subfolder structure when converting a folder to one output folder
- [ ] Cancel button for a running conversion
- [ ] Copy tags (artist, title, album) to the MP3
