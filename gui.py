import sys

# Import komponen PyQt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem
)

# Import fungsi scraper
from scraper import jalankan_scraper

class NewsScraperGUI(QWidget):

    def __init__(self):
        super().__init__()

        # Judul window
        self.setWindowTitle("News Scraper")

        # Ukuran window
        self.setGeometry(200, 200, 900, 600)

        # Layout utama
        main_layout = QVBoxLayout()

        # =========================
        # Bagian input URL
        # =========================

        input_layout = QHBoxLayout()

        label = QLabel("News URL:")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://indeks.kompas.com/")

        self.start_button = QPushButton("Start Scraping")

        input_layout.addWidget(label)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.start_button)

        # =========================
        # Tabel hasil scraping
        # =========================

        self.table = QTableWidget()

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["No", "Title", "Date", "Content"]
        )

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 400)

        # =========================
        # Susun layout
        # =========================

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Hubungkan tombol dengan function
        self.start_button.clicked.connect(self.start_scraping)

    # =====================================
    # Function saat tombol diklik
    # =====================================

    def start_scraping(self):

        # Ambil URL dari input
        url = self.url_input.text()

        if not url:
            print("URL kosong")
            return

        # Reset tabel
        self.table.setRowCount(0)

        # Jalankan scraper
        results = jalankan_scraper(url, batas_berita=5)

        # Tampilkan hasil
        self.display_results(results)

    # =====================================
    # Function menampilkan hasil scraping
    # =====================================

    def display_results(self, data):

        for i, news in enumerate(data):

            row = self.table.rowCount()
            self.table.insertRow(row)

            # Nomor
            self.table.setItem(row, 0, QTableWidgetItem(str(i + 1)))

            # Judul
            self.table.setItem(row, 1, QTableWidgetItem(news["judul"]))

            # Tanggal
            self.table.setItem(row, 2, QTableWidgetItem(news["tanggal"]))

            # Isi berita dipotong
            content_preview = news["isi"][:200]

            self.table.setItem(row, 3, QTableWidgetItem(content_preview))


# ==============================
# Menjalankan aplikasi
# ==============================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = NewsScraperGUI()
    window.show()

    sys.exit(app.exec_())