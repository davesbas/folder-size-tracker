import os
import tkinter as tk

from theme import BG, FG, DIM, FONT

class FolderPicker:
    def __init__(self, parent, initial_path, on_select):
        self.on_select = on_select
        self.current_path = os.path.abspath(initial_path)
        self.items = []

        self.window = tk.Toplevel(parent)
        self.window.title("Pilih Folder")
        self.window.geometry("700x480")
        self.window.configure(bg=BG)
        self.window.transient(parent)
        self.window.grab_set()

        self.window.bind(
            "<Escape>",
            lambda event: self.cancel()
        )

        tk.Label(
            self.window,
            text="SELECT TARGET DIRECTORY",
            bg=BG,
            fg=FG,
            font=("Consolas", 14, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.path_label = tk.Label(
            self.window,
            text="",
            bg=BG,
            fg=DIM,
            font=FONT,
            anchor="w",
        )
        self.path_label.pack(fill="x", padx=16, pady=(0, 8))

        frame = tk.Frame(self.window, bg=BG)
        frame.pack(fill="both", expand=True, padx=16)

        self.listbox = tk.Listbox(
            frame,
            bg="#061006",
            fg=FG,
            selectbackground=FG,
            selectforeground=BG,
            font=FONT,
            bd=1,
            relief="solid",
            highlightthickness=0,
            activestyle="none",
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        self.listbox.bind(
            "<Double-Button-1>",
            self.enter_selected
        )

        scrollbar = tk.Scrollbar(
            frame,
            command=self.listbox.yview,
        )
        scrollbar.pack(side="right", fill="y")

        self.listbox.config(
            yscrollcommand=scrollbar.set
        )

        buttons = tk.Frame(self.window, bg=BG)
        buttons.pack(fill="x", padx=16, pady=12)

        self.create_button(
            buttons,
            "[ UP ]",
            self.go_up,
        )

        self.create_button(
            buttons,
            "[ SELECT ]",
            self.select,
        )

        self.create_button(
            buttons,
            "[ CANCEL ]",
            self.cancel,
        )

        self.create_button(
            buttons,
            "[ DRIVES ]",
            self.show_drives,
        )

        self.refresh()

    def create_button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=BG,
            fg=FG,
            activebackground=FG,
            activeforeground=BG,
            font=FONT,
            bd=1,
            relief="solid",
            highlightthickness=0,
            padx=10,
        ).pack(side="left", padx=(0, 8))

    def get_drives(self):
        drives = []

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"

            if os.path.exists(drive):
                drives.append(drive)

        return drives


    def show_drives(self):
        self.current_path = None
        self.path_label.config(
            text="ALL AVAILABLE DRIVES"
    )

        self.listbox.delete(0, tk.END)
        self.items = self.get_drives()

        for drive in self.items:
            self.listbox.insert(
                tk.END,
                f"[DRIVE] {drive}",
        )

    def refresh(self):
        if self.current_path is None:
            self.show_drives()
            return

        self.path_label.config(
            text=self.current_path
        )

        self.listbox.delete(0, tk.END)
        self.items = []

        try:
            with os.scandir(self.current_path) as entries:
                self.items = sorted(
                    [
                        entry.path
                        for entry in entries
                        if entry.is_dir(
                            follow_symlinks=False
                        )
                    ],
                    key=lambda path: os.path.basename(
                        path
                    ).lower(),
             )

        except OSError:
            self.path_label.config(
                text="Folder tidak bisa dibaca"
            )
            return

        for path in self.items:
            self.listbox.insert(
                tk.END,
                f"[DIR] {os.path.basename(path)}",
            )

    def enter_selected(self, event=None):
        selection = self.listbox.curselection()

        if not selection:
            return

        selected_path = self.items[selection[0]]
        self.current_path = selected_path
        self.refresh()

    def go_up(self):
        if self.current_path is None:
            return

        parent = os.path.dirname(self.current_path)

        if parent == self.current_path:
            self.show_drives()
            return

        self.current_path = parent
        self.refresh()

    def select(self):
        if self.current_path is None:
            return

        self.on_select(self.current_path)
        self.window.destroy()

    def cancel(self):
        self.window.destroy()