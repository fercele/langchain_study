import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def generate_key(passphrase: bytes) -> bytes:
    salt = os.urandom(16)  # generate a random salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000  # adjust the number of iterations as needed
    )
    key = kdf.derive(passphrase)
    return key, salt

if __name__ == "__main__":
    file_location:str = input("Entre o caminho de uma pasta para salvar a chave criptográfica e o 'salt': (pasta atual) ")
    if file_location == "":
        file_location = os.getcwd()
        
    passphrase = input("Entre uma senha/passphrase (poderá ser usada junto com o salt caso perca a chave): ").encode()
    key, salt = generate_key(passphrase)
    with open(f"{file_location}/key", "wb") as f:
        f.write(key)
    with open(f"{file_location}/salt", "wb") as f:
        f.write(salt)
    
    print(f"Arquivos de chave e 'salt' gerados com sucesso na pasta {file_location}")

