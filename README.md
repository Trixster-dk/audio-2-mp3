# Audio 2 MP3

Et lille Python-projekt med grafisk brugerflade til at konvertere lydfiler til MP3.

Programmet understotter flere almindelige lydformater og lader dig:

- vaelge enkelte filer
- vaelge en hel mappe med understottede lydfiler
- gemme MP3-filer i samme mappe eller i en valgfri output-mappe
- vaelge bitrate
- skifte mellem engelsk og dansk
- skifte mellem lyst og morkt tema
- se log direkte i hovedvinduet

## Funktioner

- Tkinter-baseret desktop-GUI
- engelsk som standardsprog
- oversaettelser ligger i `translations.json`, sa flere sprog let kan tilfojes senere
- mappevalg med automatisk scanning efter understottede lydfiler
- About-knap med info om projekt og understottede inputformater
- lyst og morkt tema
- konvertering til MP3 via `pydub`
- understottelse af formater som `m4a`, `flac`, `wav`, `ogg`, `wma`, `aac` og flere

## Krav

- Python 3
- `pydub`
- `ffmpeg` installeret og tilgaengelig i PATH

## Installation

```bash
pip install -r requirements.txt
```

Installer derefter `ffmpeg`:

- Windows: download fra [ffmpeg.org](https://ffmpeg.org/download.html)
- sorg for at `ffmpeg` er tilfojet til din PATH

## Kor projektet

```bash
py convert.py
```

Eller brug batch-filen:

```bash
AudioConverter.bat
```

## Filer i projektet

- `convert.py` - hovedprogrammet med GUI, tema, sprogvalg og konverteringslogik
- `translations.json` - sprogfil med tekster til brugerfladen
- `AudioConverter.bat` - simpel Windows-starter
- `requirements.txt` - Python-afhaengigheder

## Author

Coded by Trixster, 2026.

## Note

`converter_log.txt` er bevidst ikke med i Git, fordi den indeholder lokale logdata.
