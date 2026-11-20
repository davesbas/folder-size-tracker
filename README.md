# Terminal Disk Analyzer (Folder Size Tracker)

Aplikasi penganalisis kapasitas penyimpanan dan pelacak ukuran folder menggunakan **Python** dan **Tkinter**. Dirancang ringan tanpa _library_ eksternal (_zero external dependencies_) dan mendukung lintas platform (**Windows** maupun **Linux**).

---

## Fitur Utama

- **Pemilih Folder & Drive Lintas Platform (`FolderPicker`):**
  - Mendeteksi _drive_ `A:\` hingga `Z:\` secara otomatis di **Windows**.
  - Mendeteksi _root_ (`/`), _home directory_ (`~`), dan _mount point_ umum (`/run/media`, `/media`, `/mnt`) di **Linux**.
- **Pemindaian Multi-threading & Caching:** Proses _scanning_ berjalan di _background thread_ sehingga antarmuka tidak membeku (_freeze_), dilengkapi penyimpanan _cache_ untuk navigasi antarfolder yang instan.
- **Keamanan Sistem File:** Melewati _symlink_, _mount point_ terpisah, dan direktori virtual Linux (`/proc`, `/sys`, `/dev`) untuk mencegah _infinite loop_ atau perhitungan ganda.
- **Visualisasi Bar & Persentase:** Menampilkan ukuran file/folder yang sudah diformat (`B`, `KB`, `MB`, `GB`, `TB`, `PB`) beserta _progress bar_ teks (`█░`) dan persentase pemakaian.
- **Ekspor ke CSV:** Menyimpan hasil pemindaian direktori saat ini ke dalam file `.csv`.
- **Mode CLI Alternatif:** Menyediakan skrip baris perintah mandiri (`folder_size.py`) untuk pemindaian cepat langsung dari terminal.

---

## Prasyarat

- **Python 3.x**
- **Tkinter** (biasanya sudah terinstal bawaan bersama Python di Windows; untuk pengguna Linux pastikan paket `python3-tk` sudah terpasang).

Contoh instalasi Tkinter di Linux (jika belum ada):

```bash
# Ubuntu / Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

---

## Cara Menjalankan

### 1. Mode GUI (Utama)

Jalankan aplikasi antarmuka utama dengan perintah:

```bash
python main.py
```

### 2. Mode CLI (Terminal Murni)

Jika hanya ingin melihat daftar item terbesar langsung di terminal tanpa GUI:

```bash
python folder_size.py <path_folder> --top 10
```

Contoh:

```bash
python folder_size.py /home/user/Downloads --top 5
```

---

## Pintasan Keyboard & Navigasi (Mode GUI)

| Tombol / Aksi                         | Fungsi                                                         |
| :------------------------------------ | :------------------------------------------------------------- |
| **`1`** atau Klik `[1] PINDAI FOLDER` | Membuka jendela pemilih folder/drive untuk mulai memindai      |
| **`2`** atau Klik `[2] EKSPOR CSV`    | Mengekspor hasil pemindaian saat ini ke file `.csv`            |
| **`0`** atau Klik `[0] KELUAR`        | Menutup aplikasi                                               |
| **`Enter`** atau **Double-Click**     | Masuk ke dalam subfolder yang dipilih pada daftar              |
| **`Backspace`**                       | Kembali ke folder induk (_parent directory_)                   |
| **`[ REFRESH ]`**                     | Memindai ulang folder yang sedang dibuka (memperbarui _cache_) |
| **`[ CLEAR ]`**                       | Membersihkan log dan mereset hasil pemindaian                  |
| **`Esc`** _(di jendela Pilih Folder)_ | Membatalkan pemilihan folder                                   |

---

## Struktur Proyek

```text
folder-size-tracker/
├── main.py           # Aplikasi utama GUI (MainApp) & event loop
├── scanner.py        # Logika inti pemindaian ukuran folder, format byte, & info disk
├── folder_picker.py  # Dialog kustom pemilih folder dan pendeteksi drive/mount point
├── file_ops.py       # Fungsi ekspor hasil pemindaian ke format CSV
├── theme.py          # Konfigurasi warna dan font tema retro-terminal
├── folder_size.py    # Versi CLI mandiri menggunakan argparse
└── README.md         # Dokumentasi proyek
```
