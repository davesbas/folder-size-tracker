import os 
import queue
import threading
import tkinter as tk

from scanner import scan, format_size, make_bar
from theme import BG, FG, DIM, FONT
from folder_picker import FolderPicker

class MainApp:
    def __init__(self, root):
        self.root = root
        root.title("Disk Analyzer")
        root.geometry("860x580")
        root.configure(bg=BG)

        self.text = tk.Text(
            root, bg=BG, fg=FG, font=FONT, bd=0, highlightthickness=0,
            wrap="none", padx=16, pady=8, cursor="arrow", state="disabled", 
            height=12,
        )
        self.text.pack(fill="x")
        self.text.tag_config("body", foreground=FG)
        self.text.tag_config("cursor", foreground=FG)

        self.listbox = tk.Listbox(
            root, bg=BG, fg=FG, font=FONT, bd=0, highlightthickness=0,
            selectbackground=FG, selectforeground=BG, activestyle="none",
            exportselection=False,
        )
        self.listbox.pack(fill="both", expand=True, padx=16, pady=(0,8))

        self.status = tk.Label(root, text="", bg=BG, fg=DIM, font=FONT, anchor="w")
        self.status.pack(fill="x", padx=16)
        nav = tk.Frame(root, bg=BG)
        nav.pack(fill="x", padx=16, pady=(0,4), before=self.listbox)
        self.btn_up = self._button(nav, "[ UP ]", self.go_up)
        self._button(nav, "[ REFRESH ]", self.refresh_current)
        self._button(nav, "[ CLEAR ]", self.clear_log)

        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", padx=16, pady=(4,12))
        self._button(
            bar,
            "[1] PINDAI",
            self.start_scan,
        )

        self._button(
            bar,
            "[2] FILE TERBESAR",
            self.show_unavailable,
        )

        self._button(
            bar,
            "[3] EKSPOR CSV",
            self.show_unavailable,
        )

        self._button(
            bar,
            "[0] KELUAR",
            root.destroy,
        )

        self.text.config(state="normal")
        self.text.insert("end", "█", "cursor")
        self.text.config(state="disabled")

        self.pending = ""
        self.cursor_on = True
        self.busy = False
        self.events = queue.Queue()
        self.root_path = None
        self.current_path = None
        self.items = []
        self.cache = {}

        root.bind("1", lambda e: self.start_scan())
        root.bind("2", lambda e: self.show_unavailable())
        root.bind("3", lambda e: self.show_unavailable())
        root.bind("0", lambda e: root.destroy())

        self.listbox.bind("<Return>", self.enter_selected)
        self.listbox.bind("<Double-Button-1>", self.enter_selected)
        self.listbox.bind("<BackSpace>", self.go_up)

        self.show_clickable_menu()
        self._type_tick()
        self._blink()
        self._poll()

    def _button(self, parent, label, command):
        btn = tk.Button(
            parent, text=label, command=command, cursor="hand2",bg=BG, fg=FG, 
            font=FONT, activebackground=FG, activeforeground=BG, bd=1, relief="solid",
            highlightthickness=0, padx=10, disabledforeground=DIM,
        )
        btn.pack(side="left", padx=(0, 8))
        return btn

    def say(self, message):
        self.pending += message

    def _type_tick(self):
        if self.pending:
            chunk, self.pending = self.pending[:3], self.pending[3:]
            self.text.config(state="normal")
            self.text.insert("end-2c", chunk, "body")
            self.text.config(state="disabled")
            self.text.see("end")
        self.root.after(10, self._type_tick)

    def _blink(self):
        self.cursor_on = not self.cursor_on
        self.text.tag_config("cursor", foreground=FG if self.cursor_on else BG)
        self.root.after(500, self._blink)

    def start_scan(self):
        if self.busy:
            return

        FolderPicker(
            self.root,
            os.getcwd(),
            self.folder_selected,
    )


    def folder_selected(self, folder):
        folder = os.path.normpath(folder)
        self.root_path = folder
        self.cache = {}
        self.busy = True
        self.say(f"\n> Memindai {folder}\n")

        threading.Thread(
            target=self._worker,
            args=(folder,),
            daemon=True,
    ).start()

    def _worker(self, folder):
        results = scan(folder, on_progress=lambda name: self.events.put(("progress", name)))
        self.events.put(("done", folder, results))

    def _poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    self.status.config(text=f"SCANNING... {event[1][:50]}")
                else:
                    self._show_results(event[1], event[2])
        except queue.Empty:
            pass
        self.root.after(100, self._poll)

    def _show_results(self, folder, results):
        self.busy = False
        self.status.config(text=folder)
        self._fill_list(folder, results)
        if not results:
            self.say("> FOLDER KOSONG ATAU AKSES DITOLAK\n")

    def _fill_list(self, folder, results):
        self.current_path = folder
        self.items = results
        self.cache[folder] = results
        self.listbox.delete(0, "end")
        total = sum(size for _, size in results) or 1
        for path, size in results:
            pct = size/total * 100
            mark = "/" if os.path.isdir(path) else ""
            name = os.path.basename(path) + mark
            self.listbox.insert(
                "end", f"{format_size(size):>10} {make_bar(pct, 15)} {pct:5.1f}% {name}"
            )
        if results:
            self.listbox.selection_set(0)
        self.listbox.focus_set()

    def open_folder(self, path):
        if path in self.cache:
            self._fill_list(path, self.cache[path])
            self.status.config(text=path)
        elif not self.busy:
            self.busy = True
            threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def enter_selected(self, event=None):
        sel = self.listbox.curselection()
        if sel and os.path.isdir(self.items[sel[0]][0]):
            self.open_folder(self.items[sel[0]][0])

    def go_up(self, event=None):
        if self.current_path and self.current_path != self.root_path:
            self.open_folder(os.path.dirname(self.current_path))

    def refresh_current(self, event=None):
        if self.busy or not self.current_path:
            return
        self.cache.pop(self.current_path, None)
        self.open_folder(self.current_path)

    def clear_log(self, event=None):
        self.pending = ""
        self.show_clickable_menu()

    def _update_nav(self):
        can_up = self.current_path and self.current_path != self.root_path
        self.btn_up.config(state="normal" if can_up else "disabled")

    def show_unavailable(self):
        self.say(
            "\n> FITUR INI BELUM TERSEDIA\n"
    )

    def show_clickable_menu(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)

        self.text.insert(
            tk.END,
            "=====================================\n"
            "   TERMINAL DISK ANALYZER\n"
            "   TERMINAL v1.0\n"
            "=====================================\n\n",
            "body",
        )

        self.text.insert(
            tk.END,
            "[1] PINDAI FOLDER\n",
            "menu_scan",
        )

        self.text.insert(
            tk.END,
            "[2] FILE TERBESAR\n",
            "menu_largest",
        )

        self.text.insert(
            tk.END,
            "[3] EKSPOR CSV\n",
            "menu_export",
        )

        self.text.insert(
            tk.END,
            "[0] KELUAR\n",
            "menu_exit",
        )

        self.text.insert(
            tk.END,
            "\n",
            "body",
        )

        self.text.insert(
            tk.END,
            "█",
            "cursor",
        )

        for tag in (
            "menu_scan",
            "menu_largest",
            "menu_export",
            "menu_exit",
        ):
            self.text.tag_config(
                tag,
                foreground=FG,
                background=BG,
                underline=False,
            )

            self.text.tag_bind(
                tag,
                "<Enter>",
                lambda event, current_tag=tag: (
                    self.text.tag_config(
                        current_tag,
                        foreground=BG,
                        background=FG,
                        underline=False,
                    ),
                    self.text.config(cursor="hand2"),
                ),
            )

            self.text.tag_bind(
                tag,
                "<Leave>",
                lambda event, current_tag=tag: (
                    self.text.tag_config(
                        current_tag,
                        foreground=FG,
                        background=BG,
                        underline=False,
                    ),
                    self.text.config(cursor="arrow"),
                ),
            )

        self.text.tag_bind(
            "menu_scan",
            "<Button-1>",
            lambda event: self.start_scan(),
        )

        self.text.tag_bind(
            "menu_largest",
            "<Button-1>",
            lambda event: self.show_unavailable(),
        )

        self.text.tag_bind(
            "menu_export",
            "<Button-1>",
            lambda event: self.show_unavailable(),
        )

        self.text.tag_bind(
            "menu_exit",
            "<Button-1>",
            lambda event: self.root.destroy(),
        )

        self.text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    MainApp(root)
    root.mainloop()
