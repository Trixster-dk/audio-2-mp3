# Audio 2 MP3

Et lille Python-projekt med grafisk brugerflade til at konvertere lydfiler til MP3.

Programmet understotter flere almindelige lydformater og lader dig:

- vaelge en eller flere lydfiler
- gemme MP3-filer i samme mappe eller i en valgfri output-mappe
- vaelge bitrate
- se en simpel konverteringslog

## Funktioner

- Tkinter-baseret desktop-GUI
- engelsk som standardsprog
- mulighed for at skifte mellem engelsk og dansk i appen
- konvertering til MP3 via `pydub`
- understottelse af formater som `m4a`, `flac`, `wav`, `ogg`, `wma`, `aac` og flere
- logvisning direkte i programmet

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

- `convert.py` - hovedprogrammet med GUI, sprogvalg og konverteringslogik
- `AudioConverter.bat` - simpel Windows-starter
- `requirements.txt` - Python-afhaengigheder

## Author

Coded by Trixster, 2026.

## Note

`converter_log.txt` er bevidst ikke med i Git, fordi den indeholder lokale logdata.
