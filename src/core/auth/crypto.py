import hashlib
import json
import random
import string
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


CHALLENGE_SECRET = "rpa_hard_challenge_2026"
EXTREME_SECRET = "extreme_secret_key"

def generate_timestamp() -> str:
    return str(int(time.time() * 1000))


def generate_nonce(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_challenge(timestamp: str, nonce: str) -> str:
    raw = f"{timestamp}{nonce}{CHALLENGE_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()


def solve_pow(prefix: str, difficulty: int) -> str:
    """Brute-force proof-of-work: find nonce whose SHA-256 starts with `difficulty` zeros."""
    target = "0" * difficulty
    nonce = 0

    while True:
        candidate = f"{prefix}{nonce}"
        if hashlib.sha256(candidate.encode()).hexdigest().startswith(target):
            return str(nonce)
        nonce += 1


def decrypt_payload(session_id: str, encrypted_payload: str) -> dict:
    """AES-CBC decrypt the server payload and return the parsed JSON."""
    iv_hex, cipher_hex = encrypted_payload.split(":")
    iv = bytes.fromhex(iv_hex)
    cipher_bytes = bytes.fromhex(cipher_hex)

    key = hashlib.sha256(f"{session_id}{EXTREME_SECRET}".encode()).digest()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(cipher_bytes) + decryptor.finalize()

    unpadder = PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return json.loads(data.decode())