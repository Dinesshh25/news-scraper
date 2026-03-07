# 📰 News Scraper Tool

Aplikasi desktop berbasis Python untuk mengumpulkan, menampilkan, dan mengekspor artikel berita dari situs web secara otomatis menggunakan web scraping dengan Selenium dan GUI PyQt5.

---

## 📋 Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Struktur Proyek](#struktur-proyek)
- [Komponen Utama](#komponen-utama)
- [Alur Sistem](#alur-sistem)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Dokumentasi Teknis](#dokumentasi-teknis)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Fitur Utama

✅ **Web Scraping Otomatis** - Mengumpulkan artikel dari website berita secara otomatis  
✅ **GUI Interaktif** - Antarmuka user-friendly dengan PyQt5  
✅ **Multi-Threading** - Scraping berjalan di thread terpisah agar GUI tetap responsif  
✅ **Akumulasi Data** - Bisa scraping dari beberapa URL dan hasilnya terakumulasi  
✅ **Pagination** - Navigasi hasil dengan pagination (5 item per halaman)  
✅ **Export Multi-Format** - Ekspor ke CSV dan Excel  
✅ **Pencarian Dinamis** - Filter link dengan regex dan blacklist keyword  
✅ **Live Preview** - Hasil scraping ditampilkan real-time saat sedang diproses  

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEWS SCRAPER APPLICATION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              GUI LAYER (PyQt5)                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  • Input URL & Config                             │  │   │
│  │  │  • Real-time Progress Display                     │  │   │
│  │  │  • Table Results dengan Pagination               │  │   │
│  │  │  • Export & Clear Buttons                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                      │                                     │   │
│  │                      │ PyQt5 Signals/Slots               │   │
│  │                      ▼                                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  EVENT HANDLERS (gui.py)                           │  │   │
│  │  │  • on_progress()                                   │  │   │
│  │  │  • on_article_scraped()                            │  │   │
│  │  │  • on_scraping_finished()                          │  │   │
│  │  │  • on_scraping_error()                             │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           WORKER THREAD LAYER (worker_thread.py)        │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  ScraperWorker (QThread)                           │  │   │
│  │  │  • Jalankan scraping di thread terpisah            │  │   │
│  │  │  • Emit signals: progress, article_scraped, etc.  │  │   │
│  │  │  • Support cancel operation                        │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                      │                                     │   │
│  │                      │ Selenium WebDriver                │   │
│  │                      ▼                                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  SCRAPER ENGINE (scraper.py)                       │  │   │
│  │  │  • jalankan_scraper(url, batas_berita, halaman)   │  │   │
│  │  │  • Link Collection & Filtering                     │  │   │
│  │  │  • Pagination Navigation                           │  │   │
│  │  │  • Article Data Extraction                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                      │                                     │   │
│  │                      │ Chrome WebDriver (Headless)       │   │
│  │                      ▼                                     │   │
│  │           ┌──────────────────────┐                        │   │
│  │           │   Target Website     │                        │   │
│  │           │  (e.g. Kompas, dll) │                        │   │
│  │           └──────────────────────┘                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        DATA EXPORT LAYER (exporter.py)                  │   │
│  │  • export_to_csv()                                       │   │
│  │  • export_to_excel()                                     │   │
│  │  • Data Validation                                       │   │
│  │  • Logging                                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Struktur Proyek

```
news-scraper/
├── main.py                  # Entry point aplikasi
├── gui.py                   # GUI PyQt5 (utama)
├── worker_thread.py         # Multi-threading worker
├── scraper.py              # Core scraping logic
├── exporter.py             # Export ke CSV/Excel
├── requirements.txt        # Dependencies
├── README.md               # Dokumentasi (file ini)
├── scraper.log             # Log file (auto-generated)
└── __pycache__/            # Cache Python
```

---

## 🔧 Komponen Utama

### 1. **main.py** - Entry Point
```python
def main():
    app = QApplication(sys.argv)
    window = NewsScraperGUI()
    window.show()
    sys.exit(app.exec_())
```
- Menginisialisasi aplikasi PyQt5
- Membuat dan menampilkan GUI window
- Mengatur event loop aplikasi

---

### 2. **gui.py** - GUI & Event Handling
**Tanggung jawab:**
- Membuat UI dengan PyQt5 (QWidget, QLineEdit, QPushButton, QTableWidget)
- Mengelola input URL dari user
- Menampilkan hasil scraping secara real-time di table
- Pagination (Previous/Next buttons)
- Export & Clear functionality
- Styling dengan stylesheet CSS

**Key Classes:**
```python
class NewsScraperGUI(QWidget):
    def start_scraping()       # Mulai proses scraping
    def on_progress()          # Update progress message
    def on_article_scraped()   # Tambah artikel ke table
    def on_scraping_finished() # Scraping selesai
    def on_scraping_error()    # Handle error
    def display_page()         # Tampilkan halaman tertentu
    def export_csv()           # Export ke CSV
    def export_excel()         # Export ke Excel
```

**State Management:**
- `self.all_data[]` - Semua artikel tersimpan di sini (accumulative)
- `self.current_page` - Halaman pagination saat ini
- `self.worker` - Referensi ke ScraperWorker thread

---

### 3. **worker_thread.py** - Multi-Threading Worker

**Tanggung jawab:**
- Menjalankan scraping di thread terpisah (non-blocking GUI)
- Emit signals untuk komunikasi dengan GUI
- Mendukung cancel operation

**Signals (PyQt5):**
```python
progress = pyqtSignal(str)        # Status progress message
article_scraped = pyqtSignal(dict) # Satu artikel berhasil diambil
finished_signal = pyqtSignal()    # Scraping selesai
error = pyqtSignal(str)           # Terjadi error
```

**Flow dalam run():**
1. Inisialisasi Chrome WebDriver (headless)
2. Tahap 1: Kumpulkan semua link artikel
   - Loop halaman sesuai `jumlah_halaman`
   - Filter link dengan regex & blacklist
   - Navigasi Next button
3. Tahap 2: Scrape setiap artikel
   - Extract judul dari `<h1>`
   - Extract tanggal dari `<meta>` atau `<time>`
   - Extract isi dari `<p>` tags
   - Emit `article_scraped` signal

---

### 4. **scraper.py** - Core Scraping Logic

**Tanggung jawab:**
- Fungsi utama `jalankan_scraper(url, batas_berita, jumlah_halaman)`
- Logika ekstraksi data artikel

**Email filtering rules:**
- ✅ URL dimulai dengan "http://" atau "https://"
- ✅ URL berada di domain yang sama
- ❌ Blacklist: login, profile, group, tag, category, video, search, podcast, dll

**Data Extraction:**
```python
artikel = {
    "judul": str,      # Dari <h1>
    "tanggal": str,    # Dari <meta> / <time>
    "isi": str,        # Dari <p> (min 80 char per paragraph)
    "url": str         # Link artikel lengkap
}
```

---

### 5. **exporter.py** - Export & Validation

**Tanggung jawab:**
- Validasi data sebelum export
- Export ke CSV (dengan UTF-8 BOM)
- Export ke Excel (dengan openpyxl)
- Logging ke `scraper.log`

**Functions:**
```python
validate_data(data)          # Pastikan data valid
export_to_csv(data, filename) # Export CSV dengan timestamp
export_to_excel(data, filename) # Export Excel dengan timestamp
```

---

## 📊 Alur Sistem

### A. **User Flow (UI Perspective)**

```
1. User membuka aplikasi
   └─> main.py → NewsScraperGUI window ditampilkan

2. User memasukkan URL di input field
   └─> Contoh: https://indeks.kompas.com/

3. User klik "Start Scraping"
   ├─> GUI: URL validation
   ├─> GUI: Disable tombol (prevent race condition)
   ├─> GUI: Buat ScraperWorker thread baru
   ├─> GUI: Connect signals ke slots
   └─> Worker: Thread mulai berjalan

4. Proses Scraping (di thread terpisah)
   ├─> Tahap 1: Kumpulkan link artikel
   │   ├─> Driver.get(URL)
   │   ├─> Find all <a> tags
   │   ├─> Filter dengan rules
   │   ├─> Loop pagination (Next button)
   │   └─> Emit: progress("Link yang dikumpulkan: X")
   │
   ├─> Tahap 2: Scrape setiap artikel
   │   ├─> For each link (max 10):
   │   │   ├─> Driver.get(link)
   │   │   ├─> Extract judul, tanggal, isi
   │   │   ├─> Emit: article_scraped(article_dict)
   │   │   └─> GUI: on_article_scraped() → add row to table
   │   │
   │   └─> Emit: progress("Artikel X/10 berhasil...")
   │
   └─> Driver.quit()

5. Hasil ditampilkan real-time di table
   └─> Numbering: 1, 2, 3, ..., 10

6. User ingin scraping URL yang berbeda
   └─> URL B diinput dan "Start Scraping" diklik
   └─> Data URL A tetap ada (accumulative)
   └─> Hasil URL B ditambahkan: 11, 12, ..., 20

7. User klik "Export CSV" atau "Export Excel"
   ├─> Exporter: Validasi all_data
   ├─> Exporter: Convert ke DataFrame (pandas)
   ├─> Exporter: Save file dengan timestamp
   └─> UI: Show success dialog

8. User klik "Clear Table" (optional)
   └─> Reset semua: all_data[], table rows, current_page
```

### B. **Technical Flow (Thread Perspective)**

```
┌─ MAIN THREAD (GUI) ─────────────────────────────────────────┐
│                                                              │
│  User Input → start_scraping()                             │
│       │                                                     │
│       └─→ Create ScraperWorker                             │
│           │                                                │
│           │  ┌─ WORKER THREAD (Background) ──────────────┐│
│           │  │                                            ││
│           └─→│  run() in ScraperWorker                   ││
│              │    │                                       ││
│              │    ├─→ Initialize Chrome WebDriver        ││
│              │    │    │                                  ││
│              │    │    [PHASE 1: Link Collection]       ││
│              │    │    ├─→ Loop pages                    ││
│              │    │    ├─→ Find all <a> elements        ││
│              │    │    ├─→ Filter & validate             ││
│              │    │    └─→ emit(progress)                ││
│              │    │         ↓                             ││
│         ┌────────────────────────────┐                   ││
│         │  GUI: Update status label  │                   ││
│         └────────────────────────────┘                   ││
│              │                                            ││
│              │    [PHASE 2: Article Scraping]           ││
│              │    └─→ For each valid link:               ││
│              │         ├─→ Get page DOM                  ││
│              │         ├─→ Extract metadata              ││
│              │         │   (judul, tanggal, isi)         ││
│              │         └─→ emit(article_scraped)        ││
│              │             ↓                              ││
│         ┌────────────────────────────────────────────┐  ││
│         │  GUI: on_article_scraped()                 │  ││
│         │  • Append to self.all_data                 │  ││
│         │  • Insert row to table                     │  ││
│         │  • Update pagination label                 │  ││
│         └────────────────────────────────────────────┘  ││
│              │                                            ││
│              │    └─→ Quit WebDriver                     ││
│              │    └─→ emit(finished_signal)              ││
│              │         ↓                                  ││
│         ┌──────────────────────────┐                    ││
│         │  GUI: on_scraping_finish │                    ││
│         │  • Enable tombol          │                    ││
│         │  • Reset worker reference │                    ││
│         └──────────────────────────┘                    ││
│              │                                            ││
│              └── EXIT──────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 💾 Instalasi

### Prerequisites
- **Python** 3.8 atau lebih tinggi
- **Chrome/Chromium** browser (untuk Selenium WebDriver)

### Steps

1. **Clone atau download repository**
```bash
cd news-scraper
```

2. **Buat virtual environment** (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download ChromeDriver**
   - Download dari: https://chromedriver.chromium.org/
   - Pastikan versi sesuai dengan Chrome yang terinstal
   - Letakkan di PATH atau di folder project

5. **Jalankan aplikasi**
```bash
python main.py
```

---

## 🚀 Cara Penggunaan

### Langkah Dasar

1. **Buka aplikasi** → double-click `main.py` atau `python main.py`

2. **Input URL berita** di field input
   - Contoh: `https://indeks.kompas.com/`
   - Contoh: `https://www.detik.com/`

3. **Klik "Start Scraping"**
   - Status akan berubah menjadi "Memulai scraping..."
   - Tombol akan disable untuk prevent multiple threading
   - Hasil akan ditampilkan real-time

4. **Lihat hasil di table**
   - Nomor, Judul, Tanggal, Konten ditampilkan
   - Klik judul (biru) untuk membuka artikel asli di browser

5. **Navigation** (jika lebih dari 5 hasil)
   - Gunakan Previous/Next buttons
   - Page indicator menunjukkan halaman saat ini

6. **Export data**
   - Klik "Export CSV" → file `news_scraping_YYYYMMDD_HHMMSS.csv`
   - Klik "Export Excel" → file `news_scraping_YYYYMMDD_HHMMSS.xlsx`

7. **Scraping dari URL lain** (Optional - Accumulative mode)
   - Input URL baru
   - Klik "Start Scraping" lagi
   - Data lama tetap ada, results terakumulasi (no. 11, 12, dst.)

8. **Reset tabel** (Optional)
   - Klik "Clear Table" untuk menghapus semua data

---

## 📝 Dokumentasi Teknis

### Link Filtering Rules

Sebuah link dianggap **valid** jika memenuhi kriteria:

```python
# 1. Harus HTTP/HTTPS
if not href.startswith("http"):
    continue

# 2. Domain harus sama dengan URL input
domain_inti = "kompas.com"  # dari URL utama
if domain_inti not in href:
    continue

# 3. Jangan ada blacklist keywords (case-insensitive)
blacklist = [
    "login", "profile", "group", "topik", "tag", 
    "category", "author", "account", "video", "search",
    "podcast", "foto", "tv", "komentar", "about", "contact"
]
if any(kata in href.lower() for kata in blacklist):
    continue

# 4. Deduplikasi
if href not in link_artikel:
    link_artikel.append(href)
```

### Data Extraction Strategy

**Judul:**
```python
judul = driver.find_element(By.TAG_NAME, "h1").text
```

**Tanggal (Priority order):**
1. Meta tag: `article:published_time`, `pubdate`, `og:updated_time`
2. HTML `<time>` tag
3. Text search untuk tahun (2024, 2025, 2026)

**Isi:**
```python
# Extract dari semua <p> tags
# Filter: hanya paragraph dengan >80 karakter
# Exclude: paragraf yang mengandung "Copyright"
```

### Database Structure

Data disimpan dalam list of dictionaries:
```python
self.all_data = [
    {
        "judul": "Judul Artikel 1",
        "tanggal": "2026-03-07T10:30:00+00:00",
        "isi": "Isi artikel lengkap...",
        "url": "https://example.com/article-1"
    },
    {
        "judul": "Judul Artikel 2",
        "tanggal": "2026-03-06",
        "isi": "Isi artikel 2...",
        "url": "https://example.com/article-2"
    },
    # ... lebih banyak
]
```

### Signal Connection Diagram

```
ScraperWorker (Thread)        →    NewsScraperGUI (Main Thread)
──────────────────────────────────────────────────────────
progress.emit(msg)            →    on_progress(msg)
article_scraped.emit(dict)    →    on_article_scraped(dict)
finished_signal.emit()        →    on_scraping_finished()
error.emit(msg)               →    on_scraping_error(msg)
```

---

## 🐛 Troubleshooting

### Problem: "ChromeDriver not found"
**Solution:**
- Download ChromeDriver: https://chromedriver.chromium.org/
- Pastikan versi sesuai dengan Chrome installed
- Letakkan di PATH atau di folder project

### Problem: "Hanya 1 link yang diambil padahal seharusnya 10"
**Solution:**
- Cek struktur HTML website target (mungkin layout berbeda)
- Cek apakah Next button ada dan dapat di-click
- Tambahkan print/debug untuk melihat semua link yang ditemukan
- Modifikasi filter rules jika terlalu ketat

### Problem: "Table tetap reset ke nomor 1"
**Solution:**
- Update ke versi terbaru (sudah fixed di v2)
- Jangan klik "Clear Table" sebelum scraping URL kedua

### Problem: "Scraping timeout / tidak responsif"
**Solution:**
- Tambah delay: ubah `delay=2` menjadi `delay=3` di gui.py
- Ubah `jumlah_halaman=2` menjadi `1` untuk test cepat
- Cek koneksi internet

### Problem: "Export file gagal"
**Solution:**
- Pastikan ada minimal 1 artikel yang berhasil discrap
- Cek permission folder untuk write file
- Cek disk space (biasanya tidak masalah untuk CSV/Excel)

### Problem: "GUI tidak responsif saat scraping"
**Solution:**
- Normal! GUI memang tidak responsif saat scraping berjalan di thread
- Tunggu sampai "Scraping selesai" di status bar
- Jangan close aplikasi forcefully, biarkan proses selesai

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | Latest | GUI Framework |
| Selenium | 4.x | Web Scraping & Browser Automation |
| pandas | Latest | Data processing & DataFrame |
| openpyxl | Latest | Excel export |
| python-dateutil | Latest | Date parsing |

---

## 🔐 Security Notes

- ✅ Gunakan headless mode (tidak buka browser window)
- ✅ Disable logging detail (log-level=3) untuk prevent url logging
- ⚠️ Jangan store password / credential di code
- ⚠️ Respect robots.txt dan ToS website yang di-scrape
- ⚠️ Gunakan delay yang appropriate untuk prevent server overload

---

## 📈 Future Enhancement Ideas

- [ ] Add proxy support
- [ ] Custom CSS selector configuration
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] Scheduler untuk scraping otomatis
- [ ] Advanced filtering & search
- [ ] Duplicate detection
- [ ] API endpoint
- [ ] Dark mode UI

---

## 📄 License

Free to use for educational & personal projects.

---

## 👤 Author

Created for learning web scraping with Python, PyQt5, and Selenium.

---

**Last Updated:** March 7, 2026
