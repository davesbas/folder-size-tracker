import os 
import queue
import threading
import tkinter as tk
from tkinter import filedialog

from scanner import scan, format_size, make_bar

BG = "#0a1a0a"
FG = "#33ff33"
DIM = "#1f9a1f"
FONT = ("Consolas", 12)

BANNER = """\
=====================================
   TERMINAL DISK ANALYZER
   TERMINAL v1.0
=====================================

[1] PINDAI FOLDER
[2] FILE TERBESAR (belum tersedia)
[3] EKSPOR CSV (belum tersedia)
[0] KELUAR

"""

class RetroApp:
    def __init__(self, root):
        self.root = root
        root.title("Disk Analyzer")
        root.geometry("860x580")
        root.configure(bg=BG)

        self.text = tk.Text(
            root, bg=BG, fg=FG, font=FONT, bd=0, highlightthickness=0,
            wrap="none", padx=16, pady=16, cursor="arrow", state="disabled",
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_config("body", foreground=FG)
        self.text.tag_config("cursor", foreground=FG)

        self.status = tk.Label(root, text="", bg=BG, fg=DIM, font=FONT, anchor="w")
        self.status.pack(fill="x", padx=16)

        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", padx=16, pady=(4,12))
        self._button(bar, "[1] PINDAI", self.start_scan)
        self._button(bar, "[0] KELUAR", root.destroy)

        self.text.config(state="normal")
        self.text.insert("end", "█", "cursor")
        self.text.config(state="disabled")

        self.pending = ""
        self.cursor_on = True
        self.busy = False
        self.events = queue.Queue()

        root.bind("1", lambda e: self.start_scan())
        root.bind("0", lambda e: root.destroy())

        self.say(BANNER)
        self._type_tick()
        self._blink()
        self._poll()

    def _button(self, parent, label, command):
        tk.Button(
            parent, text=label, command=command, bg=BG, fg=FG, font=FONT,
            activebackground=FG, activeforeground=BG, bd=1, relief="solid",
            highlightthickness=0, padx=10,
        ).pack(side="left", padx=(0, 8))

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
        folder = filedialog.askdirectory(title="Pilih folder untuk dipindai")
        if not folder:
            return
        self.busy = True
        self.say(f"\n> Memindai {folder}\n")
        threading.Thread(target=self._worker, args=(folder,), daemon=True).start()

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
        self.status.config(text="")
        if not results:
            self.say("> TIDAK ADA DATA ATAU AKSES DITOLAK\n\n")
            return
        total = sum(size for _, size in results) or 1
        self.say(f"\n10 TERBESAR DI {folder}\n\n")
        for path, size in results[:10]:
            percent = size / total * 100
            name = os.path.basename(path)[:30]
            self.say(f"{format_size(size):>10} {make_bar(percent)} {percent:5.1f}% {name}\n")
        self.say(f"\nTOTAL: {format_size(total)}\n\n> SIAP. TEKAN [1] UNTUK PINDAI LAGI\n")


if __name__ == "__main__":
    root = tk.Tk()
    RetroApp(root)
    root.mainloop()
