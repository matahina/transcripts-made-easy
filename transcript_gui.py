
# This code was first AI-generated then highly reviewed by a human (me!) notably _update_ui_options() and build_ui()


import os
import sys
import threading
import queue
import contextlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from transcript_cli import *
import locale







TRANSLATIONS = {
    "fr": {"app_title":"Transcription AI",
"files":"Fichiers audio / vidéo",
"add_files":"Ajouter des fichiers",
"add_folder":"Ajouter un dossier",
"remove":"Supprimer",
"clear":"Vider",
"options":"Options",
"model":"Modèle :",
"parameters":"Paramètres :",
"cpu_only":"CPU uniquement",
"no_ffmpeg":"Sans FFmpeg",
"online_mode":"Mode online",
"int8":"Int8",
"beam_size":"Beam size :",
"language":"Langue :",
"generate_srt":"Générer SRT",
"translate_english":"Traduire vers l'anglais",
"prompt":"Prompt :",
"use_vocab":"Utiliser vocabulary.txt",
"start":"▶  Lancer la transcription",
"show_warnings":"Montrer warnings",
"log":"Journal",
"ui_language":"Langue de l'interface :",
"select_audio_video":"Sélectionner les fichiers audio/vidéo",
"audio_video":"Audio/Vidéo",
"all_files":"Tous les fichiers",
"select_folder":"Sélectionner un dossier",
"no_file_title":"Aucun fichier",
"no_file_message":"Ajoutez au moins un fichier audio ou vidéo.",
"done":"Terminé",
"transcription_error":"Erreur de transcription",
"ready":"Prêt",
"transcribing":"Transcription en cours...",
"english_only":"anglais uniquement"},

    "en": {"app_title":"Transcription AI",
"files":"Audio / video files",
"add_files":"Add files",
"add_folder":"Add folder",
"remove":"Remove",
"clear":"Clear",
"options":"Options",
"model":"Model:",
"parameters":"Parameters:",
"cpu_only":"CPU only",
"no_ffmpeg":"No FFmpeg",
"online_mode":"Online mode",
"int8":"Int8",
"beam_size":"Beam size:",
"language":"Language:",
"generate_srt":"Generate SRT",
"translate_english":"Translate to English",
"prompt":"Prompt:",
"use_vocab":"Use vocabulary.txt",
"start":"▶  Start transcription",
"show_warnings":"Show warnings",
"log":"Log",
"ui_language":"Interface language:",
"select_audio_video":"Select audio/video files",
"audio_video":"Audio/Video",
"all_files":"All files",
"select_folder":"Select a folder",
"no_file_title":"No file",
"no_file_message":"Add at least one audio or video file.",
"done":"Done",
"transcription_error":"Transcription error",
"ready":"Ready",
"transcribing":"Transcription in progress...",
"english_only":"English only"}
}

import mimetypes



