import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def encrypt_api_key_using_key(crypto_key:bytes, api_key:bytes) -> bytes:
    fernet = Fernet(base64.urlsafe_b64encode(crypto_key))
    encrypted_password = fernet.encrypt(api_key)
    return encrypted_password

if __name__ == "__main__":
    path_to_existing_key:str = input("Entre o caminho completo da chave criptográfica: (key na pasta atual) ")
    if path_to_existing_key == "":
        path_to_existing_key = os.path.join(os.getcwd(), "key")

    api_key_to_encrypt:str = input("Cole (botão direito) a api key: ")
    path_to_store_api_key:str = input("Entre o caminho da pasta onde deseja salvar a api key criptografada (pasta atual): ")
    if path_to_store_api_key == "":
        path_to_store_api_key = os.getcwd()

    with open(path_to_existing_key, "rb") as f:
        crypto_key: bytes = f.read()

    encrypted_api_key: bytes = encrypt_api_key_using_key(crypto_key, api_key_to_encrypt.encode())
    
    with open(f"{path_to_store_api_key}/api_key", "wb") as f:
        f.write(encrypted_api_key)

    print(f"API key criptografada e armazenada em {path_to_store_api_key}/api_key")
