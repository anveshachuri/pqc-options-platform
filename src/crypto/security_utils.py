"""
Security Utilities
Timing attack resistance, secure random generation, memory clearing
"""

import hmac
import secrets
import os
from typing import Any


class SecurityUtils:
    """Security helper functions"""
    
    @staticmethod
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """
        Timing-attack resistant comparison
        
        Args:
            a: First byte string
            b: Second byte string
            
        Returns:
            True if equal, False otherwise
        """
        return hmac.compare_digest(a, b)
    
    @staticmethod
    def secure_random_bytes(length: int) -> bytes:
        """
        Generate cryptographically secure random bytes
        
        Args:
            length: Number of bytes
            
        Returns:
            Random bytes
        """
        return secrets.token_bytes(length)
    
    @staticmethod
    def secure_random_int(min_val: int, max_val: int) -> int:
        """Generate secure random integer in range"""
        return secrets.randbelow(max_val - min_val + 1) + min_val
    
    @staticmethod
    def zeroize_memory(data: bytearray):
        """
        Clear sensitive data from memory
        
        Args:
            data: Bytearray to clear
        """
        if isinstance(data, bytearray):
            for i in range(len(data)):
                data[i] = 0
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)