class ToolTip:
    def __init__(self, widget, text, max_width=250):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.max_width = max_width
        # Binding mouse events
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return

        # Get actual mouse pointer position
        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 15

        # Create borderless tooltip window
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Customize text
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1,
                         # font=("normal"),
                         wraplength=self.max_width, justify="left")
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class TranscriptGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.ui_language_var = tk.StringVar(value="fr" if "fr" in locale.getlocale()[0] else "en")

        self.title(self.tr("app_title"))
        self.geometry("900x900")
        self.minsize(900, 900)

        self.files = []

        # Outputs from launch_transcript() are catched from this queue
        # so they can be shown later in Tkinter widget from main thread
        self.output_queue = queue.Queue()

        self.model_var = tk.StringVar(value="whisper")
        self.language_var = tk.StringVar(value="auto")
        self.whisper_size_var = tk.StringVar(value="turbo")
        self.beam_var = tk.IntVar(value=5)
        self.cpu_var = tk.BooleanVar(value=False)
        self.online_var = tk.BooleanVar(value=False)
        self.srt_var = tk.BooleanVar(value=False)
        self.int8_var = tk.BooleanVar(value=False)
        self.no_ffmpeg_var = tk.BooleanVar(value=False)
        self.translate_var = tk.BooleanVar(value=False)
        self.vocabulary_var = tk.BooleanVar(value=False)
        self.prompt_var = tk.StringVar()
        self.warnings = tk.BooleanVar(value=False)

        self._build_style()
        self._build_ui()
        self._update_ui_options()

        # Regularly check new outputs from transcription thread
        # then send them to log queue
        self.after(50, self._process_output_queue)

        # Human change! Put the thread in a var so you can access it
        # outside function it is started as daemon [start_transcription()]
        # so you can debug it elsewhere!
        self.da_thread = None

    def tr(self, key):
        return TRANSLATIONS[self.ui_language_var.get()].get(key, TRANSLATIONS["fr"].get(key, key))

    def _set_ui_language(self, *_):
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        self._update_ui_options()

    def _build_style(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Title.TLabel", font=("", 0 , "bold"))
        self.style.configure("Section.TLabelframe", padding=10)
        self.style.configure("Section.TLabelframe.Label", font=("", 0, "bold"))
        self.style.configure("Run.TButton", font=("", 0, "bold"), padding=8)

    def _select_all_text(self, event):
        # Add selection from very start ('1.0') until the very last ('end')
        event.widget.tag_add("sel", "1.0", "end")
        # Optional : put cursor at the end of selected text
        event.widget.mark_set("insert", "end")
        # Stop default Tkinter behavior
        return "break"

    def _build_ui(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        self.status_bar = tk.Label(
            root,
            text=self.tr("ready"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5,
            pady=2
        )

        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        ui_lang = ttk.Frame(root)
        ui_lang.pack(fill="x", pady=(0, 8))
        ttk.Combobox(ui_lang, textvariable=self.ui_language_var, values=list(TRANSLATIONS), state="readonly", width=8).pack(side="right", padx=8)
        ui_lang.winfo_children()[-1].bind("<<ComboboxSelected>>", self._set_ui_language)
        ttk.Label(ui_lang, text=self.tr("ui_language"), style="Section.TLabelframe.Label").pack(side="right")

        self.magic_background = self.style.lookup("TFrame", "background")

        files_box = ttk.LabelFrame(
            root, text=self.tr("files"), style="Section.TLabelframe"
        )
        files_box.pack(fill="both"
                       # , expand=True
                       )

        list_frame = ttk.Frame(files_box)
        list_frame.pack(fill="both"
                        # , expand=True
                        )

        self.file_list = tk.Listbox(
            list_frame, selectmode=tk.EXTENDED, height=4
        )
        self.file_list.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.file_list.yview
        )
        scroll.pack(side="right", fill="y")
        self.file_list.config(yscrollcommand=scroll.set)

        buttons = ttk.Frame(files_box)
        buttons.pack(fill="x", pady=(8, 0))

        ttk.Button(buttons, text=self.tr("add_files"), command=self.add_files).pack(
            side="left"
        )
        ttk.Button(buttons, text=self.tr("add_folder"), command=self.add_folder).pack(
            side="left", padx=6
        )
        ttk.Button(buttons, text=self.tr("remove"), command=self.remove_selected).pack(
            side="left"
        )
        ttk.Button(buttons, text=self.tr("clear"), command=self.clear_files).pack(
            side="left", padx=6
        )

        ###################
        ################### "OPTIONS" FRAME
        ###################

        options = ttk.LabelFrame(
            root, text=self.tr("options"), style="Section.TLabelframe"
        )
        # options.pack(fill="x", pady=12)
        options.pack(fill="both", expand=True, pady=12)

        grid = ttk.Frame(options)
        # grid.pack(fill="x")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(4, weight=1)
        grid.rowconfigure(7, weight=1)

        ################### "MODEL" SECTION

        ttk.Label(grid, text=self.tr("model"), style="Section.TLabelframe.Label").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_combo = ttk.Combobox(
            grid, textvariable=self.model_var, values=the_models, state="readonly", width=16
        )
        self.model_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.model_combo.bind("<<ComboboxSelected>>", lambda e: self._update_ui_options())

        hrule = ttk.Separator(grid, orient="horizontal")
        hrule.grid(row=1, column=0, columnspan=5, sticky="ew", pady=10)

        ################### "PARAMS" SECTION

        ttk.Label(grid, text=self.tr("parameters"), style="Section.TLabelframe.Label").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.param_combo = ttk.Combobox(
            grid, textvariable=self.whisper_size_var,
            values=whisper_models, state="readonly", width=16
        )
        self.param_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.param_combo.bind("<<ComboboxSelected>>", lambda e: self._update_ui_options())

        ttk.Checkbutton(grid, text=self.tr("cpu_only"), variable=self.cpu_var).grid(
            row=2, column=2, sticky="w", padx=5, pady=5
        )
        ttk.Checkbutton(grid, text=self.tr("no_ffmpeg"), variable=self.no_ffmpeg_var,
            command=lambda: self._update_ui_options()).grid(
            row=2, column=3, sticky="w", padx=5, pady=5
        )
        self.allow_online = ttk.Checkbutton(grid, text=self.tr("online_mode"), variable=self.online_var)

        self.allow_online.grid(
            row=2, column=4, sticky="w", padx=5, pady=5
        )

        self.superquantif = ttk.Checkbutton(grid, text=self.tr("int8"), variable=self.int8_var)
        self.superquantif.grid(
            row=3, column=2, sticky="w", padx=5, pady=5
        )

        beam_frame = ttk.Frame(grid)
        beam_frame.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(
            beam_frame,
            text=self.tr("beam_size")
            ).pack(side="left")

        self.beam_size = ttk.Spinbox(
            beam_frame,
            from_=1,
            to=10,
            textvariable=self.beam_var,
            width=4
        )
        self.beam_size.pack(side="left")

        hrule = ttk.Separator(grid, orient="horizontal")
        hrule.grid(row=4, column=0, columnspan=5, sticky="ew", pady=10)

        ################### "LANGUAGE" SECTION

        ttk.Label(grid, text=self.tr("language"), style="Section.TLabelframe.Label").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.language_combo = ttk.Combobox(
            grid, textvariable=self.language_var,
            values=["auto"], width=16
        )
        self.language_combo.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        ToolTip(self.language_combo, "text")

        self.srt_check = ttk.Checkbutton(
            grid,
            text=self.tr("generate_srt"),
            variable=self.srt_var,
            command=lambda: self._update_ui_options()
        )
        self.srt_check.grid(
            row=5, column=2, sticky="w", padx=5, pady=5
            )

        self.translate_button = ttk.Checkbutton(
            grid,
            text=self.tr("translate_english"),
            variable=self.translate_var)
        self.translate_button.grid(
            row=5, column=3, sticky="w", padx=5, pady=5
        )

        hrule = ttk.Separator(grid, orient="horizontal")
        hrule.grid(row=6, column=0, columnspan=5, sticky="ew", pady=10)

        ################### "PROMPT" SECTION

        self.prompt_text = tk.Text(grid, height=8
                                   # , width=65
                                   )
        self.prompt_text.grid(
            row=7, column=1, columnspan=4, sticky="nsew", padx=5, pady=5
        )

        self.original_color = self.prompt_text.cget("background")

        self.prompt_text.bind("<Control-a>", self._select_all_text)
        self.prompt_text.bind("<Control-A>", self._select_all_text)

        scroll_p = ttk.Scrollbar(
            self.prompt_text, orient="vertical", command=self.prompt_text.yview
        )
        scroll_p.pack(side="right", fill="y")
        self.prompt_text.config(yscrollcommand=scroll_p.set)

        self.vocab_use = ttk.Checkbutton(
            grid, text=self.tr("use_vocab"),
            variable=self.vocabulary_var
        )
        self.vocab_use.grid(row=8, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        ttk.Label(grid, text=self.tr("prompt"), style="Section.TLabelframe.Label").grid(
            row=7, column=0, sticky="nw", padx=5, pady=5
        )


        ###################
        ################### "ACTION" FRAME
        ###################

        action_frame = ttk.Frame(root)
        action_frame.pack(fill="x", pady=(0, 10))

        self.run_button = ttk.Button(
            action_frame, text=self.tr("start"),
            style="Run.TButton", command=self.start_transcription
        )
        self.run_button.pack(side="left")



        ttk.Checkbutton(
            action_frame,
            text=self.tr("show_warnings"),
            variable=self.warnings
        ).pack(side="right")

        output_box = ttk.LabelFrame(
            root, text=self.tr("log"), style="Section.TLabelframe"
        )
        output_box.pack(fill="both", expand=True)

        self.log = tk.Text(
            output_box, height=5, wrap="word", state="disabled"
        )
        self.log.pack(side="left", fill="both", expand=True)

        log_scroll = ttk.Scrollbar(
            output_box, orient="vertical", command=self.log.yview
        )
        log_scroll.pack(side="right", fill="y")
        self.log.config(yscrollcommand=log_scroll.set)

    def _update_ui_options(self):

        self.files = check_files(self.files, self.no_ffmpeg_var.get(), False)
        self.file_list.delete(0, "end")
        if self.files != []:
            for path in self.files:
                self.file_list.insert("end", path)

        model = self.model_var.get()

        if "whisper" in model:
            self.vocab_use.configure(state="normal")
            self.prompt_text.configure(state="normal", bg = self.original_color)
            self.allow_online.configure(state="normal")
            self.online_var.set(False)
            the_values = ["auto"] + the_languages["whisper"]
            ToolTip(self.language_combo, the_helps["whisper"])
            self.beam_size.configure(state="readonly")
            self.beam_size.set(self.beam_size.get() if self.beam_size.get() in self.beam_size["values"] else 5)
            self.translate_button.configure(state="normal")
            self.superquantif.configure(state="normal")
            self.param_combo.configure(
                values = whisper_models,
                state="readonly",
                )
            self.param_combo.set(self.param_combo.get() if self.param_combo.get() in self.param_combo["values"] else "turbo")
            if not "faster" in model:
                self.allow_online.configure(state="disabled")
                self.online_var.set(False)
                self.superquantif.configure(state="disabled")
                self.int8_var.set(False)
                self.param_combo.configure(
                    values = [x for x in whisper_models if "distil" not in x],
                    state="readonly",
                    )
                self.param_combo.set(self.param_combo.get() if self.param_combo.get() in self.param_combo["values"] else self.param_combo["values"][0])
            if "-afr" in model:
                self.allow_online.configure(state="disabled")
                self.online_var.set(True)
                self.superquantif.configure(state="normal")
                self.translate_button.configure(state="disabled")
                self.translate_var.set(False)
                the_values= the_languages["whisper-afr"]
                self.param_combo.configure(
                    values = ["large"],
                    state="disabled",
                    )
                self.param_combo.set(self.param_combo["values"][0])
                ToolTip(self.language_combo, the_helps["whisper-afr"])
            if "distil" in self.param_combo.get():
                self.translate_button.configure(state="disabled")
                self.translate_var.set(False)
                the_values=["en"]
                ToolTip(self.language_combo, self.tr("english_only"))
        elif "qwen3" in model:
            self.vocab_use.configure(state="normal")
            self.prompt_text.configure(state="normal", bg = self.original_color)
            self.allow_online.configure(state="normal")
            self.online_var.set(False)
            self.superquantif.configure(state="disabled")
            self.int8_var.set(False)
            self.translate_button.configure(state="disabled")
            self.translate_var.set(False)
            the_values = ["auto"] + the_languages["qwen3"]
            if self.srt_var.get():
                the_values = ["auto"] + the_languages["qwen3_srt"]
            ToolTip(self.language_combo, the_helps["qwen3"])
            self.beam_size.configure(state="readonly")
            self.beam_size.set(self.beam_size.get() if self.beam_size.get() in self.beam_size["values"] else 1)
            self.param_combo.configure(
                values = ["0.6", "1.7"],
                state="readonly",
                )
            self.param_combo.set(self.param_combo.get() if self.param_combo.get() in self.param_combo["values"] else self.param_combo["values"][0])


        elif "nemotron" in model:
            self.vocab_use.configure(state="disabled")
            self.vocabulary_var.set(False)
            self.prompt_text.configure(state="disabled", bg=self.magic_background)
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.configure(state="disabled")
            self.allow_online.configure(state="normal")
            self.online_var.set(False)
            self.superquantif.configure(state="disabled")
            self.int8_var.set(False)
            self.translate_button.configure(state="disabled")
            self.translate_var.set(False)
            ToolTip(self.language_combo, the_helps["nemotron"])
            the_values = ["auto"] + the_languages["nemotron"]
            self.beam_size.configure(state="disabled")
            self.beam_size.set(0)
            self.param_combo.configure(
                values = ["None"],
                state="disabled",
                )
            self.param_combo.set(self.param_combo["values"][0])
            if "-en" in model:
                the_values = ["en"]
                ToolTip(self.language_combo, self.tr("english_only"))
        else:
            self.vocab_use.configure(state="disabled")
            self.vocabulary_var.set(False)
            self.prompt_text.configure(state="disabled", bg=self.magic_background)
            self.prompt_text.delete("1.0", tk.END)
            self.allow_online.configure(state="normal")
            self.online_var.set(False)
            self.superquantif.configure(state="disabled")
            self.int8_var.set(False)
            self.translate_button.configure(state="disabled")
            self.translate_var.set(False)
            ToolTip(self.language_combo, the_helps["parakeet"])
            self.beam_size.configure(state="disabled")
            self.beam_size.set(0)
            self.param_combo.configure(
                values = ["None"],
                state="disabled",
                )
            self.param_combo.set(self.param_combo["values"][0])
            the_values = ["auto"]
        self.language_combo.configure(
            values = the_values,
            state="disabled" if any(char_key in model for char_key in ["distil","parakeet"]) or "-en" in model else "readonly"
            )
        aa = self.language_combo.get()
        self.language_combo.set(self.language_combo.get() if self.language_combo.get() in the_values else the_values[0])
        bb = self.language_combo.get()
        if aa != bb:
            self.language_combo.focus_set()
        if ".en" in self.param_combo.get():
            self.translate_button.configure(state="disabled")
            self.translate_var.set(False)

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title=self.tr("select_audio_video"),
            filetypes=[
                (self.tr("audio_video"), "*"+" *".join(da_list) if not self.no_ffmpeg_var.get() else "*"+" *".join(da_list_no_ffmpeg) ),
                (self.tr("all_files"), "*.*"),
            ],
        )

        paths = check_files(paths, self.no_ffmpeg_var.get(), False)

        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.file_list.insert("end", path)

    def add_folder(self):
        folder = filedialog.askdirectory(title=self.tr("select_folder"))
        if not folder:
            return

        extensions = set(da_list) if not self.no_ffmpeg_var.get() else set(da_list_no_ffmpeg)

        for path in sorted(Path(folder).iterdir()):
            if path.is_file() and path.suffix.lower() in extensions:
                path = str(path)
                if path not in self.files:
                    self.files.append(path)
                    self.file_list.insert("end", path)

    def remove_selected(self):
        selected = list(self.file_list.curselection())
        for index in reversed(selected):
            self.file_list.delete(index)
            del self.files[index]

    def clear_files(self):
        self.files.clear()
        self.file_list.delete(0, "end")

    def _process_output_queue(self):
        """Show in log the outputs from launch_transcript()."""
        try:
            while True:
                text = self.output_queue.get_nowait()
                if text:
                    self.log_write(text)
        except queue.Empty:
            pass

        # We keep on looking for queue while app is open.
        self.after(50, self._process_output_queue)

    def _capture_output(self):
        """Returns contextlib.redirect_stdout/stderr compatible writer"""
        gui = self

        class QueueWriter:
            def write(self, text):
                if text:
                    gui.output_queue.put(text)
                return len(text) if text else 0

            def flush(self):
                pass

            def isatty(self):
                return False

        return QueueWriter()

    def log_write(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")

    def start_transcription(self):
        if not self.files:
            messagebox.showwarning(self.tr("no_file_title"), self.tr("no_file_message"))
            return

        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        self.run_button.config(state="disabled")
        self.status_bar.configure(text=self.tr("transcribing"))
        self.da_flag = True
        self.da_thread = threading.Thread(target=self._run_transcription, daemon=True)
        self.da_thread.start()

    def _run_transcription(self):
        da_error = None
        try:
            model = self.model_var.get()
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            params = self.param_combo.get()
            prompt = self.prompt_text.get("1.0", "end").strip() or None

            the_language_whisper_afr = None
            the_language_whisper = None
            the_language_nemotron = None
            the_language_qwen3 = None
            whisper_params = None
            qwen3_params = None

            if "whisper-afr" in model:
                the_language_whisper_afr = language
            elif "whisper" in model:
                the_language_whisper = language
                whisper_params = params
            elif "nemotron" in model:
                the_language_nemotron = language
            elif "qwen3" in model:
                the_language_qwen3 = language
                qwen3_params = params

            # launch_transcript() uses print() to communicate its progress.
            # We send stdout et stderr to queue so those messages
            # are shown directly in interface log area.
            gui_output = self._capture_output()

            with contextlib.redirect_stdout(gui_output), contextlib.redirect_stderr(gui_output):
                launch_transcript(
                    model, self.files, the_language_whisper, the_language_whisper_afr,
                    the_language_nemotron, the_language_qwen3,
                    whisper_params, qwen3_params, self.translate_var.get(),
                    self.cpu_var.get(), self.int8_var.get(), self.no_ffmpeg_var.get(),
                    self.beam_var.get(), self.srt_var.get(), self.online_var.get(),
                    prompt, self.vocabulary_var.get(), self.warnings.get(), False
                )
        except Exception as exc:
            da_error = exc

        finally:
            if da_error is None:
                self.after(0, self._finished, self.tr("done"))
            else:
                full_details = str(da_error) or da_error.__class__.__name__
                self.after(0, self._finished, f"Erreur : {full_details}")
                self.after(
                    0,
                    lambda details=full_details: messagebox.showerror(
                        self.tr("transcription_error"),
                        details
                    )
                )

    def _finished(self, message):
        self.run_button.config(state="normal")
        self.status_bar.configure(text=message)
        self.log_write(f"\n--- {message} ---\n")
        # print("Alive: ",self.da_thread.is_alive())


if __name__ == "__main__":
    app = TranscriptGUI()
    app.mainloop()
