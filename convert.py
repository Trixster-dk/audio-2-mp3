import json
import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from pydub import AudioSegment


class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("980x860")
        self.root.minsize(900, 760)

        self.base_dir = Path(__file__).resolve().parent
        self.translations = self.load_translations()
        self.files = []
        self.is_converting = False
        self.language_var = tk.StringVar(value="en")
        self.theme_var = tk.StringVar(value="dark")
        self.output_location_var = tk.StringVar(value="same")
        self.bitrate_var = tk.StringVar(value="320k")

        self.log_file_path = self.base_dir / "converter_log.txt"
        self.supported_formats = [
            ".m4a", ".flac", ".wav", ".ogg", ".wma", ".aac",
            ".opus", ".webm", ".mp4", ".mkv", ".avi", ".aiff",
            ".ac3", ".amr", ".mp2",
        ]

        self.theme_palette = {
            "light": {
                "app_bg": "#F4F7FB", "panel_bg": "#FFFFFF", "header_bg": "#1F5AA6",
                "header_fg": "#FFFFFF", "text": "#1D2433", "muted": "#5E6B82",
                "accent": "#1F5AA6", "entry_bg": "#FFFFFF", "entry_fg": "#1D2433",
                "list_bg": "#FFFFFF", "list_fg": "#1D2433", "log_bg": "#F8FAFD",
                "log_fg": "#1D2433",
            },
            "dark": {
                "app_bg": "#101722", "panel_bg": "#172131", "header_bg": "#0B1220",
                "header_fg": "#EAF2FF", "text": "#EAF2FF", "muted": "#A6B4CC",
                "accent": "#5AA9FF", "entry_bg": "#0F1826", "entry_fg": "#EAF2FF",
                "list_bg": "#0F1826", "list_fg": "#EAF2FF", "log_bg": "#0B1220",
                "log_fg": "#D9E7FF",
            },
        }

        self.check_dependencies()
        self.setup_style()
        self.setup_ui()
        self.apply_theme()
        self.apply_translations()
        self.reload_log()

    def load_translations(self):
        with open(self.base_dir / "translations.json", "r", encoding="utf-8") as translation_file:
            return json.load(translation_file)

    def t(self, key, **kwargs):
        template = self.translations[self.language_var.get()][key]
        return template.format(**kwargs) if kwargs else template

    def setup_style(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

    def setup_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.header_frame = tk.Frame(self.root, height=82)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = tk.Label(self.header_frame, font=("Arial", 20, "bold"))
        self.header_label.grid(row=0, column=0, sticky="w", padx=20, pady=18)

        controls_frame = tk.Frame(self.header_frame)
        controls_frame.grid(row=0, column=1, sticky="e", padx=20, pady=18)

        self.language_label = tk.Label(controls_frame, font=("Arial", 10, "bold"))
        self.language_label.grid(row=0, column=0, padx=(0, 6))

        self.language_menu = ttk.Combobox(controls_frame, state="readonly", width=10)
        self.language_menu.grid(row=0, column=1, padx=(0, 16))
        self.language_menu.bind("<<ComboboxSelected>>", self.change_language)

        self.theme_label = tk.Label(controls_frame, font=("Arial", 10, "bold"))
        self.theme_label.grid(row=0, column=2, padx=(0, 6))

        self.theme_menu = ttk.Combobox(controls_frame, state="readonly", width=10)
        self.theme_menu.grid(row=0, column=3)
        self.theme_menu.bind("<<ComboboxSelected>>", self.change_theme)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=18)
        self.main_frame.grid_rowconfigure(0, weight=3)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=2)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.file_frame = tk.LabelFrame(self.main_frame, font=("Arial", 10, "bold"))
        self.file_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self.file_frame.grid_rowconfigure(1, weight=1)
        self.file_frame.grid_columnconfigure(0, weight=1)

        file_button_frame = tk.Frame(self.file_frame)
        file_button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        file_button_frame.grid_columnconfigure(3, weight=1)

        self.select_files_button = tk.Button(file_button_frame, width=14, command=self.select_files, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
        self.select_files_button.grid(row=0, column=0, padx=(0, 6))

        self.select_folder_button = tk.Button(file_button_frame, width=14, command=self.select_folder, bg="#2E8B57", fg="white", font=("Arial", 9, "bold"))
        self.select_folder_button.grid(row=0, column=1, padx=6)

        self.clear_button = tk.Button(file_button_frame, width=14, command=self.clear_files, bg="#C62828", fg="white", font=("Arial", 9, "bold"))
        self.clear_button.grid(row=0, column=2, padx=6)

        self.file_count_label = tk.Label(file_button_frame, font=("Arial", 10, "bold"))
        self.file_count_label.grid(row=0, column=3, sticky="e")

        list_container = tk.Frame(self.file_frame)
        list_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(list_container, height=12, font=("Courier New", 9))
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        file_scrollbar = tk.Scrollbar(list_container, command=self.file_listbox.yview)
        file_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)

        self.output_frame = tk.LabelFrame(self.main_frame, font=("Arial", 10, "bold"))
        self.output_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.output_frame.grid_columnconfigure(0, weight=1)

        location_frame = tk.Frame(self.output_frame)
        location_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.same_folder_radio = tk.Radiobutton(location_frame, variable=self.output_location_var, value="same", command=self.toggle_output_folder, font=("Arial", 9), anchor="w")
        self.same_folder_radio.grid(row=0, column=0, sticky="w")

        self.other_folder_radio = tk.Radiobutton(location_frame, variable=self.output_location_var, value="other", command=self.toggle_output_folder, font=("Arial", 9), anchor="w")
        self.other_folder_radio.grid(row=1, column=0, sticky="w", pady=(8, 0))

        folder_frame = tk.Frame(self.output_frame)
        folder_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        folder_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = tk.Entry(folder_frame, state="disabled", font=("Arial", 9))
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.browse_button = tk.Button(folder_frame, command=self.select_output_folder, state="disabled")
        self.browse_button.grid(row=0, column=1)

        bitrate_frame = tk.Frame(self.output_frame)
        bitrate_frame.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

        self.bitrate_label = tk.Label(bitrate_frame, font=("Arial", 9, "bold"))
        self.bitrate_label.grid(row=0, column=0, padx=(0, 10))

        self.bitrate_radios = []
        for index, bitrate in enumerate(["128k", "192k", "256k", "320k"], start=1):
            radio = tk.Radiobutton(bitrate_frame, text=bitrate, variable=self.bitrate_var, value=bitrate, font=("Arial", 9))
            radio.grid(row=0, column=index, padx=4)
            self.bitrate_radios.append(radio)

        self.actions_frame = tk.LabelFrame(self.main_frame, font=("Arial", 10, "bold"))
        self.actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.actions_frame.grid_columnconfigure(0, weight=1)

        actions_inner = tk.Frame(self.actions_frame)
        actions_inner.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        actions_inner.grid_columnconfigure(0, weight=1)

        self.convert_button = tk.Button(actions_inner, command=self.start_conversion, bg="#FF9800", fg="white", font=("Arial", 14, "bold"), height=2, cursor="hand2")
        self.convert_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.about_button = tk.Button(actions_inner, command=self.show_about, bg="#6A4C93", fg="white", font=("Arial", 10, "bold"), width=12)
        self.about_button.grid(row=0, column=1)

        lower_frame = tk.Frame(self.main_frame)
        lower_frame.grid(row=3, column=0, sticky="nsew")
        lower_frame.grid_columnconfigure(0, weight=1)
        lower_frame.grid_columnconfigure(1, weight=1)
        lower_frame.grid_rowconfigure(0, weight=1)

        self.progress_frame = tk.LabelFrame(lower_frame, font=("Arial", 10, "bold"))
        self.progress_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.status_label = tk.Label(self.progress_frame, font=("Arial", 9))
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(12, 6))

        self.progress = ttk.Progressbar(self.progress_frame, mode="determinate")
        self.progress.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.progress_label = tk.Label(self.progress_frame, font=("Arial", 9, "bold"))
        self.progress_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 12))

        self.log_frame = tk.LabelFrame(lower_frame, font=("Arial", 10, "bold"))
        self.log_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, font=("Courier New", 9), height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.log_text.config(state="disabled")

        self.footer_label = tk.Label(self.root, font=("Arial", 9))
        self.footer_label.grid(row=2, column=0, pady=(0, 12))

    def apply_translations(self):
        self.root.title(self.t("app_title"))
        self.header_label.config(text=self.t("header_title"))
        self.language_label.config(text=f"{self.t('language')}:")
        self.theme_label.config(text=f"{self.t('theme')}:")
        self.language_menu.config(values=[self.translations["en"]["language_name"], self.translations["da"]["language_name"]])
        self.language_menu.set(self.translations[self.language_var.get()]["language_name"])
        self.theme_menu.config(values=[self.t("theme_light"), self.t("theme_dark")])
        self.theme_menu.set(self.t(f"theme_{self.theme_var.get()}"))
        self.file_frame.config(text=self.t("files_section"))
        self.select_files_button.config(text=self.t("select_files"))
        self.select_folder_button.config(text=self.t("select_folder"))
        self.clear_button.config(text=self.t("clear_list"))
        self.output_frame.config(text=self.t("output_section"))
        self.same_folder_radio.config(text=self.t("same_folder"))
        self.other_folder_radio.config(text=self.t("other_folder"))
        self.browse_button.config(text=self.t("browse"))
        self.bitrate_label.config(text=self.t("bitrate"))
        self.actions_frame.config(text=self.t("actions_section"))
        self.convert_button.config(text=self.t("converting_button") if self.is_converting else self.t("convert"))
        self.about_button.config(text=self.t("about_button"))
        self.progress_frame.config(text=self.t("progress_section"))
        self.log_frame.config(text=self.t("log_section"))
        self.footer_label.config(text=self.t("credits"))
        self.update_file_list()
        self.update_progress_text(0, len(self.files))
        if not self.is_converting:
            self.status_label.config(text=self.t("ready"))

    def apply_theme(self):
        colors = self.theme_palette[self.theme_var.get()]
        self.root.configure(bg=colors["app_bg"])
        self.header_frame.configure(bg=colors["header_bg"])
        self.header_label.configure(bg=colors["header_bg"], fg=colors["header_fg"])
        self.footer_label.configure(bg=colors["app_bg"], fg=colors["muted"])
        for widget in [self.main_frame, self.file_frame, self.output_frame, self.actions_frame, self.progress_frame, self.log_frame]:
            widget.configure(bg=colors["panel_bg"], fg=colors["text"])
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors["app_bg"])
        for widget in self.header_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors["header_bg"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=colors["header_bg"], fg=colors["header_fg"])
        for frame in [self.file_frame, self.output_frame, self.actions_frame, self.progress_frame, self.log_frame]:
            for child in frame.winfo_children():
                self.style_widget_tree(child, colors)
        self.file_listbox.configure(bg=colors["list_bg"], fg=colors["list_fg"], selectbackground=colors["accent"], selectforeground=colors["header_fg"], highlightbackground=colors["accent"], highlightcolor=colors["accent"])
        self.output_entry.configure(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["entry_fg"], disabledbackground=colors["entry_bg"], disabledforeground=colors["muted"])
        self.log_text.configure(bg=colors["log_bg"], fg=colors["log_fg"], insertbackground=colors["log_fg"])
        self.status_label.configure(bg=colors["panel_bg"], fg=colors["muted"])
        self.progress_label.configure(bg=colors["panel_bg"], fg=colors["text"])
        self.style.configure("TCombobox", fieldbackground=colors["entry_bg"], background=colors["panel_bg"], foreground=colors["entry_fg"], arrowcolor=colors["entry_fg"])
        self.style.map("TCombobox", fieldbackground=[("readonly", colors["entry_bg"])])
        self.style.configure("Horizontal.TProgressbar", troughcolor=colors["entry_bg"], background=colors["accent"], bordercolor=colors["entry_bg"], lightcolor=colors["accent"], darkcolor=colors["accent"])

    def style_widget_tree(self, widget, colors):
        if isinstance(widget, tk.Frame):
            widget.configure(bg=colors["panel_bg"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=colors["panel_bg"], fg=colors["text"])
        elif isinstance(widget, tk.Button):
            widget.configure(activebackground=widget.cget("bg"), activeforeground="white")
        elif isinstance(widget, tk.Radiobutton):
            widget.configure(bg=colors["panel_bg"], fg=colors["text"], selectcolor=colors["entry_bg"], activebackground=colors["panel_bg"], activeforeground=colors["text"])
        for child in widget.winfo_children():
            self.style_widget_tree(child, colors)

    def change_language(self, _event=None):
        selected = self.language_menu.get()
        for code, translations in self.translations.items():
            if translations["language_name"] == selected:
                self.language_var.set(code)
                break
        self.apply_translations()

    def change_theme(self, _event=None):
        selected = self.theme_menu.get()
        self.theme_var.set("dark" if selected == self.t("theme_dark") else "light")
        self.apply_theme()
        self.apply_translations()

    def check_dependencies(self):
        try:
            import pydub  # noqa: F401
        except ImportError:
            messagebox.showerror("Error", "pydub is not installed.\n\nInstall it with: pip install pydub")
            return False
        try:
            test_audio = AudioSegment.silent(duration=100)
            temp_file = self.base_dir / "test_ffmpeg.mp3"
            test_audio.export(temp_file, format="mp3")
            os.remove(temp_file)
        except Exception as error:
            messagebox.showerror("Error", f"FFmpeg is not available or is not working correctly.\n\nDownload FFmpeg from: https://ffmpeg.org/download.html\n\nError: {error}")
            return False
        return True

    def file_type_labels(self):
        return [
            (self.t("all_audio_files"), " ".join(f"*{ext}" for ext in self.supported_formats)),
            (self.t("m4a_files"), "*.m4a"),
            (self.t("flac_files"), "*.flac"),
            (self.t("wav_files"), "*.wav"),
            (self.t("ogg_files"), "*.ogg"),
            (self.t("all_files"), "*.*"),
        ]

    def toggle_output_folder(self):
        if self.output_location_var.get() == "other":
            self.output_entry.config(state="normal")
            self.browse_button.config(state="normal")
        else:
            self.output_entry.config(state="disabled")
            self.browse_button.config(state="disabled")

    def normalize_new_files(self, candidates):
        existing = {str(Path(path).resolve()).lower() for path in self.files}
        added = []
        duplicates = 0
        for candidate in candidates:
            resolved = Path(candidate).resolve()
            key = str(resolved).lower()
            if key in existing:
                duplicates += 1
                continue
            existing.add(key)
            added.append(str(resolved))
        return added, duplicates

    def select_files(self):
        files = filedialog.askopenfilenames(title=self.t("select_audio_files_title"), filetypes=self.file_type_labels())
        if not files:
            return
        valid_files = [file for file in files if Path(file).suffix.lower() in self.supported_formats]
        added_files, duplicates = self.normalize_new_files(valid_files)
        self.files.extend(added_files)
        self.update_file_list()
        skipped_count = len(files) - len(valid_files)
        if skipped_count:
            self.log_to_file(self.t("unsupported_skipped", count=skipped_count))
        if duplicates:
            self.log_to_file(self.t("duplicate_skipped", count=duplicates))

    def select_folder(self):
        folder = filedialog.askdirectory(title=self.t("select_input_folder_title"))
        if not folder:
            return
        supported_files = [str(path) for path in Path(folder).rglob("*") if path.is_file() and path.suffix.lower() in self.supported_formats]
        if not supported_files:
            self.log_to_file(self.t("folder_no_supported_files", folder=folder))
            return
        added_files, duplicates = self.normalize_new_files(supported_files)
        self.files.extend(sorted(added_files))
        self.update_file_list()
        self.log_to_file(self.t("folder_added", count=len(added_files), folder=folder))
        if duplicates:
            self.log_to_file(self.t("duplicate_skipped", count=duplicates))

    def clear_files(self):
        self.files = []
        self.update_file_list()
        self.progress["value"] = 0
        self.update_progress_text(0, 0)
        self.status_label.config(text=self.t("ready"))
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

    def append_log_view(self, line):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def reload_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        try:
            if self.log_file_path.exists():
                with open(self.log_file_path, "r", encoding="utf-8") as log_file:
                    content = log_file.read()
                self.log_text.insert(tk.END, content if content else self.t("no_log_yet"))
            else:
                self.log_text.insert(tk.END, self.t("no_log_yet"))
        except Exception as error:
            self.log_text.insert(tk.END, self.t("log_read_failed", error=error))
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def log_to_file(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_message + "\n")
        except Exception as error:
            print(self.t("log_write_failed", error=error))
        self.append_log_view(log_message)

    def show_about(self):
        formats = ", ".join(ext.lstrip(".").upper() for ext in self.supported_formats)
        messagebox.showinfo(self.t("about_title"), self.t("about_message", formats=formats))

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning(self.t("no_files_title"), self.t("no_files_message"))
            self.log_to_file(self.t("conversion_aborted_no_files"))
            return
        if self.output_location_var.get() == "other" and not self.output_entry.get():
            messagebox.showwarning(self.t("missing_folder_title"), self.t("missing_folder_message"))
            self.log_to_file(self.t("conversion_aborted_no_folder"))
            return
        if self.is_converting:
            messagebox.showinfo(self.t("already_converting_title"), self.t("already_converting_message"))
            return
        threading.Thread(target=self.convert_files, daemon=True).start()

    def convert_files(self):
        self.is_converting = True
        self.convert_button.config(state="disabled", bg="#808080", text=self.t("converting_button"))
        bitrate = self.bitrate_var.get()
        total_files = len(self.files)
        successful = 0
        failed = 0
        self.log_to_file("=" * 60)
        self.log_to_file(self.t("conversion_started", count=total_files))
        self.log_to_file(self.t("bitrate_log", bitrate=bitrate))
        for index, input_file in enumerate(self.files, start=1):
            try:
                self.status_label.config(text=self.t("converting_status", filename=os.path.basename(input_file)), fg="#FF9800")
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
                self.log_to_file(self.t("convert_log_line", current=index, total=total_files, source=os.path.basename(input_file), target=f"{filename}.mp3"))
                audio = AudioSegment.from_file(input_file)
                audio.export(output_file, format="mp3", bitrate=bitrate)
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                self.log_to_file(self.t("success_log", size=file_size))
                successful += 1
            except Exception as error:
                self.log_to_file(self.t("failure_log", error=error))
                failed += 1
        self.progress["value"] = 100 if total_files else 0
        self.status_label.config(text=self.t("finished_status", successful=successful, failed=failed), fg="#4CAF50" if failed == 0 else "#F44336")
        self.update_progress_text(total_files, total_files)
        self.log_to_file("=" * 60)
        self.log_to_file(self.t("conversion_finished"))
        self.log_to_file(self.t("successful_count", count=successful))
        self.log_to_file(self.t("failed_count", count=failed))
        self.log_to_file("=" * 60)
        self.is_converting = False
        self.convert_button.config(state="normal", bg="#FF9800", text=self.t("convert"))
        if failed == 0:
            messagebox.showinfo(self.t("success_title"), self.t("success_message", count=successful))
        else:
            messagebox.showwarning(self.t("partial_success_title"), self.t("partial_success_message", successful=successful, failed=failed))


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConverterGUI(root)
    root.mainloop()
