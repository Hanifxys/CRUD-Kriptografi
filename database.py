import mysql.connector
from mysql.connector import Error
import config # Import konfigurasi dari config.py
import logging
import time

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_connection(max_retries=5, retry_delay=5):
    """
    Membuat koneksi ke database MySQL menggunakan konfigurasi dari `config.py`.
    Akan mencoba kembali koneksi jika gagal, hingga `max_retries` kali.

    Args:
        max_retries (int): Jumlah maksimum percobaan ulang koneksi.
        retry_delay (int): Penundaan (dalam detik) antara setiap percobaan ulang.

    Returns:
        mysql.connector.connection.MySQLConnection: Objek koneksi jika berhasil.

    Raises:
        mysql.connector.Error: Jika koneksi ke database gagal setelah semua percobaan.
    """
    connection = None
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Mencoba koneksi ke database (Percobaan {attempt}/{max_retries})...")
            connection = mysql.connector.connect(**config.DB_CONFIG)
            if connection.is_connected():
                logging.info("Koneksi ke database MySQL berhasil!")
                return connection
        except Error as e:
            logging.warning(f"Gagal terhubung ke MySQL pada percobaan {attempt}: {e}")
            if attempt < max_retries:
                logging.info(f"Menunggu {retry_delay} detik sebelum mencoba lagi...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Gagal terhubung ke MySQL setelah {max_retries} percobaan.")
                raise # Melempar kembali exception setelah semua percobaan gagal
    return connection

def close_connection(connection):
    """
    Menutup koneksi database MySQL yang diberikan.

    Args:
        connection (mysql.connector.connection.MySQLConnection): Objek koneksi yang akan ditutup.
    """
    if connection and connection.is_connected():
        connection.close()
        logging.info("Koneksi database MySQL ditutup.")

if __name__ == "__main__":
    # Contoh penggunaan dengan penanganan error yang lebih baik
    conn = None
    try:
        conn = create_connection()
        if conn:
            logging.info("Koneksi berhasil dibuat dalam contoh penggunaan.")
            # Lakukan operasi database di sini
            pass
    except Error as e:
        logging.error(f"Gagal terhubung ke database dalam contoh penggunaan: {e}")
    finally:
        if conn:
            close_connection(conn)
