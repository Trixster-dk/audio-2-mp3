import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from pydub import AudioSegment


TRANSLATIONS = {
    "en": {
        "app_title": "Audio to MP3 Converter",
        "header_title": "Audio to MP3 Converter",
        "language": "Language",
        "language_english": "English",
        "language_danish": "Danish",
        "files_section": "Files",
        "select_files": "Select files",
        "clear_list": "Clear list",
        "files_selected_singular": "{count} file selected",
        "files_selected_plural": "{count} files selected",
        "output_section": "Output settings",
        "same_folder": "Save in the same folder as the source file",
        "other_folder": "Choose a different folder:",
        "browse": "Browse",
        "bitrate": "MP3 bitrate:",
        "convert": "Convert to MP3",
        "converting_button": "Converting...",
        "show_log": "Show log",
        "progress_section": "Progress",
        "ready": "Ready to convert",
        "progress_count": "{current} / {total} files",
        "credits": "Coded by Trixster, 2026",
        "all_audio_files": "All audio files",
        "m4a_files": "M4A files",
        "flac_files": "FLAC files",
        "wav_files": "WAV files",
        "ogg_files": "OGG files",
        "all_files": "All files",
        "select_audio_files_title": "Select audio files",
        "unsupported_skipped": "{count} files were skipped (unsupported format)",
        "file_list_cleared": "File list cleared",
        "select_output_folder_title": "Select output folder",
        "output_folder_selected": "Output folder selected: {folder}",
        "log_write_failed": "Could not write to log: {error}",
        "log_window_title": "Conversion log",
        "reload_log": "Reload",
        "clear_log": "Clear log",
        "open_log_file": "Open log file",
        "no_log_yet": "No log yet...\n",
        "log_read_failed": "Error reading log: {error}\n",
        "confirm_title": "Confirm",
        "confirm_clear_log": "Are you sure you want to clear the entire log?",
        "log_cleared": "Log cleared",
        "error_title": "Error",
        "log_clear_failed": "Could not clear log: {error}",
        "info_title": "Info",
        "log_missing": "The log file does not exist yet",
        "log_open_failed": "Could not open log file: {error}",
        "no_files_title": "No files",
        "no_files_message": "Please select some files first.",
        "conversion_aborted_no_files": "Conversion aborted: no files selected",
        "missing_folder_title": "Missing folder",
        "missing_folder_message": "Please choose an output folder.",
        "conversion_aborted_no_folder": "Conversion aborted: no output folder selected",
        "already_converting_title": "Already converting",
        "already_converting_message": "A conversion is already in progress.",
        "conversion_started": "Starting a new conversion of {count} files",
        "bitrate_log": "Bitrate: {bitrate}",
        "converting_status": "Converting: {filename}",
        "convert_log_line": "[{current}/{total}] {source} -> {target}",
        "success_log": "Success! ({size:.2f} MB)",
        "failure_log": "ERROR: {error}",
        "finished_status": "Finished. {successful} succeeded, {failed} failed",
        "conversion_finished": "Conversion finished!",
        "successful_count": "Successful: {count}",
        "failed_count": "Failed: {count}",
        "success_title": "Success",
        "success_message": "All {count} files were converted successfully.",
        "partial_success_title": "Partial success",
        "partial_success_message": "Conversion finished.\n\nSuccessful: {successful}\nFailed: {failed}\n\nCheck the log for details.",
        "dependency_missing_title": "Missing dependency",
        "dependency_missing_message": "pydub is not installed.\n\nInstall it with: pip install pydub",
        "ffmpeg_error_title": "FFmpeg error",
        "ffmpeg_error_message": "FFmpeg is not available or is not working correctly.\n\nDownload FFmpeg from: https://ffmpeg.org/download.html\n\nError: {error}",
    },
    "da": {
        "app_title": "Audio Converter til MP3",
        "header_title": "Audio Converter til MP3",
        "language": "Sprog",
        "language_english": "English",
        "language_danish": "Dansk",
        "files_section": "Filer",
        "select_files": "Vaelg filer",
        "clear_list": "Ryd liste",
        "files_selected_singular": "{count} fil valgt",
        "files_selected_plural": "{count} filer valgt",
        "output_section": "Output indstillinger",
        "same_folder": "Gem i samme mappe som originalen",
        "other_folder": "Vaelg en anden mappe:",
        "browse": "Gennemse",
        "bitrate": "MP3 bitrate:",
        "convert": "Konverter til MP3",
        "converting_button": "Konverterer...",
        "show_log": "Vis log",
        "progress_section": "Fremskridt",
        "ready": "Klar til konvertering",
        "progress_count": "{current} / {total} filer",
        "credits": "Coded by Trixster, 2026",
        "all_audio_files": "Alle lydfiler",
        "m4a_files": "M4A filer",
        "flac_files": "FLAC filer",
        "wav_files": "WAV filer",
        "ogg_files": "OGG filer",
        "all_files": "Alle filer",
        "select_audio_files_title": "Vaelg lydfiler",
        "unsupported_skipped": "{count} filer blev sprunget over (ikke understottet format)",
        "file_list_cleared": "Filliste ryddet",
        "select_output_folder_title": "Vaelg output mappe",
        "output_folder_selected": "Output mappe valgt: {folder}",
        "log_write_failed": "Kunne ikke skrive til log: {error}",
        "log_window_title": "Konverteringslog",
        "reload_log": "Genindlaes",
        "clear_log": "Ryd log",
        "open_log_file": "Aabn log fil",
        "no_log_yet": "Ingen log endnu...\n",
        "log_read_failed": "Fejl ved indlaesning af log: {error}\n",
        "confirm_title": "Bekraeft",
        "confirm_clear_log": "Er du sikker paa, at du vil rydde hele loggen?",
        "log_cleared": "Log ryddet",
        "error_title": "Fejl",
        "log_clear_failed": "Kunne ikke rydde log: {error}",
        "info_title": "Info",
        "log_missing": "Logfilen eksisterer ikke endnu",
        "log_open_failed": "Kunne ikke aabne logfil: {error}",
        "no_files_title": "Ingen filer",
        "no_files_message": "Vaelg venligst nogle filer forst.",
        "conversion_aborted_no_files": "Konvertering afbrudt: Ingen filer valgt",
        "missing_folder_title": "Manglende mappe",
        "missing_folder_message": "Vaelg venligst en output mappe.",
        "conversion_aborted_no_folder": "Konvertering afbrudt: Ingen output mappe valgt",
        "already_converting_title": "Konverterer allerede",
        "already_converting_message": "En konvertering er allerede i gang.",
        "conversion_started": "Starter ny konvertering af {count} filer",
        "bitrate_log": "Bitrate: {bitrate}",
        "converting_status": "Konverterer: {filename}",
        "convert_log_line": "[{current}/{total}] {source} -> {target}",
        "success_log": "Succes! ({size:.2f} MB)",
        "failure_log": "FEJL: {error}",
        "finished_status": "Faerdig. {successful} succesfulde, {failed} fejlede",
        "conversion_finished": "Konvertering faerdig!",
        "successful_count": "Succesfulde: {count}",
        "failed_count": "Fejlede: {count}",
        "success_title": "Succes",
        "success_message": "Alle {count} filer blev konverteret succesfuldt.",
        "partial_success_title": "Delvis succes",
        "partial_success_message": "Konvertering faerdig.\n\nSuccesfulde: {successful}\nFejlede: {failed}\n\nTjek loggen for detaljer.",
        "dependency_missing_title": "Manglende afhaengighed",
        "dependency_missing_message": "pydub er ikke installeret.\n\nInstaller med: pip install pydub",
        "ffmpeg_error_title": "FFmpeg fejl",
        "ffmpeg_error_message": "FFmpeg er ikke tilgaengelig eller virker ikke korrekt.\n\nDownload FFmpeg fra: https://ffmpeg.org/download.html\n\nFejl: {error}",
    },
}


