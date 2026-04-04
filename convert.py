import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import threading
from pydub import AudioSegment
import os
from pathlib import Path
from datetime import datetime

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter til MP3")
        self.root.geometry("800x600")
        
        self.files = []
        self.is_converting = False
        self.log_window = None
        
        # Log fil
        self.log_file_path = os.path.join(os.path.dirname(__file__), "converter_log.txt")
        
        # Understøttede formater
        self.supported_formats = [
            '.m4a', '.flac', '.wav', '.ogg', '.wma', '.aac', 
            '.opus', '.webm', '.mp4', '.mkv', '.avi', '.aiff',
            '.ac3', '.amr', '.mp2'
        ]
        
        self.check_dependencies()
        self.setup_ui()
    
    def check_dependencies(self):
        """Tjek om pydub og ffmpeg er tilgængelige"""
        try:
            import pydub
        except ImportError:
            messagebox.showerror(
                "Manglende afhængighed",
                "pydub er ikke installeret!\n\nInstaller med: pip install pydub"
            )
            return False
        
        # Test ffmpeg
        try:
            test_audio = AudioSegment.silent(duration=100)
            test_audio.export("test_ffmpeg.mp3", format="mp3")
            os.remove("test_ffmpeg.mp3")
        except Exception as e:
            messagebox.showerror(
                "FFmpeg fejl",
                f"FFmpeg er ikke tilgængelig eller fungerer ikke korrekt!\n\n"
                f"Download FFmpeg fra: https://ffmpeg.org/download.html\n\n"
                f"Fejl: {str(e)}"
            )
            return False
        
        return True
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2196F3", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header = tk.Label(
            header_frame,
            text="🎵 Audio Converter til MP3",
            font=("Arial", 18, "bold"),
            bg="#2196F3",
            fg="white"
        )
        header.pack(expand=True)
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Fil-sektion
        file_frame = tk.LabelFrame(main_frame, text="Filer", font=("Arial", 10, "bold"))
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        button_frame = tk.Frame(file_frame)
        button_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Button(
            button_frame,
            text="📁 Vælg filer",
            command=self.select_files,
            width=15,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑️ Ryd liste",
            command=self.clear_files,
            width=15,
            bg="#f44336",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        self.file_count_label = tk.Label(
            button_frame,
            text="0 filer valgt",
            font=("Arial", 10, "bold"),
            fg="#2196F3"
        )
        self.file_count_label.pack(side=tk.LEFT, padx=20)
        
        # Filliste med scrollbar
        list_container = tk.Frame(file_frame)
        list_container.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_container,
            height=8,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9)
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Output sektion
        output_frame = tk.LabelFrame(main_frame, text="Output indstillinger", font=("Arial", 10, "bold"))
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output mappe valg
        location_frame = tk.Frame(output_frame)
        location_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.output_location_var = tk.StringVar(value="samme")
        
        tk.Radiobutton(
            location_frame,
            text="Samme mappe som original",
            variable=self.output_location_var,
            value="samme",
            command=self.toggle_output_folder,
            font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        tk.Radiobutton(
            location_frame,
            text="Vælg anden mappe:",
            variable=self.output_location_var,
            value="anden",
            command=self.toggle_output_folder,
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=(5, 0))
        
        folder_frame = tk.Frame(output_frame)
        folder_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.output_entry = tk.Entry(folder_frame, state='disabled')
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_button = tk.Button(
            folder_frame,
            text="📂 Gennemse",
            command=self.select_output_folder,
            state='disabled'
        )
        self.browse_button.pack(side=tk.LEFT)
        
        # Bitrate
        bitrate_frame = tk.Frame(output_frame)
        bitrate_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(
            bitrate_frame,
            text="MP3 Bitrate:",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.bitrate_var = tk.StringVar(value="320k")
        bitrates = ["128k", "192k", "256k", "320k"]
        
        for bitrate in bitrates:
            tk.Radiobutton(
                bitrate_frame,
                text=bitrate,
                variable=self.bitrate_var,
                value=bitrate,
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=5)
        
        # Konverter og log sektion
        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.convert_button = tk.Button(
            action_frame,
            text="🚀 KONVERTER TIL MP3",
            command=self.start_conversion,
            bg="#FF9800",
            fg="white",
            font=("Arial", 14, "bold"),
            height=2,
            cursor="hand2"
        )
        self.convert_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.log_button = tk.Button(
            action_frame,
            text="📋 Vis Log",
            command=self.open_log_window,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2"
        )
        self.log_button.pack(side=tk.LEFT)
        
        # Progress sektion
        progress_frame = tk.LabelFrame(main_frame, text="Fremskridt", font=("Arial", 10, "bold"))
        progress_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            progress_frame,
            text="Klar til konvertering",
            font=("Arial", 9),
            fg="#666"
        )
        self.status_label.pack(pady=(10, 5), padx=10)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=100
        )
        self.progress.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="0 / 0 filer",
            font=("Arial", 9, "bold")
        )
        self.progress_label.pack(pady=(0, 10))
    
    def toggle_output_folder(self):
        """Aktiver/deaktiver output mappe vælger"""
        if self.output_location_var.get() == "anden":
            self.output_entry.config(state='normal')
            self.browse_button.config(state='normal')
        else:
            self.output_entry.config(state='disabled')
            self.browse_button.config(state='disabled')
    
    def select_files(self):
        filetypes = [
            ("Alle lydfiler", " ".join(f"*{ext}" for ext in self.supported_formats)),
            ("M4A filer", "*.m4a"),
            ("FLAC filer", "*.flac"),
            ("WAV filer", "*.wav"),
            ("OGG filer", "*.ogg"),
            ("Alle filer", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Vælg lydfiler",
            filetypes=filetypes
        )
        
        if files:
            # Filtrer kun understøttede formater
            valid_files = [f for f in files if Path(f).suffix.lower() in self.supported_formats]
            self.files.extend(valid_files)
            self.update_file_list()
            
            if len(valid_files) < len(files):
                self.log_to_file(f"⚠️ {len(files) - len(valid_files)} filer blev sprunget over (ikke understøttet format)")
    
    def clear_files(self):
        self.files = []
        self.update_file_list()
        self.log_to_file("🗑️ Filliste ryddet")
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            filename = os.path.basename(file)
            ext = Path(file).suffix.upper()
            self.file_listbox.insert(tk.END, f"{filename} [{ext}]")
        
        count = len(self.files)
        self.file_count_label.config(text=f"{count} fil{'er' if count != 1 else ''} valgt")
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Vælg output mappe")
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self.log_to_file(f"📁 Output mappe valgt: {folder}")
    
    def log_to_file(self, message):
        """Gem log til fil"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Kunne ikke skrive til log: {e}")
        
        # Opdater log vindue hvis det er åbent
        if self.log_window and self.log_window.winfo_exists():
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, log_message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
    
    def open_log_window(self):
        """Åbn log vindue"""
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            return
        
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Konverteringslog")
        self.log_window.geometry("700x400")
        
        # Toolbar
        toolbar = tk.Frame(self.log_window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(
            toolbar,
            text="🔄 Genindlæs",
            command=self.reload_log,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🗑️ Ryd log",
            command=self.clear_log,
            bg="#f44336",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📂 Åbn log fil",
            command=self.open_log_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        # Log text
        self.log_text = scrolledtext.ScrolledText(
            self.log_window,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Indlæs eksisterende log
        self.reload_log()
    
    def reload_log(self):
        """Genindlæs log fra fil"""
        if not self.log_window or not self.log_window.winfo_exists():
            return
        
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, "r", encoding="utf-8") as f:
                    self.log_text.insert(tk.END, f.read())
            else:
                self.log_text.insert(tk.END, "Ingen log endnu...\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Fejl ved indlæsning af log: {e}\n")
        
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def clear_log(self):
        """Ryd log fil"""
        if messagebox.askyesno("Bekræft", "Er du sikker på at du vil rydde hele loggen?"):
            try:
                with open(self.log_file_path, "w", encoding="utf-8") as f:
                    f.write("")
                self.reload_log()
                self.log_to_file("📋 Log ryddet")
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke rydde log: {e}")
    
    def open_log_file(self):
        """Åbn log fil i standard editor"""
        try:
            if os.path.exists(self.log_file_path):
                os.startfile(self.log_file_path)
            else:
                messagebox.showinfo("Info", "Log filen eksisterer ikke endnu")
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne log fil: {e}")
    
    def start_conversion(self):
        if not self.files:
            messagebox.showwarning("Ingen filer", "Vælg venligst nogle filer først!")
            self.log_to_file("⚠️ Konvertering afbrudt: Ingen filer valgt")
            return
        
        # Tjek output mappe hvis "anden" er valgt
        if self.output_location_var.get() == "anden":
            output_folder = self.output_entry.get()
            if not output_folder:
                messagebox.showwarning("Manglende mappe", "Vælg venligst en output mappe!")
                self.log_to_file("⚠️ Konvertering afbrudt: Ingen output mappe valgt")
                return
        
        if self.is_converting:
            messagebox.showinfo("Konverterer", "Konvertering er allerede i gang!")
            return
        
        # Kør konvertering i separat tråd
        thread = threading.Thread(target=self.convert_files, daemon=True)
        thread.start()
    
    def convert_files(self):
        self.is_converting = True
        self.convert_button.config(state='disabled', bg="#cccccc", text="⏳ KONVERTERER...")
        
        bitrate = self.bitrate_var.get()
        total_files = len(self.files)
        successful = 0
        failed = 0
        
        self.log_to_file(f"{'='*60}")
        self.log_to_file(f"🚀 Starter ny konvertering af {total_files} filer")
        self.log_to_file(f"⚙️ Bitrate: {bitrate}")
        
        for i, input_file in enumerate(self.files, 1):
            try:
                # Opdater UI
                self.status_label.config(
                    text=f"Konverterer: {os.path.basename(input_file)}",
                    fg="#FF9800"
                )
                self.progress_label.config(text=f"{i} / {total_files} filer")
                progress_value = (i / total_files) * 100
                self.progress['value'] = progress_value
                self.root.update_idletasks()
                
                # Bestem output mappe
                if self.output_location_var.get() == "samme":
                    output_folder = os.path.dirname(input_file)
                else:
                    output_folder = self.output_entry.get()
                    os.makedirs(output_folder, exist_ok=True)
                
                # Konverter fil
                filename = Path(input_file).stem
                output_file = os.path.join(output_folder, f"{filename}.mp3")
                
                self.log_to_file(f"[{i}/{total_files}] 🔄 {os.path.basename(input_file)} → {filename}.mp3")
                
                audio = AudioSegment.from_file(input_file)
                audio.export(output_file, format="mp3", bitrate=bitrate)
                
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                self.log_to_file(f"           ✅ Succes! ({file_size:.2f} MB)")
                successful += 1
                
            except Exception as e:
                self.log_to_file(f"           ❌ FEJL: {str(e)}")
                failed += 1
        
        # Færdig
        self.progress['value'] = 100
        self.status_label.config(
            text=f"✅ Færdig! {successful} succesfulde, {failed} fejlede",
            fg="#4CAF50" if failed == 0 else "#f44336"
        )
        
        self.log_to_file(f"{'='*60}")
        self.log_to_file(f"✅ Konvertering færdig!")
        self.log_to_file(f"   Succesfulde: {successful}")
        self.log_to_file(f"   Fejlede: {failed}")
        self.log_to_file(f"{'='*60}\n")
        
        self.convert_button.config(
            state='normal',
            bg="#FF9800",
            text="🚀 KONVERTER TIL MP3"
        )
        self.is_converting = False
        
        # Vis resultat dialog
        if failed == 0:
            messagebox.showinfo(
                "Succes!",
                f"Alle {successful} filer blev konverteret succesfuldt! 🎉"
            )
        else:
            messagebox.showwarning(
                "Delvis succes",
                f"Konvertering færdig:\n\n✅ {successful} succesfulde\n❌ {failed} fejlede\n\nTjek loggen for detaljer."
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConverterGUI(root)
    root.mainloop()