"""
Secure Client for sending encrypted pricing requests
"""

import json
import requests
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.kyber_crypto import KyberCrypto
from crypto.key_manager import KeyManager
from crypto.security_utils import SecurityUtils


class SecureClient:
    """Client for secure options pricing requests"""
    
    def __init__(self, server_url: str = "http://localhost:5000",
                 keys_directory: str = "keys/client"):
        """
        Initialize secure client
        
        Args:
            server_url: Server endpoint URL
            keys_directory: Directory for client keys
        """
        self.server_url = server_url
        self.crypto = KyberCrypto()
        self.key_manager = KeyManager(keys_directory)
        self.session_token = SecurityUtils.generate_session_token()
        
        # Initialize client keys if they don't exist
        self.client_fingerprint = None
        self.public_key = None
        self.private_key = None
        self.server_public_key = None
        
    def initialize_keys(self):
        """Generate or load client keys"""
        keys = self.key_manager.list_keys()
        
        if not keys:
            # Generate new keys
            self.public_key, self.private_key = self.crypto.generate_keypair()
            self.client_fingerprint = self.key_manager.save_keys(
                self.public_key, self.private_key, "encryption"
            )
            print(f"Generated new client keys: {self.client_fingerprint}")
        else:
            # Load existing keys
            self.client_fingerprint = keys[0]['fingerprint']
            self.public_key, self.private_key = self.key_manager.load_keys(
                self.client_fingerprint
            )
            print(f"Loaded existing client keys: {self.client_fingerprint}")
    
    def load_server_public_key(self, server_key_path: str):
        """
        Load server's public key
        
        Args:
            server_key_path: Path to server's public key file
        """
        import base64
        
        with open(server_key_path, 'r') as f:
            key_data = json.load(f)
        
        self.server_public_key = base64.b64decode(key_data['public_key'])
        print(f"Loaded server public key: {key_data['fingerprint']}")
    
    def create_pricing_request(self, symbol: str, strike: float, expiry: float,
                              spot: float, volatility: float, rate: float,
                              option_type: str = 'call') -> Dict[str, Any]:
        """
        Create pricing request payload
        
        Args:
            symbol: Stock symbol
            strike: Strike price
            expiry: Time to expiry (years)
            spot: Current spot price
            volatility: Implied volatility
            rate: Risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            Request dictionary
        """
        request = {
            'symbol': symbol,
            'S': spot,
            'K': strike,
            'T': expiry,
            'r': rate,
            'sigma': volatility,
            'type': option_type
        }
        return request
    
    def encrypt_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt request with server's public key
        
        Args:
            request_data: Pricing request dictionary
            
        Returns:
            Encrypted package with metadata
        """
        if not self.server_public_key:
            raise ValueError("Server public key not loaded. Call load_server_public_key() first.")
        
        # Convert to JSON bytes
        plaintext = json.dumps(request_data).encode('utf-8')
        
        # Encrypt with hybrid encryption
        encrypted_package = self.crypto.hybrid_encrypt(plaintext, self.server_public_key)
        
        # Add message metadata
        message = {
            'header': {
                'version': '1.0',
                'timestamp': datetime.utcnow().isoformat(),
                'message_id': str(uuid.uuid4()),
                'client_id': self.client_fingerprint,
                'session_token': self.session_token
            },
            'payload': encrypted_package
        }
        
        return message
    
    def send_request(self, encrypted_message: Dict[str, Any], 
                    endpoint: str = '/price_option') -> requests.Response:
        """
        Send encrypted request to server
        
        Args:
            encrypted_message: Encrypted message package
            endpoint: API endpoint
            
        Returns:
            Server response
        """
        url = f"{self.server_url}{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=encrypted_message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to server: {e}")
    
    def decrypt_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt server response
        
        Args:
            response_data: Encrypted response from server
            
        Returns:
            Decrypted pricing result
        """
        encrypted_payload = response_data['payload']
        
        # Decrypt with client's private key
        decrypted_bytes = self.crypto.hybrid_decrypt(
            encrypted_payload,
            self.public_key,
            self.private_key
        )
        
        # Parse JSON
        result = json.loads(decrypted_bytes.decode('utf-8'))
        return result
    
    def price_option(self, symbol: str, strike: float, expiry: float,
                    spot: float, volatility: float, rate: float,
                    option_type: str = 'call') -> Dict[str, Any]:
        """
        End-to-end encrypted option pricing
        
        Args:
            symbol: Stock symbol
            strike: Strike price
            expiry: Time to expiry
            spot: Spot price
            volatility: Volatility
            rate: Risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            Pricing result with Greeks
        """
        # Create request
        request_data = self.create_pricing_request(
            symbol, strike, expiry, spot, volatility, rate, option_type
        )
        
        # Encrypt
        encrypted_message = self.encrypt_request(request_data)
        
        # Send
        response = self.send_request(encrypted_message)
        
        # Decrypt response
        result = self.decrypt_response(response.json())
        
        return result
    
    def batch_price_options(self, options_list: list) -> list:
        """
        Price multiple options in batch
        
        Args:
            options_list: List of option parameter dictionaries
            
        Returns:
            List of pricing results
        """
        results = []
        
        for option_params in options_list:
            try:
                result = self.price_option(**option_params)
                results.append({
                    'params': option_params,
                    'result': result,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'params': option_params,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = SecureClient()
    client.initialize_keys()
    
    # Load server's public key
    client.load_server_public_key("keys/server/encryption_<timestamp>_public.json")
    
    # Price an option
    result = client.price_option(
        symbol='AAPL',
        strike=150.0,
        expiry=1.0,
        spot=155.0,
        volatility=0.25,
        rate=0.05,
        option_type='call'
    )
    
    print(json.dumps(result, indent=2))