"""Vault round-trip and tamper checks. Run: python tests/test_vault.py (or pytest)."""
import json
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidTag

from cellar import vault

vault.KDF = {"memory_cost": 8 * 1024, "iterations": 1, "lanes": 1}  # fast for tests


def raises(fn):
    try:
        fn()
    except InvalidTag:
        return True
    return False


def test_vault():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "vault.json"
        v = vault.Vault(path)
        v.set_password("correct horse battery")
        v.entries.append({"site": "example.com", "username": "me", "password": "s3cret!", "notes": ""})
        v.save()
        assert b"s3cret" not in path.read_bytes()

        v2 = vault.Vault(path)
        v2.unlock("correct horse battery")
        assert v2.entries[0]["password"] == "s3cret!"
        assert raises(lambda: vault.Vault(path).unlock("wrong password!!"))

        # Weakening the KDF params in the file must break decryption (header is AAD).
        data = json.loads(path.read_text())
        data["header"]["kdf"]["iterations"] = 2
        path.write_text(json.dumps(data))
        assert raises(lambda: vault.Vault(path).unlock("correct horse battery"))

        # Re-key keeps entries.
        v2.set_password("new master password")
        v3 = vault.Vault(path)
        v3.unlock("new master password")
        assert v3.entries == v2.entries


def test_generate_password():
    pw = vault.generate_password()
    assert len(pw) == 24 and any(c.isdigit() for c in pw) and any(c.isupper() for c in pw)


if __name__ == "__main__":
    test_vault()
    test_generate_password()
    print("ok")
