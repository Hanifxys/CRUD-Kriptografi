# config.py

# Konfigurasi database MySQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'crud_db',
    'user': 'user',
    'password': 'password'
}

# Kunci rahasia untuk enkripsi/dekripsi.
# PENTING: Dalam aplikasi nyata, ini harus diambil dari variabel lingkungan
# atau sistem manajemen kunci yang aman, BUKAN disimpan langsung di kode.
SECRET_KEY = "my_super_secret_key_123" # Ganti dengan kunci yang lebih kuat dan aman!
