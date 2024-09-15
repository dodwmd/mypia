import pytest
from personal_ai_assistant.utils.encryption import EncryptionManager


@pytest.fixture
def encryption_manager():
    key = EncryptionManager.generate_key("test_password")
    return EncryptionManager(key)


def test_encrypt_decrypt(encryption_manager):
    original_text = "This is a secret message"
    encrypted = encryption_manager.encrypt(original_text)
    decrypted = encryption_manager.decrypt(encrypted)
    assert decrypted == original_text


def test_hash_password():
    password = "secure_password123"
    hashed = EncryptionManager.hash_password(password)
    assert EncryptionManager.verify_password(hashed, password)
    assert not EncryptionManager.verify_password(hashed, "wrong_password")


def test_generate_key():
    key1 = EncryptionManager.generate_key("password1")
    key2 = EncryptionManager.generate_key("password2")
    assert key1 != key2
