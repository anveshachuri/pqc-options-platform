"""
Integration tests for end-to-end workflow
"""

import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crypto.kyber_crypto import KyberCrypto
from src.pricing.black_scholes import BlackScholes


class TestIntegration:
    """Test integrated workflows"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.crypto = KyberCrypto()
        self.pricer = BlackScholes()
    
    def test_encrypted_pricing_workflow(self):
        """Test complete encrypted pricing request flow"""
        # Generate keys
        server_pub, server_priv = self.crypto.generate_keypair()
        client_pub, client_priv = self.crypto.generate_keypair()
        
        # Create pricing request
        request = {
            'S': 100.0,
            'K': 100.0,
            'T': 1.0,
            'r': 0.05,
            'sigma': 0.2,
            'type': 'call'
        }
        
        # Encrypt request (client encrypts with server's public key)
        request_json = json.dumps(request).encode('utf-8')
        encrypted_request = self.crypto.hybrid_encrypt(request_json, server_pub)
        
        # Server decrypts
        decrypted_request = self.crypto.hybrid_decrypt(
            encrypted_request, server_pub, server_priv
        )
        request_data = json.loads(decrypted_request.decode('utf-8'))
        
        # Server prices option
        result = self.pricer.price_option(request_data)
        
        # Server encrypts response
        result_json = json.dumps(result).encode('utf-8')
        encrypted_response = self.crypto.hybrid_encrypt(result_json, client_pub)
        
        # Client decrypts response
        decrypted_response = self.crypto.hybrid_decrypt(
            encrypted_response, client_pub, client_priv
        )
        final_result = json.loads(decrypted_response.decode('utf-8'))
        
        # Verify result
        assert 'price' in final_result
        assert final_result['price'] > 0
        assert 'delta' in final_result
    
    def test_batch_pricing(self):
        """Test batch pricing of multiple options"""
        pub_key, priv_key = self.crypto.generate_keypair()
        
        options = [
            {'S': 100, 'K': 90, 'T': 1.0, 'r': 0.05, 'sigma': 0.2, 'type': 'call'},
            {'S': 100, 'K': 100, 'T': 1.0, 'r': 0.05, 'sigma': 0.2, 'type': 'call'},
            {'S': 100, 'K': 110, 'T': 1.0, 'r': 0.05, 'sigma': 0.2, 'type': 'call'},
        ]
        
        results = []
        for option in options:
            # Encrypt
            request_json = json.dumps(option).encode('utf-8')
            encrypted = self.crypto.hybrid_encrypt(request_json, pub_key)
            
            # Decrypt and price
            decrypted = self.crypto.hybrid_decrypt(encrypted, pub_key, priv_key)
            option_data = json.loads(decrypted.decode('utf-8'))
            result = self.pricer.price_option(option_data)
            results.append(result)
        
        assert len(results) == 3
        # ITM call should be most expensive
        assert results[0]['price'] > results[1]['price'] > results[2]['price']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])