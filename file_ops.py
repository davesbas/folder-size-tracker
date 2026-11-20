import csv
import os
from scanner import format_size

def save_to_csv(filepath, items):
    """Simpan hasil pemindaian [(path, size), ...] ke file CSV."""
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nama", "Path", "Tipe", "Ukuran (Bytes)", "Ukuran Terformat"])
        for path, size in items:
            item_type = "Folder" if os.path.isdir(path) else "File"
            writer.writerow([
                os.path.basename(path),
                path,
                item_type,
                size,
                format_size(size),
            ])

