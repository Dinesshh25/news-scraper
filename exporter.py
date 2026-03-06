import pandas as pd
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def validate_data(data):
    """Validasi data agar tidak kosong"""
    if not data:
        raise ValueError("Data scraping kosong, tidak dapat diexport.")
    for item in data:
        if not item.get('judul') or not item.get('isi'):
            raise ValueError("Data berita tidak lengkap: judul atau isi kosong.")
    return True

def export_to_csv(data, filename=None):
    """Export data ke CSV"""
    try:
        validate_data(data)
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_scraping_{timestamp}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logging.info(f"Data berhasil diexport ke CSV: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error exporting to CSV: {str(e)}")
        raise

def export_to_excel(data, filename=None):
    """Export data ke Excel"""
    try:
        validate_data(data)
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_scraping_{timestamp}.xlsx"
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine='openpyxl')
        logging.info(f"Data berhasil diexport ke Excel: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error exporting to Excel: {str(e)}")
        raise
