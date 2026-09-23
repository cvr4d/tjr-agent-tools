#!/usr/bin/env python3
"""
TJR Agent Tools - GUI
A simple graphical interface for all TJR tools.
"""

import os
import sys
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:
    print("Error: customtkinter not installed.")
    print("Install with: pip install customtkinter")
    sys.exit(1)


# ============ CONFIG ============
APP_TITLE = "TJR Agent Tools"
APP_SIZE = "1100x750"

# Colors
COLOR_BG = "#1a1a1a"
COLOR_CARD = "#2b2b2b"
COLOR_ACCENT = "#1f6aa5"
COLOR_SUCCESS = "#2fa572"
COLOR_ERROR = "#c0392b"
COLOR_TEXT = "#e0e0e0"
COLOR_MUTED = "#888888"
# ================================


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TJRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(900, 600)

        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.build_header()

        # Tabview
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLOR_CARD,
            segmented_button_fg_color=COLOR_BG,
            segmented_button_selected_color=COLOR_ACCENT,
        )
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.tab_context = self.tabview.add("🔍 Exact Search")
        self.tab_fuzzy = self.tabview.add("🔎 Fuzzy Search")
        self.tab_sub = self.tabview.add("📝 Generate Subtitles")
        self.tab_frame = self.tabview.add("🎬 Add Frame")

        self.build_context_tab()
        self.build_fuzzy_tab()
        self.build_sub_tab()
        self.build_frame_tab()

        # Status bar
        self.status = ctk.CTkLabel(
            self, text="Ready", anchor="w",
            font=ctk.CTkFont(size=12), text_color=COLOR_MUTED
        )
        self.status.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

    # ==========================================
    # HEADER
    # ==========================================
    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=70)
        header.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header, text="🎯 TJR Agent Tools",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLOR_TEXT
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header, text="Search, generate, and process YouTube subtitles",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_MUTED
        )
        subtitle.grid(row=1, column=0, sticky="w")

    # ==========================================
    # HELPER: Run command in background
    # ==========================================
    def run_tool(self, cmd, output_box, status_msg="Working..."):
        output_box.delete("1.0", "end")
        output_box.insert("end", f"⏳ {status_msg}\n\n")
        self.set_status(status_msg)

        def worker():
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    cwd=str(Path(__file__).parent),
                )
                output = result.stdout

                self.after(0, lambda: self.display_output(output_box, output))
                self.after(0, lambda: self.set_status("✅ Done"))
            except FileNotFoundError as e:
                self.after(0, lambda: self.display_output(
                    output_box, f"❌ Error: {e}\n\nIs Python in PATH?"
                ))
                self.after(0, lambda: self.set_status("❌ Failed"))
            except Exception as e:
                self.after(0, lambda: self.display_output(
                    output_box, f"❌ Error: {e}"
                ))
                self.after(0, lambda: self.set_status("❌ Failed"))

        threading.Thread(target=worker, daemon=True).start()

    def display_output(self, output_box, text):
        output_box.delete("1.0", "end")
        output_box.insert("end", text if text.strip() else "(no output)")
        output_box.see("end")

    def set_status(self, msg):
        self.status.configure(text=msg)

    def get_python(self):
        """Return the Python executable path (venv if available)."""
        base = Path(__file__).parent
        if sys.platform == "win32":
            venv_py = base / "venv" / "Scripts" / "python.exe"
        else:
            venv_py = base / "venv" / "bin" / "python"

        if venv_py.exists():
            return str(venv_py)
        return sys.executable

    def make_output_box(self, parent):
        box = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            fg_color=COLOR_BG,
        )
        return box

    # ==========================================
    # TAB 1: EXACT SEARCH
    # ==========================================
    def build_context_tab(self):
        tab = self.tab_context
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(4, weight=1)

        # Title
        ctk.CTkLabel(
            tab, text="Exact phrase search in subtitle files",
            font=ctk.CTkFont(size=14), text_color=COLOR_MUTED
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Input
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame, text="Phrase:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.context_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text='e.g. "fair value gap"',
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.context_entry.grid(row=0, column=1, sticky="ew")

        # Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(
            btn_frame, text="▶  Search", width=140, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            command=self.run_context_search
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="🗑  Clear", width=100, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="gray30",
            command=lambda: self.clear_tab(self.context_entry, self.context_output)
        ).grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="📂  Open Subtitles Folder", width=200, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="gray30",
            command=self.open_subtitles_folder
        ).grid(row=0, column=2)

        # Output label
        ctk.CTkLabel(
            tab, text="Results:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")

        # Output box
        self.context_output = self.make_output_box(tab)
        self.context_output.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="nsew")

    def run_context_search(self):
        query = self.context_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty", "Please enter a search phrase.")
            return
        cmd = [self.get_python(), "tjr_context.py", query]
        self.run_tool(cmd, self.context_output, f"Searching for: {query}")

    # ==========================================
    # TAB 2: FUZZY SEARCH
    # ==========================================
    def build_fuzzy_tab(self):
        tab = self.tab_fuzzy
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            tab, text="Fuzzy search — finds similar phrases even with typos",
            font=ctk.CTkFont(size=14), text_color=COLOR_MUTED
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame, text="Phrase:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.fuzzy_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text='e.g. "fair value gapp"',
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.fuzzy_entry.grid(row=0, column=1, sticky="ew")

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(
            btn_frame, text="▶  Search", width=140, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            command=self.run_fuzzy_search
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="🗑  Clear", width=100, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="gray30",
            command=lambda: self.clear_tab(self.fuzzy_entry, self.fuzzy_output)
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            tab, text="Results:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")

        self.fuzzy_output = self.make_output_box(tab)
        self.fuzzy_output.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="nsew")

    def run_fuzzy_search(self):
        query = self.fuzzy_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty", "Please enter a search phrase.")
            return
        cmd = [self.get_python(), "tjr_fuzzy.py", query]
        self.run_tool(cmd, self.fuzzy_output, f"Fuzzy searching: {query}")

    # ==========================================
    # TAB 3: GENERATE SUBTITLES
    # ==========================================
    def build_sub_tab(self):
        tab = self.tab_sub
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            tab, text="Generate SRT subtitles from any video/audio file",
            font=ctk.CTkFont(size=14), text_color=COLOR_MUTED
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # File picker
        file_frame = ctk.CTkFrame(tab, fg_color="transparent")
        file_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            file_frame, text="Video:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.sub_file_entry = ctk.CTkEntry(
            file_frame,
            placeholder_text="Select a video/audio file...",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.sub_file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            file_frame, text="📂  Browse", width=100, height=40,
            font=ctk.CTkFont(size=13),
            command=self.browse_video_file
        ).grid(row=0, column=2)

        # Options
        options_frame = ctk.CTkFrame(tab, fg_color="transparent")
        options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(
            options_frame, text="Max words per line:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.sub_words_var = tk.StringVar(value="4")
        words_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "10"],
            variable=self.sub_words_var,
            width=100, height=35,
            font=ctk.CTkFont(size=13),
        )
        words_menu.grid(row=0, column=1, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(
            btn_frame, text="▶  Generate", width=160, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            command=self.run_sub
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="🗑  Clear", width=100, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="gray30",
            command=lambda: self.clear_tab(self.sub_file_entry, self.sub_output)
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            tab, text="Output:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")

        self.sub_output = self.make_output_box(tab)
        self.sub_output.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="nsew")

    def browse_video_file(self):
        path = filedialog.askopenfilename(
            title="Select video/audio file",
            filetypes=[
                ("Video/Audio", "*.mp4 *.mkv *.avi *.mov *.webm *.mp3 *.wav *.m4a"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.sub_file_entry.delete(0, "end")
            self.sub_file_entry.insert(0, path)

    def run_sub(self):
        video = self.sub_file_entry.get().strip()
        if not video:
            messagebox.showwarning("Empty", "Please select a video file.")
            return
        if not Path(video).exists():
            messagebox.showerror("Not found", f"File not found:\n{video}")
            return
        words = self.sub_words_var.get()
        cmd = [self.get_python(), "sub.py", video, words]
        self.run_tool(cmd, self.sub_output, f"Generating subtitles for: {Path(video).name}")

    # ==========================================
    # TAB 4: ADD FRAME
    # ==========================================
    def build_frame_tab(self):
        tab = self.tab_frame
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            tab, text="Add rounded corners + black frame around a video",
            font=ctk.CTkFont(size=14), text_color=COLOR_MUTED
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # File picker
        file_frame = ctk.CTkFrame(tab, fg_color="transparent")
        file_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            file_frame, text="Video:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.frame_file_entry = ctk.CTkEntry(
            file_frame,
            placeholder_text="Select a video file...",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.frame_file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            file_frame, text="📂  Browse", width=100, height=40,
            font=ctk.CTkFont(size=13),
            command=self.browse_frame_file
        ).grid(row=0, column=2)

        # Output name (optional)
        out_frame = ctk.CTkFrame(tab, fg_color="transparent")
        out_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        out_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            out_frame, text="Output name (optional):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.frame_output_entry = ctk.CTkEntry(
            out_frame,
            placeholder_text="Leave empty for auto-name",
            height=35,
            font=ctk.CTkFont(size=13),
        )
        self.frame_output_entry.grid(row=0, column=1, sticky="ew")

        # Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(
            btn_frame, text="▶  Process", width=160, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            command=self.run_frame
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="🗑  Clear", width=100, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="gray30",
            command=lambda: self.clear_tab(self.frame_file_entry, self.frame_output)
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            tab, text="Output:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")

        self.frame_output = self.make_output_box(tab)
        self.frame_output.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="nsew")

    def browse_frame_file(self):
        path = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[
                ("Video", "*.mp4 *.mkv *.avi *.mov *.webm"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.frame_file_entry.delete(0, "end")
            self.frame_file_entry.insert(0, path)

    def run_frame(self):
        video = self.frame_file_entry.get().strip()
        if not video:
            messagebox.showwarning("Empty", "Please select a video file.")
            return
        if not Path(video).exists():
            messagebox.showerror("Not found", f"File not found:\n{video}")
            return
        output = self.frame_output_entry.get().strip()
        cmd = [self.get_python(), "frame.py", video]
        if output:
            cmd.append(output)
        self.run_tool(cmd, self.frame_output, f"Processing: {Path(video).name}")

    # ==========================================
    # HELPERS
    # ==========================================
    def clear_tab(self, entry, output):
        if hasattr(entry, "delete"):
            entry.delete(0, "end")
        output.delete("1.0", "end")
        self.set_status("Ready")

    def open_subtitles_folder(self):
        subdir = os.environ.get("TJR_SUBTITLES", str(Path.home() / "TJR_SUBTITLES"))
        if not Path(subdir).exists():
            messagebox.showerror("Not found", f"Folder does not exist:\n{subdir}")
            return
        if sys.platform == "win32":
            os.startfile(subdir)
        elif sys.platform == "darwin":
            subprocess.run(["open", subdir])
        else:
            subprocess.run(["xdg-open", subdir])


def main():
    app = TJRApp()
    app.mainloop()


if __name__ == "__main__":
    main()

