import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def generate_key(passphrase: bytes, salt: bytes) -> bytes:
    # print(f"Usando passphrase: {passphrase}")
    # print(f"Usando salt: {salt}")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000  # adjust the number of iterations as needed
    )
    key = kdf.derive(passphrase)
    return key

def decrypt_api_key_using_passphrase(passphrase:bytes, salt:bytes, api_key:bytes) -> bytes:
    derived_key = generate_key(passphrase, salt)
    fernet = Fernet(base64.urlsafe_b64encode(derived_key))
    decrypted_password = fernet.decrypt(api_key)
    return decrypted_password

def decrypt_api_key_using_key(crypto_key:bytes, api_key:bytes) -> bytes:
    fernet = Fernet(base64.urlsafe_b64encode(crypto_key))
    decrypted_password = fernet.decrypt(api_key)
    return decrypted_password

def decrypt_api_key(path_to_key_file:str, path_to_encrypted_api_key:str) -> str:
    with open(path_to_key_file, "rb") as f:
        crypto_key = f.read()
    with open(path_to_encrypted_api_key, "rb") as f:
        encrypted_api_key = f.read()

    result:bytes = decrypt_api_key_using_key(crypto_key, encrypted_api_key)
    return result.decode()

def get_api_key(prefix: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # print(__file__) #/home/celestino_wsl/dev/otimizai/langchain/workspace/quickstart/../gerenciador_api_keys/recupera_api_key.py
    # print(os.path.abspath(__file__)) #/home/celestino_wsl/dev/otimizai/langchain/workspace/gerenciador_api_keys/recupera_api_key.py
    # print(os.path.dirname(os.path.abspath(__file__))) #/home/celestino_wsl/dev/otimizai/langchain/workspace/gerenciador_api_keys/recupera_api_key.py

    path_to_key_file = os.environ.get('CRYPTO_KEY_FILE', os.path.join(current_dir, "key"))
    path_to_encrypted_api_key = os.environ.get('ENCRYPTED_API_KEY_FILE', os.path.join(current_dir, f"{prefix}_api_key"))

    # print(f"Usando arquivo de chave criptográfica: {path_to_key_file}")
    # print(f"Usando arquivo de api key criptografada: {path_to_encrypted_api_key}")

    return decrypt_api_key(path_to_key_file, path_to_encrypted_api_key)


if __name__ == "__main__":
    opcao = input("Digite 1 para usar um arquivo de chaves ou 2 para usar uma passphrase e o arquivo de salt (1): ")
    if opcao == "" or opcao == "1":
        path_to_existing_key:str = input("Caminho do arquivo de chave criptográfica (pasta atual/key): ")
        if path_to_existing_key == "":
            path_to_existing_key = os.path.join(os.getcwd(), "key")

        path_to_encrypted_api_key:str = input("Camiho do arquivo da api key criptografada (pasta atual/api_key): ")
        if path_to_encrypted_api_key == "":
            path_to_encrypted_api_key = os.path.join(os.getcwd(), "api_key")

        decrypted_api_key:str = decrypt_api_key(path_to_existing_key, path_to_encrypted_api_key)

    elif opcao == "2":
        passphrase = input("Senha/passphrase: ").encode()
        path_to_salt:str = input("Caminho do arquivo de salt (pasta atual/salt): ")
        if path_to_salt == "":
            path_to_salt = os.path.join(os.getcwd(), "salt")


        path_to_encrypted_api_key:str = input("Caminho do arquivo com a api key criptografada (pasta atual/api key): ")
        if path_to_encrypted_api_key == "":
            path_to_encrypted_api_key = os.path.join(os.getcwd(), "api_key")

        with open(path_to_salt, "rb") as f:
            salt = f.read()
        with open(path_to_encrypted_api_key, "rb") as f:
            encrypted_api_key = f.read()

        decrypted_api_key:str = decrypt_api_key_using_passphrase(passphrase, salt, encrypted_api_key).decode()

    else:
        raise ValueError("Opção inválida")
    
    print(f"API key: {decrypted_api_key}")
