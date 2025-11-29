import database
import xor_cipher
from mysql.connector import Error
import config # Import konfigurasi dari config.py
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_user(username, email, password):
    """
    Membuat pengguna baru dengan kata sandi terenkripsi.

    Args:
        username (str): Nama pengguna.
        email (str): Alamat email pengguna.
        password (str): Kata sandi pengguna (plaintext).

    Returns:
        bool: True jika pengguna berhasil ditambahkan, False jika gagal.
    """
    if not all([username, email, password]):
        logging.warning("Input username, email, dan password tidak boleh kosong.")
        return False

    encrypted_password = xor_cipher.xor_encrypt_decrypt(password, config.SECRET_KEY)
    
    conn = None
    try:
        conn = database.create_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO users (username, email, password_encrypted) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, encrypted_password.encode('utf-8'))) # Encode kembali ke bytes untuk VARBINARY
            conn.commit()
            logging.info(f"Pengguna '{username}' berhasil ditambahkan.")
            return True
    except Error as e:
        logging.error(f"Error saat menambahkan pengguna '{username}': {e}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan tak terduga saat membuat pengguna '{username}': {e}")
    finally:
        if conn:
            database.close_connection(conn)
    return False

def get_all_users():
    """
    Mengambil semua pengguna dari database dan mendekripsi kata sandi mereka.

    Returns:
        list: Daftar dictionary yang berisi data pengguna, termasuk kata sandi yang didekripsi.
              Mengembalikan list kosong jika tidak ada pengguna atau terjadi error.
    """
    conn = None
    users = []
    try:
        conn = database.create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True) # Mengembalikan hasil sebagai dictionary
            query = "SELECT id, username, email, password_encrypted, created_at FROM users"
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                # Dekripsi kata sandi
                encrypted_password_b64 = row['password_encrypted'].decode('utf-8')
                row['password'] = xor_cipher.xor_decrypt(encrypted_password_b64, config.SECRET_KEY)
                del row['password_encrypted'] # Hapus kolom terenkripsi
                users.append(row)
    except Error as e:
        logging.error(f"Error saat mengambil semua pengguna: {e}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan tak terduga saat mengambil semua pengguna: {e}")
    finally:
        if conn:
            database.close_connection(conn)
    return users

def get_user_by_username(username):
    """
    Mengambil pengguna berdasarkan username dan mendekripsi kata sandi mereka.

    Args:
        username (str): Nama pengguna yang akan dicari.

    Returns:
        dict: Dictionary yang berisi data pengguna jika ditemukan, termasuk kata sandi yang didekripsi.
              Mengembalikan None jika pengguna tidak ditemukan atau terjadi error.
    """
    if not username:
        logging.warning("Input username tidak boleh kosong.")
        return None

    conn = None
    user = None
    try:
        conn = database.create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, username, email, password_encrypted, created_at FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                # Dekripsi kata sandi
                encrypted_password_b64 = result['password_encrypted'].decode('utf-8')
                result['password'] = xor_cipher.xor_decrypt(encrypted_password_b64, config.SECRET_KEY)
                del result['password_encrypted'] # Hapus kolom terenkripsi
                user = result
    except Error as e:
        logging.error(f"Error saat mengambil pengguna '{username}': {e}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan tak terduga saat mengambil pengguna '{username}': {e}")
    finally:
        if conn:
            database.close_connection(conn)
    return user

def update_user(username, new_email=None, new_password=None):
    """
    Memperbarui informasi pengguna (email dan/atau kata sandi).
    Kata sandi baru akan dienkripsi sebelum disimpan.

    Args:
        username (str): Nama pengguna yang akan diperbarui.
        new_email (str, optional): Alamat email baru. Defaults to None.
        new_password (str, optional): Kata sandi baru (plaintext). Defaults to None.

    Returns:
        bool: True jika pengguna berhasil diperbarui, False jika gagal.
    """
    if not username:
        logging.warning("Input username tidak boleh kosong.")
        return False

    if not new_email and not new_password:
        logging.warning("Tidak ada data yang disediakan untuk diperbarui (email atau password baru). ")
        return False

    conn = None
    try:
        conn = database.create_connection()
        if conn:
            cursor = conn.cursor()
            updates = []
            params = []

            if new_email:
                updates.append("email = %s")
                params.append(new_email)
            if new_password:
                encrypted_password = xor_cipher.xor_encrypt_decrypt(new_password, config.SECRET_KEY)
                updates.append("password_encrypted = %s")
                params.append(encrypted_password.encode('utf-8'))
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE username = %s"
            params.append(username)
            
            cursor.execute(query, tuple(params))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Pengguna '{username}' berhasil diperbarui.")
                return True
            else:
                logging.warning(f"Pengguna '{username}' tidak ditemukan atau tidak ada perubahan.")
                return False
    except Error as e:
        logging.error(f"Error saat memperbarui pengguna '{username}': {e}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan tak terduga saat memperbarui pengguna '{username}': {e}")
    finally:
        if conn:
            database.close_connection(conn)
    return False

