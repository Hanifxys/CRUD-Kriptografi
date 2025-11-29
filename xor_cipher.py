import base64
import config # Import konfigurasi dari config.py

def xor_encrypt_decrypt(data: str, key: str) -> str:
    """
    Melakukan enkripsi/dekripsi menggunakan Stream XOR cipher.
    Karena XOR adalah operasi simetris, fungsi yang sama dapat digunakan untuk
    enkripsi dan dekripsi.

    Args:
        data (str): Data plaintext untuk dienkripsi, atau data ciphertext untuk didekripsi.
        key (str): Kunci rahasia yang digunakan untuk operasi XOR.

    Returns:
        str: Data ciphertext (jika input adalah plaintext) atau data plaintext (jika input adalah ciphertext).
             Output akan di-encode base64 agar aman untuk disimpan/ditransmisikan.
    """
    # Konversi data dan kunci ke bytes
    data_bytes = data.encode('utf-8')
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)

    # Lakukan operasi XOR
    xored_bytes = bytearray()
    for i in range(len(data_bytes)):
        xored_bytes.append(data_bytes[i] ^ key_bytes[i % key_len])

    # Encode hasil XOR ke base64 agar aman untuk disimpan/ditransmisikan
    return base64.b64encode(xored_bytes).decode('utf-8')

def xor_decrypt(encrypted_data_b64: str, key: str) -> str:
    """
    Melakukan dekripsi data yang telah dienkripsi dengan Stream XOR dan di-encode base64.

    Args:
        encrypted_data_b64 (str): Data ciphertext yang di-encode base64.
        key (str): Kunci rahasia yang digunakan untuk dekripsi.

    Returns:
        str: Data plaintext yang telah didekripsi.
    """
    # Decode data base64 terlebih dahulu
    decoded_bytes = base64.b64decode(encrypted_data_b64)

    # Konversi kunci ke bytes
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)

    # Lakukan operasi XOR untuk dekripsi
    decrypted_bytes = bytearray()
    for i in range(len(decoded_bytes)):
        decrypted_bytes.append(decoded_bytes[i] ^ key_bytes[i % key_len])

    # Decode bytes hasil dekripsi kembali ke string UTF-8
    return decrypted_bytes.decode('utf-8')

# Contoh penggunaan
if __name__ == "__main__":
    # Contoh penggunaan dengan kunci dari konfigurasi
    secret_key = config.SECRET_KEY
    original_text = "Ini adalah data sensitif yang perlu dienkripsi."

    print(f"Original: {original_text}")

    # Enkripsi
    encrypted_text_b64 = xor_encrypt_decrypt(original_text, secret_key)
    print(f"Encrypted (Base64): {encrypted_text_b64}")

    # Dekripsi
    decrypted_text = xor_decrypt(encrypted_text_b64, secret_key)
    print(f"Decrypted: {decrypted_text}")

    # Uji dengan data lain
    another_text = "PasswordPengguna123!"
    encrypted_another = xor_encrypt_decrypt(another_text, secret_key)
    decrypted_another = xor_decrypt(encrypted_another, secret_key)
    print(f"\nOriginal (another): {another_text}")
    print(f"Encrypted (another): {encrypted_another}")
    print(f"Decrypted (another): {decrypted_another}")

    assert original_text == decrypted_text
    assert another_text == decrypted_another
    print("\nTes enkripsi/dekripsi berhasil!")
