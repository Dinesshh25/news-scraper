import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame
)

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from scraper import jalankan_scraper


class NewsScraperGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("News Scraper Tool")
        self.setGeometry(200, 200, 1150, 650)

        main_layout = QVBoxLayout()

        # ======================
        # TITLE
        # ======================

        title = QLabel("📰 News Scraper Dashboard")
        title.setStyleSheet("""
        font-size:28px;
        font-weight:700;
        color:#2C3E50;
        margin-bottom:12px;
        """)

        # ======================
        # INPUT AREA
        # ======================

        input_layout = QHBoxLayout()

        label = QLabel("News URL")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://indeks.kompas.com/")

        self.start_button = QPushButton("Start Scraping")
        self.clear_button = QPushButton("Clear Table")

        input_layout.addWidget(label)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.start_button)
        input_layout.addWidget(self.clear_button)

        # ======================
        # STATUS
        # ======================

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color:#64748B;font-weight:500;")

        # ======================
        # CARD CONTAINER
        # ======================

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

        # ======================
        # LAYOUT
        # ======================

        main_layout.addWidget(title)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        # ======================
        # EVENTS
        # ======================

        self.start_button.clicked.connect(self.start_scraping)
        self.clear_button.clicked.connect(self.clear_table)

        # ======================
        # STYLE
        # ======================

        self.setStyleSheet("""

        QWidget{
            background:#F4F7FB;
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
            border:1px solid #E5E7EB;
            border-radius:8px;
        }

        QPushButton{
            padding:8px 18px;
            border-radius:8px;
            font-weight:600;
        }

        QPushButton#start{
            background:#3B82F6;
            color:white;
        }

        QPushButton#start:hover{
            background:#2563EB;
        }

        QPushButton#start:pressed{
            background:white;
            color:#3B82F6;
            border:2px solid #3B82F6;
        }

        QPushButton#clear{
            background:#EF4444;
            color:white;
        }

        QPushButton#clear:hover{
            background:#DC2626;
        }

        QPushButton#clear:pressed{
            background:white;
            color:#EF4444;
            border:2px solid #EF4444;
        }

        QFrame{
            background:white;
            border-radius:14px;
            padding:12px;
        }

        QTableWidget{
            border:none;
            background:white;
        }

        QHeaderView::section{
            background:#E2E8F0;
            color:#1F2937;
            border:none;
            border-bottom:2px solid #CBD5E1;
            padding:4px;
            font-weight:700;
        }

        QTableWidget::item{
            padding:8px;
        }

        QTableWidget::item:hover{
            background:#EEF2FF;
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

    # ======================
    # START SCRAPING
    # ======================

    def start_scraping(self):

        url = self.url_input.text()

        if not url:
            self.status_label.setText("Status: URL kosong")
            return

        self.status_label.setText("Status: Scraping sedang berjalan...")

        self.table.setRowCount(0)

        results = jalankan_scraper(url)

        self.display_results(results)

        self.status_label.setText("Status: Scraping selesai")

    # ======================
    # DISPLAY RESULTS
    # ======================

    def display_results(self, data):

        for i, news in enumerate(data):

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(i + 1)))

            title_item = QTableWidgetItem(news["judul"])
            title_item.setForeground(Qt.blue)
            title_item.setData(Qt.UserRole, news["url"])

            self.table.setItem(row, 1, title_item)

            date_text = news["tanggal"]

            try:
                date_obj = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                formatted_date = date_obj.strftime("%d/%m/%Y")
            except:
                formatted_date = date_text

            self.table.setItem(row, 2, QTableWidgetItem(formatted_date))

            content = news["isi"][:700]

            self.table.setItem(row, 3, QTableWidgetItem(content))

        self.table.resizeRowsToContents()

    # ======================
    # OPEN ARTICLE
    # ======================

    def open_article(self, row, column):

        if column == 1:

            item = self.table.item(row, column)

            if item:

                url = item.data(Qt.UserRole)

                if url:
                    QDesktopServices.openUrl(QUrl(url))

    # ======================
    # CLEAR TABLE
    # ======================

    def clear_table(self):

        self.table.setRowCount(0)
        self.status_label.setText("Status: Table cleared")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = NewsScraperGUI()
    window.show()

    sys.exit(app.exec_())