def delete_user(username):
    """
    Menghapus pengguna dari database berdasarkan username.

    Args:
        username (str): Nama pengguna yang akan dihapus.

    Returns:
        bool: True jika pengguna berhasil dihapus, False jika gagal.
    """
    if not username:
        logging.warning("Input username tidak boleh kosong.")
        return False

    conn = None
    try:
        conn = database.create_connection()
        if conn:
            cursor = conn.cursor()
            query = "DELETE FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Pengguna '{username}' berhasil dihapus.")
                return True
            else:
                logging.warning(f"Pengguna '{username}' tidak ditemukan.")
                return False
    except Error as e:
        logging.error(f"Error saat menghapus pengguna '{username}': {e}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan tak terduga saat menghapus pengguna '{username}': {e}")
    finally:
        if conn:
            database.close_connection(conn)
    return False

# Contoh penggunaan
if __name__ == "__main__":
    logging.info("--- Menguji operasi CREATE ---")
    create_user("john_doe", "john.doe@example.com", "secure_password_123")
    create_user("jane_smith", "jane.smith@example.com", "another_secure_pass")
    create_user("test_user", "test@example.com", "test_pass")

    logging.info("\n--- Menguji operasi READ ---")
    logging.info("Semua pengguna:")
    all_users = get_all_users()
    for user in all_users:
        safe_user = {k: v for k, v in user.items() if k != 'password'}
        logging.info(safe_user)

    logging.info("\nMencari pengguna 'john_doe':")
    john = get_user_by_username("john_doe")
    if john:
        logging.info(john)
    else:
        logging.info("Pengguna 'john_doe' tidak ditemukan.")

    logging.info("\nMencari pengguna yang tidak ada:")
    non_existent_user = get_user_by_username("non_existent")
    if non_existent_user:
        logging.info(non_existent_user)
    else:
        logging.info("Pengguna 'non_existent' tidak ditemukan.")

    logging.info("\n--- Menguji operasi UPDATE ---")
    logging.info("Memperbarui email 'john_doe':")
    update_user("john_doe", new_email="john.doe.new@example.com")
    john_updated = get_user_by_username("john_doe")
    if john_updated:
        logging.info(john_updated)

    logging.info("\nMemperbarui password 'jane_smith':")
    update_user("jane_smith", new_password="new_strong_pass")
    jane_updated = get_user_by_username("jane_smith")
    if jane_updated:
        logging.info(jane_updated)

    logging.info("\nMemperbarui email dan password 'test_user':")
    update_user("test_user", new_email="test_new@example.com", new_password="super_new_pass")
    test_updated = get_user_by_username("test_user")
    if test_updated:
        logging.info(test_updated)

    logging.info("\nMencoba memperbarui pengguna yang tidak ada:")
    update_user("non_existent_user", new_email="no@example.com")

    logging.info("\n--- Menguji operasi DELETE ---")
    logging.info("Menghapus pengguna 'john_doe':")
    delete_user("john_doe")
    logging.info("Memverifikasi bahwa 'john_doe' telah dihapus:")
    john_deleted = get_user_by_username("john_doe")
    if not john_deleted:
        logging.info("Pengguna 'john_doe' berhasil dihapus.")

    logging.info("\nMencoba menghapus pengguna yang tidak ada:")
    delete_user("non_existent_user")

    logging.info("\n--- Semua pengguna setelah operasi DELETE ---")
    all_users_final = get_all_users()
    for user in all_users_final:
        logging.info(user)


