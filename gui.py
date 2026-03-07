import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame
)

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox

from worker_thread import ScraperWorker
from exporter import export_to_csv, export_to_excel


class NewsScraperGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.current_page = 0
        self.items_per_page = 5
        self.all_data = []
        self.worker = None  # Referensi ke worker thread
        self.setWindowTitle("News Scraper Tool")
        self.setGeometry(200, 200, 1150, 650)

        main_layout = QVBoxLayout()

        # TITLE
        title = QLabel("📰 News Scraper Dashboard")
        title.setStyleSheet("""
        font-size:28px;
        font-weight:700;
        color:#0F802F;
        margin-bottom:12px;
        """)

        # INPUT AREA
        input_layout = QHBoxLayout()

        label = QLabel("News URL")
        label.setObjectName("urlLabel")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://indeks.kompas.com/")

        self.start_button = QPushButton("Start Scraping")
        self.clear_button = QPushButton("Clear Table")
        self.export_csv_button = QPushButton("Export CSV")
        self.export_excel_button = QPushButton("Export Excel")
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        input_layout.addWidget(label)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.start_button)
        input_layout.addWidget(self.clear_button)
        input_layout.addWidget(self.export_csv_button)
        input_layout.addWidget(self.export_excel_button)

        # STATUS
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
        background:#ECFDF5;
        color:#065F46;
        padding:6px 10px;
        border-radius:6px;
        border:1px solid #A7F3D0;
        font-weight:500;
        """)
        
        # CARD CONTAINER
        card = QFrame()
        card_layout = QVBoxLayout()

        self.table = QTableWidget()

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["No", "Title", "Date", "Content"]
        )

        self.table.setRowCount(0)

        self.table.verticalHeader().setVisible(False)

        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setFixedHeight(100)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 360)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 580)

        self.table.setWordWrap(True)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setFixedHeight(60)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        self.table.cellClicked.connect(self.open_article)

        card_layout.addWidget(self.table)
        card.setLayout(card_layout)

        # LAYOUT
        main_layout.addWidget(title)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        # PAGINATION AREA
        pagination_layout = QHBoxLayout()

        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet("""
        background:#FDF2F8;
        color:#BE185D;
        padding:6px 14px;
        border-radius:10px;
        font-weight:600;
        """)

        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()

        main_layout.addLayout(pagination_layout)

        # EVENTS
        self.start_button.clicked.connect(self.start_scraping)
        self.clear_button.clicked.connect(self.clear_table)
        self.export_csv_button.clicked.connect(self.export_csv)
        self.export_excel_button.clicked.connect(self.export_excel)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        # STYLE
        self.setStyleSheet("""

        QLabel#urlLabel{
            background:#F0FDF4;
            border:1px solid #86EFAC;
            padding:6px 12px;
            border-radius:8px;
        }
                           
        QWidget{
            background:#FFF1F7;
            font-family:Segoe UI;
            font-size:14px;
        }

        QLabel{
            color:#34495E;
            font-weight:600;
        }

        QLineEdit{
            background:white;
            padding:8px;
            border:1px solid #F9A8D4;
            border-radius:8px;
        }

        QPushButton{
            padding:8px 18px;
            border-radius:8px;
            font-weight:600;
        }

        QPushButton#start{
            background:#10B981;
            color:white;
        }

        QPushButton#start:hover{
            background:white;
            color:#10B981;
            border:2px solid #10B981;
        }

        QPushButton#start:pressed{
            background:white;
            color:#10B981;
            border:2px solid #10B981;
        }

        QPushButton#clear{
            background:#EC4899;
            color:white;
        }

        PushButton#clear:hover{
            background:white;
            color:#EC4899;
            border:2px solid #EC4899;
        }

        QPushButton#clear:pressed{
            background:white;
            color:#EC4899;
            border:2px solid #EC4899;
        }
                           
        QPushButton#prev,
        QPushButton#next{
            background:#ECFDF5;
            color:#065F46;
            border:1px solid #A7F3D0;
        }

        QPushButton#prev:hover,
        QPushButton#next:hover{
            background:#D1FAE5;
        }

        QPushButton#prev:pressed,
        QPushButton#next:pressed{
            background:#A7F3D0;
        }

        QFrame{
            background:#FFF9FB;
            border-radius:14px;
            padding:12px;
        }

        QTableWidget{
            border:none;
            background:#F0FDF4;
        }

        QHeaderView::section{
            background:#FCE7F3;
            color:#9D174D;
            border:none;
            border-bottom:2px solid #F9A8D4;
            padding:4px;
            font-weight:700;
        }

        QTableWidget::item{
            padding:8px;
            background:#F7FEFA;
        }

        QTableWidget::item:hover{
            background:#ECFDF5;
        }

        QScrollBar:vertical{
            background:#F1F5F9;
            width:8px;
        }

        QScrollBar::handle:vertical{
            background:#CBD5E1;
            border-radius:4px;
        }

        QScrollBar::handle:vertical:hover{
            background:#94A3B8;
        }

        """)

        self.start_button.setObjectName("start")
        self.clear_button.setObjectName("clear")
        self.prev_button.setObjectName("prev")
        self.next_button.setObjectName("next")

    # START SCRAPING
    def start_scraping(self):

        url = self.url_input.text()

        if not url:
            self.status_label.setText("Status: URL kosong")
            return

        # Reset data dan tabel
        self.all_data = []
        self.current_page = 0
        self.table.setRowCount(0)

        # Disable tombol selama scraping
        self.start_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.export_csv_button.setEnabled(False)
        self.export_excel_button.setEnabled(False)

        self.status_label.setText("Status: Memulai scraping...")

        # Buat worker thread dan hubungkan signal
        self.worker = ScraperWorker(url, batas_berita=10, jumlah_halaman=2, delay=2)
        self.worker.progress.connect(self.on_progress)
        self.worker.article_scraped.connect(self.on_article_scraped)
        self.worker.finished_signal.connect(self.on_scraping_finished)
        self.worker.error.connect(self.on_scraping_error)
        self.worker.start()

    # SLOT: MENERIMA UPDATE PROGRESS
    def on_progress(self, message):
        self.status_label.setText(f"Status: {message}")

    # SLOT: MENERIMA SATU ARTIKEL SECARA BERTAHAP
    def on_article_scraped(self, article):
        self.all_data.append(article)

        # Tampilkan langsung di tabel
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

        title_item = QTableWidgetItem(article["judul"])
        title_item.setForeground(Qt.blue)
        title_item.setData(Qt.UserRole, article.get("url", ""))
        self.table.setItem(row, 1, title_item)

        date_text = article.get("tanggal", "Tanggal tidak tersedia")
        if date_text:
            try:
                date_obj = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                formatted_date = date_obj.strftime("%d/%m/%Y")
            except Exception:
                formatted_date = str(date_text)[:20]
        else:
            formatted_date = "Tanggal tidak tersedia"

        self.table.setItem(row, 2, QTableWidgetItem(formatted_date))

        content = article["isi"][:700]
        self.table.setItem(row, 3, QTableWidgetItem(content))

        self.table.resizeRowsToContents()

        # Update pagination label
        total_pages = max(1, (len(self.all_data) - 1) // self.items_per_page + 1)
        self.page_label.setText(f"Page {self.current_page + 1} / {total_pages}")

    # SLOT: SCRAPING SELESAI
    def on_scraping_finished(self):
        # Re-enable semua tombol
        self.start_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.export_csv_button.setEnabled(True)
        self.export_excel_button.setEnabled(True)

        if not self.all_data:
            self.status_label.setText("Status: Tidak ada berita ditemukan")
        else:
            self.status_label.setText(f"Status: Scraping selesai — {len(self.all_data)} berita")
            self.current_page = 0
            self.display_page()

        self.worker = None

    # SLOT: SCRAPING ERROR
    def on_scraping_error(self, error_message):
        self.status_label.setText("Status: Scraping gagal")
        QMessageBox.warning(
            self,
            "Scraping Error",
            f"{error_message}\n\nKemungkinan website terlalu lama merespon atau terjadi timeout."
        )

    # DISPLAY RESULTS
    def display_results(self, data):

        for i, news in enumerate(data):

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(i + 1)))

            title_item = QTableWidgetItem(news["judul"])
            title_item.setForeground(Qt.blue)
            title_item.setData(Qt.UserRole, news.get("url", ""))

            self.table.setItem(row, 1, title_item)

            date_text = news.get("tanggal", "Tanggal tidak tersedia")

            if date_text:
                try:
                    date_obj = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                except Exception:
                    formatted_date = str(date_text)[:20]
            else:
                formatted_date = "Tanggal tidak tersedia"

            self.table.setItem(row, 2, QTableWidgetItem(formatted_date))

            content = news["isi"][:700]

            self.table.setItem(row, 3, QTableWidgetItem(content))

        self.table.resizeRowsToContents()

    # DISPLAY PAGINATION
    def display_page(self):

        self.table.setRowCount(0)

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page

        page_data = self.all_data[start:end]

        for i, news in enumerate(page_data):

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(start + i + 1)))

            title_item = QTableWidgetItem(news["judul"])
            title_item.setForeground(Qt.blue)
            title_item.setData(Qt.UserRole, news["url"])

            self.table.setItem(row, 1, title_item)

            date_text = news["tanggal"]

            try:
                date_obj = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                formatted = date_obj.strftime("%d/%m/%Y")
            except:
                formatted = date_text

            self.table.setItem(row, 2, QTableWidgetItem(formatted))

            content = news["isi"][:700]
            self.table.setItem(row, 3, QTableWidgetItem(content))

        self.table.resizeRowsToContents()

        total_pages = (len(self.all_data) - 1) // self.items_per_page + 1
        self.page_label.setText(f"Page {self.current_page + 1} / {total_pages}")

    # OPEN ARTICLE
    def open_article(self, row, column):

        if column == 1:

            item = self.table.item(row, column)

            if item:

                url = item.data(Qt.UserRole)

                if url:
                    QDesktopServices.openUrl(QUrl(url))

    # PREVIOUS PAGE
    def prev_page(self):

        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()


    # NEXT PAGE
    def next_page(self):

        if (self.current_page + 1) * self.items_per_page < len(self.all_data):
            self.current_page += 1
            self.display_page()

    # CLEAR TABLE
    def clear_table(self):

        self.table.setRowCount(0)
        self.status_label.setText("Status: Table cleared")

    # EXPORT CSV
    def export_csv(self):
        if not self.all_data:
            QMessageBox.warning(self, "Export Error", "Tidak ada data untuk diexport.")
            return
        try:
            filename = export_to_csv(self.all_data)
            QMessageBox.information(self, "Export Success", f"Data berhasil diexport ke {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Gagal export CSV: {str(e)}")

    # EXPORT EXCEL
    def export_excel(self):
        if not self.all_data:
            QMessageBox.warning(self, "Export Error", "Tidak ada data untuk diexport.")
            return
        try:
            filename = export_to_excel(self.all_data)
            QMessageBox.information(self, "Export Success", f"Data berhasil diexport ke {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Gagal export Excel: {str(e)}")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = NewsScraperGUI()
    window.show()

    sys.exit(app.exec_())