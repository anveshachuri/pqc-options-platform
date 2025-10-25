"""
Key Management System
Handles storage, loading, and rotation of cryptographic keys
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class KeyManager:
    """Manages cryptographic key lifecycle"""
    
    def __init__(self, keys_directory: str = "keys"):
        """
        Initialize key manager
        
        Args:
            keys_directory: Directory to store keys
        """
        self.keys_dir = Path(keys_directory)
        self.keys_dir.mkdir(exist_ok=True)
        self.rotation_interval_days = 30
        
    def save_keys(self, public_key: bytes, private_key: bytes, 
                  key_type: str = "encryption") -> str:
        """
        Save keys to disk
        
        Args:
            public_key: Public key bytes
            private_key: Private key bytes
            key_type: 'encryption' or 'signing'
            
        Returns:
            Key fingerprint (identifier)
        """
        # Timezone-aware UTC timestamp with microseconds
        now_utc = datetime.now(timezone.utc)
        timestamp = now_utc.strftime("%Y%m%d_%H%M%S_%f")
        fingerprint = f"{key_type}_{timestamp}"

        key_data = {
            'fingerprint': fingerprint,
            'type': key_type,
            'created_at': now_utc.isoformat(),
            'public_key': base64.b64encode(public_key).decode('utf-8'),
            'private_key': base64.b64encode(private_key).decode('utf-8'),
            'rotation_due': (now_utc + timedelta(days=self.rotation_interval_days)).isoformat()
        }
        
        # Save full key file
        key_file = self.keys_dir / f"{fingerprint}.json"
        with open(key_file, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        # Save public key separately for distribution
        pub_file = self.keys_dir / f"{fingerprint}_public.json"
        with open(pub_file, 'w') as f:
            json.dump({
                'fingerprint': fingerprint,
                'type': key_type,
                'public_key': key_data['public_key']
            }, f, indent=2)
        
        return fingerprint
    
    def load_keys(self, fingerprint: str) -> Tuple[bytes, bytes]:
        """
        Load keys from disk
        
        Args:
            fingerprint: Key identifier
            
        Returns:
            Tuple of (public_key, private_key)
        """
        key_file = self.keys_dir / f"{fingerprint}.json"
        
        if not key_file.exists():
            raise FileNotFoundError(f"Key file not found: {fingerprint}")
        
        with open(key_file, 'r') as f:
            key_data = json.load(f)
        
        public_key = base64.b64decode(key_data['public_key'])
        private_key = base64.b64decode(key_data['private_key'])
        
        return public_key, private_key
    
    def load_public_key(self, fingerprint: str) -> bytes:
        """Load only public key"""
        pub_file = self.keys_dir / f"{fingerprint}_public.json"
        
        if not pub_file.exists():
            raise FileNotFoundError(f"Public key file not found: {fingerprint}")
        
        with open(pub_file, 'r') as f:
            key_data = json.load(f)
        
        return base64.b64decode(key_data['public_key'])
    
    def list_keys(self) -> list:
        """List all available keys (ignore public-only files)"""
        keys = []
        for key_file in self.keys_dir.glob("*.json"):
            if key_file.name.endswith("_public.json"):
                continue
            with open(key_file, 'r') as f:
                key_data = json.load(f)
                keys.append({
                    'fingerprint': key_data['fingerprint'],
                    'type': key_data['type'],
                    'created_at': key_data['created_at'],
                    'rotation_due': key_data.get('rotation_due', 'N/A')
                })
        return keys
    
    def check_rotation_needed(self, fingerprint: str) -> bool:
        """Check if key rotation is due"""
        key_file = self.keys_dir / f"{fingerprint}.json"
        
        with open(key_file, 'r') as f:
            key_data = json.load(f)
        
        rotation_due = datetime.fromisoformat(key_data['rotation_due'])
        return datetime.now(timezone.utc) >= rotation_due
    
    def delete_keys(self, fingerprint: str):
        """Securely delete keys"""
        key_file = self.keys_dir / f"{fingerprint}.json"
        pub_file = self.keys_dir / f"{fingerprint}_public.json"
        
        if key_file.exists():
            key_file.unlink()
        if pub_file.exists():
            pub_file.unlink()
