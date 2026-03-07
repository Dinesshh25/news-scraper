from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import time
import re

def jalankan_scraper(url_utama, batas_berita=10, jumlah_halaman=2):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    
    domain_utama = urlparse(url_utama).netloc
    domain_inti = ".".join(domain_utama.split(".")[-2:])
    
    link_artikel = [] 
    
    try:
        driver.get(url_utama)
        time.sleep(3)

        # ---- SISTEM PENGAMBILAN LINK + PAGINATION ---
        for hal in range(jumlah_halaman):
            print(f"--- Scanning Halaman {hal + 1} ---")
            semua_tag_a = driver.find_elements(By.TAG_NAME, "a")
            
            kata_terlarang = [
                "login", "profile", "group", "topik", "tag", "category",
                "author", "account", "?source=", "indeks", "video", "search",
                "podcast", "foto", "tv", "komentar", "tujuan", "about", "contact"
            ]

            for tag in semua_tag_a:
                href = tag.get_attribute("href")

                # simple debug print so we can see which urls are visited
                # (comment out later when everything works)
                # print("candidate href=", href)

                # Filter: awali http dan berada dalam domain utama
                if not href or not href.startswith("http"):
                    continue
                if domain_inti not in href:
                    continue

                # beberapa situs memakai struktur berbeda, jadi jangan terlalu
                # ketat terhadap jumlah '-' atau angka. jika ingin membatasi
                # gunakan regex yang sesuai dengan situs target, misalnya
                # artikel kompas selalu punya '/YYYY/MM/DD/' di url.
                
                aman = True
                for kata in kata_terlarang:
                    if kata in href.lower():
                        aman = False
                        break

                if not aman:
                    continue

                # pastikan tidak duplikat
                if href not in link_artikel:
                    link_artikel.append(href)
            
            if hal < jumlah_halaman - 1: 
                try:
                    next_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(text(), 'Selanjutnya') or contains(text(), 'Berikutnya')]")
                    print("Pindah ke halaman berikutnya...")
                    next_btn.click()
                    time.sleep(3) 
                except:
                    print("Tombol pagination tidak ditemukan lagi.")
                    break

        # --- PENGOLAHAN LINK YANG DITEMUKAN ---
        print(f"\nTotal ditemukan {len(link_artikel)} link unik.")
        # debugging: tampilkan semua link sebelum diproses
        for l in link_artikel:
            print("  ->", l)
        
        hasil_scraping = []
        for link in link_artikel[:batas_berita]:
            print(f"Membuka: {link}")
            driver.get(link)
            time.sleep(2)
            
            # Ambil Judul
            try:
                judul = driver.find_element(By.TAG_NAME, "h1").text
            except:
                judul = "Judul tidak ditemukan"
                
            # Ambil Tanggal
            tanggal = ""
            try:
                # Cara 1: Cari di meta tag (biasanya paling akurat untuk mesin)
                meta_date = driver.find_elements(By.XPATH, "//meta[@property='article:published_time' or @name='pubdate' or @property='og:updated_time']")
                if meta_date:
                    tanggal = meta_date[0].get_attribute("content")
            except:
                pass

            if not tanggal:
                try:
                    # Cara 2: Cari tag <time> (umum di web modern)
                    tanggal = driver.find_element(By.TAG_NAME, "time").text
                except:
                    try:
                        # Cara 3: Cari elemen yang mengandung kata "2024" atau "2025" (Prediksi teks tanggal)
                        el_tanggal = driver.find_element(By.XPATH, "//*[contains(text(), '2024') or contains(text(), '2025')]")
                        tanggal = el_tanggal.text
                    except:
                        tanggal = "Tanggal tidak tersedia"

            # Ambil Isi Berita
            try:
                paragraf = driver.find_elements(By.TAG_NAME, "p")
                isi_berita = ""
                for p in paragraf:
                    teks = p.text.strip()
                    if len(teks) > 80 and "Copyright" not in teks:
                        isi_berita += teks + "\n\n"
            except:
                isi_berita = "Isi tidak ditemukan"
                
            hasil_scraping.append({
                "judul": judul,
                "tanggal": tanggal,
                "isi": isi_berita.strip(),
                "url": link
            })
            
        return hasil_scraping

    except Exception as e:
        print(f"Error utama: {e}")
        return []
    finally:
        driver.quit()

        
if __name__ == "__main__":
    test_url = "https://indeks.kompas.com/" 
    
    hasil = jalankan_scraper(test_url, batas_berita=2)
    
    print("\n=== HASIL AKHIR ===")
    for i, berita in enumerate(hasil):
        print(f"\nBerita ke-{i+1}")
        print(f"Judul   : {berita['judul']}")
        print(f"Tanggal : {berita['tanggal']}")
        print(f"Isi     : {berita['isi'][:250]}... [dipotong]")