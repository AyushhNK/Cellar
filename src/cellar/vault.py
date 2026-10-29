"""Encrypted vault storage.

Vault = one JSON file. Key = Argon2id(master password); data = AES-256-GCM.
The KDF header is bound as AAD, so tampering with the file fails decryption.
"""
import base64
import json
import os
import secrets
import string
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

KDF = {"memory_cost": 256 * 1024, "iterations": 3, "lanes": 4}  # Argon2id, 256 MiB


def b64e(b):
    return base64.b64encode(b).decode()


def derive_key(password, salt, kdf):
    return Argon2id(salt=salt, length=32, **kdf).derive(password.encode())


def generate_password(n=24):
    classes = (string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation)
    alphabet = "".join(classes)
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(n))
        if all(any(c in cls for c in pw) for cls in classes):
            return pw


class Vault:
    def __init__(self, path):
        self.path = Path(path)
        self.entries = []
        self._key = self._header = None

    def exists(self):
        return self.path.exists()

    def set_password(self, password):
        """Create the vault, or re-key it with a new master password and fresh salt."""
        self._header = {"v": 1, "salt": b64e(os.urandom(16)), "kdf": KDF}
        self._key = derive_key(password, base64.b64decode(self._header["salt"]), KDF)
        self.save()

    def unlock(self, password):
        """Raises InvalidTag on wrong password or tampered file."""
        data = json.loads(self.path.read_text())
        header = data["header"]
        key = derive_key(password, base64.b64decode(header["salt"]), header["kdf"])
        plain = AESGCM(key).decrypt(base64.b64decode(data["nonce"]), base64.b64decode(data["ct"]), self._aad(header))
        self._header, self._key, self.entries = header, key, json.loads(plain)

    def save(self):
        nonce = os.urandom(12)
        ct = AESGCM(self._key).encrypt(nonce, json.dumps(self.entries).encode(), self._aad(self._header))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        # Write-then-rename so a crash mid-save never corrupts the existing vault.
        with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as f:
            json.dump({"header": self._header, "nonce": b64e(nonce), "ct": b64e(ct)}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    def lock(self):
        self._key = None
        self.entries = []

    @staticmethod
    def _aad(header):
        return json.dumps(header, sort_keys=True).encode()
