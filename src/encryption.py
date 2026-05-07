"""Encryption utilities for sensitive data"""
import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class FieldEncryption:
    """Encrypt and decrypt sensitive fields"""

    def __init__(self):
        # Generate key from SECRET_KEY environment variable
        secret = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

        # Derive a Fernet key from the secret using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'luxury_travel_salt_v1',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        try:
            if not plaintext:
                return None
            ciphertext = self.cipher.encrypt(plaintext.encode())
            return ciphertext.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string"""
        try:
            if not ciphertext:
                return None
            plaintext = self.cipher.decrypt(ciphertext.encode())
            return plaintext.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None


# Global encryption instance
field_encryption = FieldEncryption()
