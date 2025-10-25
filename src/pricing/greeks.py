"""
Options Greeks Calculator
First and second order sensitivities
"""

import numpy as np
from scipy.stats import norm
from typing import Dict


class GreeksCalculator:
    """Calculate option sensitivities (Greeks)"""
    
    @staticmethod
    def delta(S: float, K: float, T: float, r: float, sigma: float, 
             option_type: str = 'call') -> float:
        """
        Delta: ∂V/∂S (sensitivity to spot price)
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Delta value
        """
        if T <= 0:
            if option_type.lower() == 'call':
                return 1.0 if S > K else 0.0
            else:
                return -1.0 if S < K else 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1
    
    @staticmethod
    def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Gamma: ∂²V/∂S² (rate of change of delta)
        
        Returns:
            Gamma value (same for calls and puts)
        """
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        return gamma
    
    @staticmethod
    def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Vega: ∂V/∂σ (sensitivity to volatility)
        
        Returns:
            Vega value (same for calls and puts)
        """
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)
        return vega / 100  # Per 1% change in volatility
    
    @staticmethod
    def theta(S: float, K: float, T: float, r: float, sigma: float, 
             option_type: str = 'call') -> float:
        """
        Theta: ∂V/∂t (time decay)
        
        Returns:
            Theta value (per day)
        """
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == 'call':
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                    r * K * np.exp(-r * T) * norm.cdf(d2))
        else:
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                    r * K * np.exp(-r * T) * norm.cdf(-d2))
        
        return theta / 365  # Per day
    
    @staticmethod
    def rho(S: float, K: float, T: float, r: float, sigma: float, 
           option_type: str = 'call') -> float:
        """
        Rho: ∂V/∂r (sensitivity to interest rate)
        
        Returns:
            Rho value (per 1% change in rate)
        """
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        return rho / 100  # Per 1% change in rate
    
    @staticmethod
    def calculate_all_greeks(S: float, K: float, T: float, r: float, 
                            sigma: float, option_type: str = 'call') -> Dict[str, float]:
        """
        Calculate all Greeks at once
        
        Returns:
            Dictionary with all Greek values
        """
        return {
            'delta': GreeksCalculator.delta(S, K, T, r, sigma, option_type),
            'gamma': GreeksCalculator.gamma(S, K, T, r, sigma),
            'vega': GreeksCalculator.vega(S, K, T, r, sigma),
            'theta': GreeksCalculator.theta(S, K, T, r, sigma, option_type),
            'rho': GreeksCalculator.rho(S, K, T, r, sigma, option_type)
        }