class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("820x640")

        self.files = []
        self.is_converting = False
        self.log_window = None
        self.log_text = None
        self.language_var = tk.StringVar(value="en")
        self.language_names = {
            "en": TRANSLATIONS["en"]["language_english"],
            "da": TRANSLATIONS["en"]["language_danish"],
        }

        self.log_file_path = os.path.join(os.path.dirname(__file__), "converter_log.txt")
        self.supported_formats = [
            ".m4a",
            ".flac",
            ".wav",
            ".ogg",
            ".wma",
            ".aac",
            ".opus",
            ".webm",
            ".mp4",
            ".mkv",
            ".avi",
            ".aiff",
            ".ac3",
            ".amr",
            ".mp2",
        ]

        self.check_dependencies()
        self.setup_ui()
        self.apply_translations()

    def t(self, key, **kwargs):
        template = TRANSLATIONS[self.language_var.get()][key]
        if kwargs:
            return template.format(**kwargs)
        return template

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg="#1F5AA6", height=72)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        self.header_label = tk.Label(
            header_frame,
            font=("Arial", 18, "bold"),
            bg="#1F5AA6",
            fg="white",
        )
        self.header_label.pack(side=tk.LEFT, padx=20)

        language_frame = tk.Frame(header_frame, bg="#1F5AA6")
        language_frame.pack(side=tk.RIGHT, padx=20)

        self.language_label = tk.Label(
            language_frame,
            font=("Arial", 10, "bold"),
            bg="#1F5AA6",
            fg="white",
        )
        self.language_label.pack(side=tk.LEFT, padx=(0, 8))

        self.language_menu = ttk.Combobox(
            language_frame,
            state="readonly",
            width=12,
            values=list(self.language_names.values()),
        )
        self.language_menu.current(0)
        self.language_menu.pack(side=tk.LEFT)
        self.language_menu.bind("<<ComboboxSelected>>", self.change_language)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.file_frame = tk.LabelFrame(main_frame, font=("Arial", 10, "bold"))
        self.file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        button_frame = tk.Frame(self.file_frame)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        self.select_button = tk.Button(
            button_frame,
            command=self.select_files,
            width=15,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(
            button_frame,
            command=self.clear_files,
            width=15,
            bg="#f44336",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.file_count_label = tk.Label(
            button_frame,
            font=("Arial", 10, "bold"),
            fg="#1F5AA6",
        )
        self.file_count_label.pack(side=tk.LEFT, padx=20)

        list_container = tk.Frame(self.file_frame)
        list_container.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_container,
            height=8,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        self.output_frame = tk.LabelFrame(main_frame, font=("Arial", 10, "bold"))
        self.output_frame.pack(fill=tk.X, pady=(0, 10))

        location_frame = tk.Frame(self.output_frame)
        location_frame.pack(pady=10, padx=10, fill=tk.X)

        self.output_location_var = tk.StringVar(value="same")

        self.same_folder_radio = tk.Radiobutton(
            location_frame,
            variable=self.output_location_var,
            value="same",
            command=self.toggle_output_folder,
            font=("Arial", 9),
        )
        self.same_folder_radio.pack(anchor=tk.W)

        self.other_folder_radio = tk.Radiobutton(
            location_frame,
            variable=self.output_location_var,
            value="other",
            command=self.toggle_output_folder,
            font=("Arial", 9),
        )
        self.other_folder_radio.pack(anchor=tk.W, pady=(5, 0))

        folder_frame = tk.Frame(self.output_frame)
        folder_frame.pack(pady=5, padx=10, fill=tk.X)

        self.output_entry = tk.Entry(folder_frame, state="disabled")
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.browse_button = tk.Button(
            folder_frame,
            command=self.select_output_folder,
            state="disabled",
        )
        self.browse_button.pack(side=tk.LEFT)

        bitrate_frame = tk.Frame(self.output_frame)
        bitrate_frame.pack(pady=10, padx=10, fill=tk.X)

        self.bitrate_label = tk.Label(
            bitrate_frame,
            font=("Arial", 9, "bold"),
        )
        self.bitrate_label.pack(side=tk.LEFT, padx=(0, 10))

        self.bitrate_var = tk.StringVar(value="320k")
        for bitrate in ["128k", "192k", "256k", "320k"]:
            tk.Radiobutton(
                bitrate_frame,
                text=bitrate,
                variable=self.bitrate_var,
                value=bitrate,
                font=("Arial", 9),
            ).pack(side=tk.LEFT, padx=5)

        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.convert_button = tk.Button(
            action_frame,
            command=self.start_conversion,
            bg="#FF9800",
            fg="white",
            font=("Arial", 14, "bold"),
            height=2,
            cursor="hand2",
        )
        self.convert_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.log_button = tk.Button(
            action_frame,
            command=self.open_log_window,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2",
        )
        self.log_button.pack(side=tk.LEFT)

        self.progress_frame = tk.LabelFrame(main_frame, font=("Arial", 10, "bold"))
        self.progress_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            self.progress_frame,
            font=("Arial", 9),
            fg="#666666",
        )
        self.status_label.pack(pady=(10, 5), padx=10)

        self.progress = ttk.Progressbar(
            self.progress_frame,
            mode="determinate",
            length=100,
        )
        self.progress.pack(pady=(0, 10), padx=10, fill=tk.X)

        self.progress_label = tk.Label(
            self.progress_frame,
            font=("Arial", 9, "bold"),
        )
        self.progress_label.pack(pady=(0, 10))

        self.footer_label = tk.Label(
            self.root,
            font=("Arial", 9),
            fg="#666666",
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=(0, 10))

    def apply_translations(self):
        self.root.title(self.t("app_title"))
        self.header_label.config(text=self.t("header_title"))
        self.language_label.config(text=f"{self.t('language')}:")
        self.file_frame.config(text=self.t("files_section"))
        self.select_button.config(text=self.t("select_files"))
        self.clear_button.config(text=self.t("clear_list"))
        self.output_frame.config(text=self.t("output_section"))
        self.same_folder_radio.config(text=self.t("same_folder"))
        self.other_folder_radio.config(text=self.t("other_folder"))
        self.browse_button.config(text=self.t("browse"))
        self.bitrate_label.config(text=self.t("bitrate"))
        self.convert_button.config(
            text=self.t("converting_button") if self.is_converting else self.t("convert")
        )
        self.log_button.config(text=self.t("show_log"))
        self.progress_frame.config(text=self.t("progress_section"))
        self.footer_label.config(text=self.t("credits"))

        if self.log_window and self.log_window.winfo_exists():
            self.log_window.title(self.t("log_window_title"))
            self.reload_log_button.config(text=self.t("reload_log"))
            self.clear_log_button.config(text=self.t("clear_log"))
            self.open_log_file_button.config(text=self.t("open_log_file"))

        self.update_file_list()
        self.update_progress_text(0, len(self.files))
        if not self.is_converting:
            self.status_label.config(text=self.t("ready"))

    def change_language(self, _event=None):
        selected_label = self.language_menu.get()
        for language_code, display_label in self.language_names.items():
            if selected_label == display_label:
                self.language_var.set(language_code)
                break
        self.apply_translations()

    def check_dependencies(self):
        try:
            import pydub  # noqa: F401
        except ImportError:
            messagebox.showerror(
                self.t("dependency_missing_title"),
                self.t("dependency_missing_message"),
            )
            return False

        try:
            test_audio = AudioSegment.silent(duration=100)
            test_audio.export("test_ffmpeg.mp3", format="mp3")
            os.remove("test_ffmpeg.mp3")
        except Exception as error:
            messagebox.showerror(
                self.t("ffmpeg_error_title"),
                self.t("ffmpeg_error_message", error=error),
            )
            return False

        return True

    def toggle_output_folder(self):
        if self.output_location_var.get() == "other":
            self.output_entry.config(state="normal")
            self.browse_button.config(state="normal")
        else:
            self.output_entry.config(state="disabled")
            self.browse_button.config(state="disabled")

    def file_type_labels(self):
        return [
            (self.t("all_audio_files"), " ".join(f"*{ext}" for ext in self.supported_formats)),
            (self.t("m4a_files"), "*.m4a"),
            (self.t("flac_files"), "*.flac"),
            (self.t("wav_files"), "*.wav"),
            (self.t("ogg_files"), "*.ogg"),
            (self.t("all_files"), "*.*"),
        ]

    def select_files(self):
        files = filedialog.askopenfilenames(
            title=self.t("select_audio_files_title"),
            filetypes=self.file_type_labels(),
        )

        if files:
            valid_files = [file for file in files if Path(file).suffix.lower() in self.supported_formats]
            self.files.extend(valid_files)
            self.update_file_list()

            skipped_count = len(files) - len(valid_files)
            if skipped_count:
                self.log_to_file(self.t("unsupported_skipped", count=skipped_count))

    def clear_files(self):
        self.files = []
        self.update_file_list()
        self.log_to_file(self.t("file_list_cleared"))

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file_path in self.files:
            filename = os.path.basename(file_path)
            extension = Path(file_path).suffix.upper()
            self.file_listbox.insert(tk.END, f"{filename} [{extension}]")

        count = len(self.files)
        key = "files_selected_singular" if count == 1 else "files_selected_plural"
        self.file_count_label.config(text=self.t(key, count=count))

    def update_progress_text(self, current, total):
        self.progress_label.config(text=self.t("progress_count", current=current, total=total))

    def select_output_folder(self):
        folder = filedialog.askdirectory(title=self.t("select_output_folder_title"))
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self.log_to_file(self.t("output_folder_selected", folder=folder))

    def log_to_file(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        try:
            with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_message + "\n")
        except Exception as error:
            print(self.t("log_write_failed", error=error))

        if self.log_window and self.log_window.winfo_exists():
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, log_message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")

    def open_log_window(self):
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            return

        self.log_window = tk.Toplevel(self.root)
        self.log_window.geometry("700x400")
        self.log_window.title(self.t("log_window_title"))

        toolbar = tk.Frame(self.log_window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        self.reload_log_button = tk.Button(
            toolbar,
            command=self.reload_log,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        self.reload_log_button.pack(side=tk.LEFT, padx=5)

        self.clear_log_button = tk.Button(
            toolbar,
            command=self.clear_log,
            bg="#f44336",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        self.clear_log_button.pack(side=tk.LEFT, padx=5)

        self.open_log_file_button = tk.Button(
            toolbar,
            command=self.open_log_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        self.open_log_file_button.pack(side=tk.LEFT, padx=5)

        self.log_text = scrolledtext.ScrolledText(
            self.log_window,
            wrap=tk.WORD,
            font=("Courier", 9),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.apply_translations()
        self.reload_log()

    def reload_log(self):
        if not self.log_window or not self.log_window.winfo_exists():
            return

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)

        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, "r", encoding="utf-8") as log_file:
                    self.log_text.insert(tk.END, log_file.read())
            else:
                self.log_text.insert(tk.END, self.t("no_log_yet"))
        except Exception as error:
            self.log_text.insert(tk.END, self.t("log_read_failed", error=error))

        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def clear_log(self):
        if messagebox.askyesno(self.t("confirm_title"), self.t("confirm_clear_log")):
            try:
                with open(self.log_file_path, "w", encoding="utf-8") as log_file:
                    log_file.write("")
                self.reload_log()
                self.log_to_file(self.t("log_cleared"))
            except Exception as error:
                messagebox.showerror(self.t("error_title"), self.t("log_clear_failed", error=error))

    def open_log_file(self):
        try:
            if os.path.exists(self.log_file_path):
                os.startfile(self.log_file_path)
            else:
                messagebox.showinfo(self.t("info_title"), self.t("log_missing"))
        except Exception as error:
            messagebox.showerror(self.t("error_title"), self.t("log_open_failed", error=error))

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning(self.t("no_files_title"), self.t("no_files_message"))
            self.log_to_file(self.t("conversion_aborted_no_files"))
            return

        if self.output_location_var.get() == "other":
            output_folder = self.output_entry.get()
            if not output_folder:
                messagebox.showwarning(
                    self.t("missing_folder_title"),
                    self.t("missing_folder_message"),
                )
                self.log_to_file(self.t("conversion_aborted_no_folder"))
                return

        if self.is_converting:
            messagebox.showinfo(
                self.t("already_converting_title"),
                self.t("already_converting_message"),
            )
            return

        threading.Thread(target=self.convert_files, daemon=True).start()

    def convert_files(self):
        self.is_converting = True
        self.convert_button.config(state="disabled", bg="#CCCCCC", text=self.t("converting_button"))

        bitrate = self.bitrate_var.get()
        total_files = len(self.files)
        successful = 0
        failed = 0

        self.log_to_file("=" * 60)
        self.log_to_file(self.t("conversion_started", count=total_files))
        self.log_to_file(self.t("bitrate_log", bitrate=bitrate))

        for index, input_file in enumerate(self.files, start=1):
            try:
                self.status_label.config(
                    text=self.t("converting_status", filename=os.path.basename(input_file)),
                    fg="#FF9800",
                )
                self.update_progress_text(index, total_files)
                self.progress["value"] = (index / total_files) * 100
                self.root.update_idletasks()

                if self.output_location_var.get() == "same":
                    output_folder = os.path.dirname(input_file)
                else:
                    output_folder = self.output_entry.get()
                    os.makedirs(output_folder, exist_ok=True)

                filename = Path(input_file).stem
                output_file = os.path.join(output_folder, f"{filename}.mp3")

                self.log_to_file(
                    self.t(
                        "convert_log_line",
                        current=index,
                        total=total_files,
                        source=os.path.basename(input_file),
                        target=f"{filename}.mp3",
                    )
                )

                audio = AudioSegment.from_file(input_file)
                audio.export(output_file, format="mp3", bitrate=bitrate)

                file_size = os.path.getsize(output_file) / (1024 * 1024)
                self.log_to_file(self.t("success_log", size=file_size))
                successful += 1
            except Exception as error:
                self.log_to_file(self.t("failure_log", error=error))
                failed += 1

        self.progress["value"] = 100
        self.status_label.config(
            text=self.t("finished_status", successful=successful, failed=failed),
            fg="#4CAF50" if failed == 0 else "#F44336",
        )
        self.update_progress_text(total_files, total_files)

        self.log_to_file("=" * 60)
        self.log_to_file(self.t("conversion_finished"))
        self.log_to_file(self.t("successful_count", count=successful))
        self.log_to_file(self.t("failed_count", count=failed))
        self.log_to_file("=" * 60 + "\n")

        self.convert_button.config(
            state="normal",
            bg="#FF9800",
            text=self.t("convert"),
        )
        self.is_converting = False

        if failed == 0:
            messagebox.showinfo(self.t("success_title"), self.t("success_message", count=successful))
        else:
            messagebox.showwarning(
                self.t("partial_success_title"),
                self.t("partial_success_message", successful=successful, failed=failed),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConverterGUI(root)
    root.mainloop()
