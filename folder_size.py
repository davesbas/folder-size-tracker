"""Pelacak ukuran folder sederhana"""

import argparse
import os

from scanner import format_size, make_bar, scan

def main():
    parser = argparse.ArgumentParser(description="Pelacak ukuran folder")
    parser.add_argument("path", help="folder yang ingin dipindai")
    parser.add_argument("--top", type=int, default=10, help="jumlah teratas")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print("Path tidak ditemukan atau bukan folder.")
        return

    results = scan(
        args.path,
        on_progress=lambda name: print(f"Memindai {name[:40]:<40}...", end="\r", flush=True),
    )

    print(" " * 60, end="\r")
    if not results:
        print(f"Folder kosong atau akses ditolak: {args.path}")
        return

    total_size = sum(size for _, size in results)
    divider = total_size or 1

    print(f"\n{args.top} terbesar di {args.path}\n")
    for path, size in results[: args.top]:
        percent = size / divider * 100
        bar = make_bar(percent, width=20)
        mark = "/" if os.path.isdir(path) else ""
        print(f"{format_size(size):>10} {bar} {percent:5.1f}% {os.path.basename(path)}{mark}")
    print(f"\nTotal: {format_size(total_size)}")

if __name__ == "__main__":
    main()