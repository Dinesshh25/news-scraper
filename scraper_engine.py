from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import time
import re # Modul untuk mendeteksi pola teks (seperti angka)

def jalankan_scraper(url_utama, batas_berita=3):
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--log-level=3") 
    driver = webdriver.Chrome(options=chrome_options)
    
    domain_utama = urlparse(url_utama).netloc
    domain_inti = ".".join(domain_utama.split(".")[-2:]) 
    
    print(f"Mencoba membuka: {url_utama}\n")
    
    try:
        driver.get(url_utama)
        time.sleep(3) 
        
        semua_tag_a = driver.find_elements(By.TAG_NAME, "a")
        
        # Tambahan kata "tujuan" dan "about" ke daftar hitam
        kata_terlarang = [
            "login", "profile", "group", "topik", "tag", "category", 
            "author", "account", "?source=", "indeks", "video", "search", 
            "podcast", "foto", "tv", "komentar", "tujuan", "about"
        ]
        link_artikel = []
        
        for tag in semua_tag_a:
            href = tag.get_attribute("href")
            
            if href and href.startswith("http") and domain_inti in href:
                # Syarat 1: Ada minimal 3 strip
                if href.count("-") >= 3:
                    # --- JURUS 3: Pastikan ada deretan angka (Tahun/ID) di dalam URL ---
                    # \d{2,} artinya mencari minimal 2 angka berderet (misal 26, 2026, 12345)
                    if re.search(r'\d{2,}', href):
                        
                        aman = True
                        for kata in kata_terlarang:
                            if kata in href.lower():
                                aman = False
                                break
                        
                        if aman and href not in link_artikel:
                            link_artikel.append(href)
        
        print(f"Ditemukan {len(link_artikel)} link artikel SUPER BERSIH.")
        print("Mulai mengambil isi berita...\n")
        
        hasil_scraping = []
        
        for link in link_artikel[:batas_berita]:
            print(f"Membuka: {link}")
            driver.get(link)
            time.sleep(3) 
            
            # 1. Ambil Judul
            try:
                judul = driver.find_element(By.TAG_NAME, "h1").text
            except:
                judul = "Judul tidak ditemukan"
                
            # 2. Ambil Tanggal 
            tanggal = ""
            try:
                # Kombinasi pencarian meta tag yang paling umum
                meta_date = driver.find_element(By.XPATH, "//meta[@property='article:published_time' or @name='pubdate']")
                tanggal = meta_date.get_attribute("content")
            except:
                pass 
                
            if not tanggal: 
                try:
                    tanggal = driver.find_element(By.TAG_NAME, "time").text
                except:
                    tanggal = "Tanggal tidak ditemukan"

            # 3. Ambil Isi Berita
            try:
                paragraf = driver.find_elements(By.TAG_NAME, "p")
                isi_berita = ""
                for p in paragraf:
                    teks = p.text.strip()
                    if len(teks) > 80 and "Copyright" not in teks and "Baca juga" not in teks: 
                        isi_berita += teks + "\n\n"
            except:
                isi_berita = "Isi tidak ditemukan"
                
            data_berita = {
                "judul": judul,
                "tanggal": tanggal,
                "isi": isi_berita.strip(),
                "url": link
            }
            hasil_scraping.append(data_berita)
            
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