"""Pelacak ukuran folder sederhana"""

import argparse
import os

def format_size(num_bytes):
    #ubah byte menjadi KB/MB/GB yang mudah dibaca.
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def folder_size(path):
    #Hitung total ukuran sebuah folder secara rekursif
    total = 0
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_symlink():
                        continue #hindari loop dan hitungan ganda
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += folder_size(entry.path)
                except (PermissionError, OSError):
                    continue #lewati item yang tidak bisa diakses
    except (PermissionError,OSError):
        pass #lewati folder terlarang, misal System Volume Information
    return total

def scan(root):
    #Hitung ukuran tiap item langsung di dalam root.
    results = []
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir():
                        print(f"Memindai {entry.name}...", end="\r")
                        results.append((entry.path, folder_size(entry.path)))
                    elif entry.is_file():
                        results.append((entry.path, entry.stat().st_size))
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError) as e:
        print(f"Tidak bisa membuka {root}: {e}")
    return results

def main():
    parser = argparse.ArgumentParser(description="Pelacak ukuran folder")
    parser.add_argument("path", help="folder yang ingin dipindai")
    parser.add_argument("--top", type=int, default=10, help="jumlah teratas")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print("Path tidak ditemukan atau bukan folder.")
        return

    results = scan(args.path)
    results.sort(key=lambda item: item[1], reverse=True)
    total = sum(size for _, size in results) or 1

    print(" " * 60, end="\r")
    print(f"\n{args.top} terbesar di {args.path}\n")
    for path, size in results[: args.top]:
        percent = size / total * 100
        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
        print(f"{format_size(size):>10} {bar} {percent:5.1f}% {os.path.basename(path)}")
    print(f"\nTotal: {format_size(total)}")

if __name__ == "__main__":
    main()