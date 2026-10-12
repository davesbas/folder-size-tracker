"""Logika pemindaian folder (tanpa tampilan, bisa dipakai ulang)."""
import os


def format_size(num_bytes):
    """Ubah byte menjadi KB/MB/GB yang mudah dibaca."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def make_bar(percent, width=20):
    """Bar teks, misalnya ████████░░░░░░░░░░░░."""
    filled = int(percent / 100 * width)
    return "█" * filled + "░" * (width - filled)


def folder_size(path):
    """Hitung total ukuran sebuah folder secara rekursif."""
    total = 0
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += folder_size(entry.path)
                except OSError:
                    continue
    except OSError:
        pass  # folder terlarang, lewati saja
    return total


def scan(root, on_progress=None):
    """Hitung ukuran tiap item di dalam root, urut dari terbesar.

    on_progress(nama) dipanggil setiap mulai memindai satu subfolder,
    berguna untuk menampilkan status di tampilan.
    """
    results = []
    try:
        with os.scandir(root) as entries:
            items = list(entries)
    except OSError:
        return results

    for entry in items:
        try:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if on_progress:
                    on_progress(entry.name)
                results.append((entry.path, folder_size(entry.path)))
            elif entry.is_file():
                results.append((entry.path, entry.stat().st_size))
        except OSError:
            continue

    results.sort(key=lambda item: item[1], reverse=True)
    return results