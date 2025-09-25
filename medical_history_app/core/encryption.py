"""
Encryption utilities for HIPAA-compliant data protection.
"""
import base64
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive medical data.
    """
    
    def __init__(self):
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not encryption_key:
            raise ImproperlyConfigured("ENCRYPTION_KEY must be set in settings")
        
        try:
            # Ensure key is bytes
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            self.cipher_suite = Fernet(encryption_key)
        except Exception as e:
            raise ImproperlyConfigured(f"Invalid encryption key: {e}")
    
    def encrypt(self, data):
        """
        Encrypt data and return base64 encoded string.
        """
        if data is None:
            return None
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.cipher_suite.encrypt(data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """
        Decrypt base64 encoded string and return original data.
        """
        if encrypted_data is None:
            return None
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            
            return decrypted_data.decode('utf-8')
        except Exception:
            # If decryption fails, assume data was not encrypted
            return encrypted_data


# Global encryption service instance
encryption_service = EncryptionService()


def encrypt_field(value):
    """
    Convenience function for encrypting field values.
    """
    return encryption_service.encrypt(value)


def decrypt_field(value):
    """
    Convenience function for decrypting field values.
    """
    return encryption_service.decrypt(value)