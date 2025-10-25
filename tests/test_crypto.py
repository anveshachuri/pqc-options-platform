"""
Unit tests for cryptography module
"""

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crypto.kyber_crypto import KyberCrypto
from src.crypto.key_manager import KeyManager
from src.crypto.security_utils import SecurityUtils


class TestKyberCrypto:
    """Test Kyber cryptography"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.crypto = KyberCrypto()
    
    def test_key_generation(self):
        """Test key pair generation"""
        pub_key, priv_key = self.crypto.generate_keypair()
        
        assert pub_key is not None
        assert priv_key is not None
        assert len(pub_key) > 0
        assert len(priv_key) > 0
    
    def test_encryption_decryption_roundtrip(self):
        """Test encrypt-decrypt produces original data"""
        plaintext = b"Hello, Post-Quantum World!"
        pub_key, priv_key = self.crypto.generate_keypair()
        
        # Encrypt
        encrypted = self.crypto.hybrid_encrypt(plaintext, pub_key)
        
        # Decrypt
        decrypted = self.crypto.hybrid_decrypt(encrypted, pub_key, priv_key)
        
        assert decrypted == plaintext
    
    def test_different_keys_fail_decryption(self):
        """Test that wrong keys can't decrypt"""
        plaintext = b"Secret message"
        pub_key1, priv_key1 = self.crypto.generate_keypair()
        pub_key2, priv_key2 = self.crypto.generate_keypair()
        
        encrypted = self.crypto.hybrid_encrypt(plaintext, pub_key1)
        
        # Try to decrypt with wrong keys - should raise exception
        with pytest.raises(Exception):
            self.crypto.hybrid_decrypt(encrypted, pub_key2, priv_key2)
    
    @pytest.mark.skip(reason="Dilithium signatures not available on Windows - liboqs limitation")
    def test_signature_verification(self):
        """Test digital signature creation and verification"""
        message = b"Sign this message"
        pub_key, priv_key = self.crypto.generate_signing_keypair()
        
        # Sign
        signature = self.crypto.sign_message(message, priv_key)
        
        # Verify
        is_valid = self.crypto.verify_signature(message, signature, pub_key)
        
        assert is_valid is True
    
    @pytest.mark.skip(reason="Dilithium signatures not available on Windows - liboqs limitation")
    def test_invalid_signature_fails(self):
        """Test that tampered signatures fail verification"""
        message = b"Original message"
        tampered_message = b"Tampered message"
        pub_key, priv_key = self.crypto.generate_signing_keypair()
        
        signature = self.crypto.sign_message(message, priv_key)
        
        # Try to verify tampered message
        is_valid = self.crypto.verify_signature(tampered_message, signature, pub_key)
        
        assert is_valid is False
    
    def test_encrypt_large_data(self):
        """Test encryption of large data"""
        plaintext = b"X" * 1048576  # 1 MB
        pub_key, priv_key = self.crypto.generate_keypair()
        
        encrypted = self.crypto.hybrid_encrypt(plaintext, pub_key)
        decrypted = self.crypto.hybrid_decrypt(encrypted, pub_key, priv_key)
        
        assert decrypted == plaintext


class TestKeyManager:
    """Test key management"""
    
    def setup_method(self):
        """Setup test fixtures"""
        import tempfile
        self.test_dir = tempfile.mkdtemp()
        self.key_manager = KeyManager(self.test_dir)
        self.crypto = KyberCrypto()
    
    def teardown_method(self):
        """Cleanup test directory"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_keys(self):
        """Test saving and loading keys"""
        pub_key, priv_key = self.crypto.generate_keypair()
        
        # Save
        fingerprint = self.key_manager.save_keys(pub_key, priv_key)
        
        # Load
        loaded_pub, loaded_priv = self.key_manager.load_keys(fingerprint)
        
        assert loaded_pub == pub_key
        assert loaded_priv == priv_key
    
    def test_list_keys(self):
        """Test listing saved keys"""
        pub_key1, priv_key1 = self.crypto.generate_keypair()
        pub_key2, priv_key2 = self.crypto.generate_keypair()
        
        fp1 = self.key_manager.save_keys(pub_key1, priv_key1)
        fp2 = self.key_manager.save_keys(pub_key2, priv_key2)
        
        keys = self.key_manager.list_keys()
        
        assert len(keys) == 2
        assert any(k['fingerprint'] == fp1 for k in keys)
        assert any(k['fingerprint'] == fp2 for k in keys)
    
    def test_delete_keys(self):
        """Test key deletion"""
        pub_key, priv_key = self.crypto.generate_keypair()
        fingerprint = self.key_manager.save_keys(pub_key, priv_key)
        
        # Delete
        self.key_manager.delete_keys(fingerprint)
        
        # Try to load - should fail
        with pytest.raises(FileNotFoundError):
            self.key_manager.load_keys(fingerprint)


class TestSecurityUtils:
    """Test security utilities"""
    
    def test_constant_time_compare(self):
        """Test timing-safe comparison"""
        a = b"test_string"
        b = b"test_string"
        c = b"different_string"
        
        assert SecurityUtils.constant_time_compare(a, b) is True
        assert SecurityUtils.constant_time_compare(a, c) is False
    
    def test_secure_random_bytes(self):
        """Test secure random generation"""
        random1 = SecurityUtils.secure_random_bytes(32)
        random2 = SecurityUtils.secure_random_bytes(32)
        
        assert len(random1) == 32
        assert len(random2) == 32
        assert random1 != random2
    
    def test_zeroize_memory(self):
        """Test memory clearing"""
        data = bytearray(b"sensitive_data")
        SecurityUtils.zeroize_memory(data)
        
        assert all(byte == 0 for byte in data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])