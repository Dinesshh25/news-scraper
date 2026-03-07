import time
import re
from urllib.parse import urlparse

from PyQt5.QtCore import QThread, pyqtSignal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class ScraperWorker(QThread):
    """
    Worker thread untuk menjalankan scraping di background.
    
    Signals:
        progress(str)          - Mengirim pesan status/progress ke GUI
        article_scraped(dict)  - Mengirim satu artikel hasil scraping ke GUI
        finished_signal()      - Memberitahu GUI bahwa scraping selesai
        error(str)             - Mengirim pesan error ke GUI
    """

    progress = pyqtSignal(str)
    article_scraped = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, batas_berita=10, jumlah_halaman=2, delay=2):
        """
        Args:
            url (str): URL utama yang akan di-scrape
            batas_berita (int): Jumlah maksimal berita yang diambil
            jumlah_halaman (int): Jumlah halaman yang di-scan untuk link
            delay (int/float): Delay antar request dalam detik
        """
        super().__init__()
        self.url = url
        self.batas_berita = batas_berita
        self.jumlah_halaman = jumlah_halaman
        self.delay = delay
        self._is_cancelled = False

    def cancel(self):
        """Membatalkan proses scraping."""
        self._is_cancelled = True

    def run(self):
        """
        Method utama yang berjalan di thread terpisah.
        Melakukan scraping dan mengirim hasil ke GUI secara bertahap.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")

        driver = None

        try:
            self.progress.emit("Membuka browser...")
            driver = webdriver.Chrome(options=chrome_options)

            domain_utama = urlparse(self.url).netloc
            domain_inti = ".".join(domain_utama.split(".")[-2:])

            link_artikel = []

            # ---- TAHAP 1: KUMPULKAN LINK ARTIKEL ----
            self.progress.emit("Mengakses halaman utama...")
            driver.get(self.url)
            time.sleep(3)

            for hal in range(self.jumlah_halaman):
                if self._is_cancelled:
                    self.progress.emit("Scraping dibatalkan.")
                    return

                self.progress.emit(f"Scanning halaman {hal + 1} dari {self.jumlah_halaman}...")

                semua_tag_a = driver.find_elements(By.TAG_NAME, "a")

                kata_terlarang = [
                    "login", "profile", "group", "topik", "tag", "category",
                    "author", "account", "?source=", "indeks", "video", "search",
                    "podcast", "foto", "tv", "komentar", "tujuan", "about", "contact"
                ]

                for tag in semua_tag_a:
                    href = tag.get_attribute("href")

                    if href and href.startswith("http") and domain_inti in href:
                        if href.count("-") >= 2 and re.search(r'\d{2,}', href):
                            aman = True
                            for kata in kata_terlarang:
                                if kata in href.lower():
                                    aman = False
                                    break

                            if aman and href not in link_artikel:
                                link_artikel.append(href)

                # Navigasi ke halaman berikutnya
                if hal < self.jumlah_halaman - 1:
                    try:
                        next_btn = driver.find_element(
                            By.XPATH,
                            "//a[contains(text(), 'Next') or contains(text(), 'Selanjutnya') or contains(text(), 'Berikutnya')]"
                        )
                        self.progress.emit("Pindah ke halaman berikutnya...")
                        next_btn.click()
                        time.sleep(self.delay)
                    except Exception:
                        self.progress.emit("Tombol pagination tidak ditemukan.")
                        break

            total_link = len(link_artikel)
            jumlah_target = min(self.batas_berita, total_link)
            self.progress.emit(f"Ditemukan {total_link} link. Mengambil {jumlah_target} berita...")

            # ---- TAHAP 2: SCRAPE SETIAP ARTIKEL (BERTAHAP) ----
            for idx, link in enumerate(link_artikel[:self.batas_berita]):
                if self._is_cancelled:
                    self.progress.emit("Scraping dibatalkan.")
                    return

                self.progress.emit(f"Scraping artikel {idx + 1}/{jumlah_target}...")

                # Delay antar request
                if idx > 0:
                    time.sleep(self.delay)

                driver.get(link)
                time.sleep(2)

                # Ambil Judul
                try:
                    judul = driver.find_element(By.TAG_NAME, "h1").text
                except Exception:
                    judul = "Judul tidak ditemukan"

                # Ambil Tanggal
                tanggal = ""
                try:
                    meta_date = driver.find_elements(
                        By.XPATH,
                        "//meta[@property='article:published_time' or @name='pubdate' or @property='og:updated_time']"
                    )
                    if meta_date:
                        tanggal = meta_date[0].get_attribute("content")
                except Exception:
                    pass

                if not tanggal:
                    try:
                        tanggal = driver.find_element(By.TAG_NAME, "time").text
                    except Exception:
                        try:
                            el_tanggal = driver.find_element(
                                By.XPATH,
                                "//*[contains(text(), '2024') or contains(text(), '2025') or contains(text(), '2026')]"
                            )
                            tanggal = el_tanggal.text
                        except Exception:
                            tanggal = "Tanggal tidak tersedia"

                # Ambil Isi Berita
                try:
                    paragraf = driver.find_elements(By.TAG_NAME, "p")
                    isi_berita = ""
                    for p in paragraf:
                        teks = p.text.strip()
                        if len(teks) > 80 and "Copyright" not in teks:
                            isi_berita += teks + "\n\n"
                except Exception:
                    isi_berita = "Isi tidak ditemukan"

                artikel = {
                    "judul": judul,
                    "tanggal": tanggal,
                    "isi": isi_berita.strip(),
                    "url": link
                }

                # Kirim satu artikel ke GUI secara bertahap
                self.article_scraped.emit(artikel)
                self.progress.emit(f"Artikel {idx + 1}/{jumlah_target} berhasil diambil: {judul[:50]}...")

            self.progress.emit(f"Scraping selesai! Total {jumlah_target} berita berhasil diambil.")

        except Exception as e:
            self.error.emit(f"Terjadi error saat scraping:\n\n{str(e)}")

        finally:
            if driver:
                driver.quit()
            self.finished_signal.emit()
