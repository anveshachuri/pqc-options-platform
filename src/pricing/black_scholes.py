"""
Black-Scholes Options Pricing Model
"""

import numpy as np
from scipy.stats import norm
from typing import Dict, Union


class BlackScholes:
    """Black-Scholes options pricing"""
    
    @staticmethod
    def call_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        European call option price
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Call option price
        """
        if T <= 0:
            return max(S - K, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return call
    
    @staticmethod
    def put_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        European put option price
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Put option price
        """
        if T <= 0:
            return max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return put
    
    @staticmethod
    def price_with_dividends(S: float, K: float, T: float, r: float, 
                            sigma: float, q: float, option_type: str = 'call') -> float:
        """
        Option price with continuous dividend yield
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry
            r: Risk-free rate
            sigma: Volatility
            q: Dividend yield
            option_type: 'call' or 'put'
            
        Returns:
            Option price
        """
        S_adjusted = S * np.exp(-q * T)
        
        if option_type.lower() == 'call':
            return BlackScholes.call_price(S_adjusted, K, T, r, sigma)
        else:
            return BlackScholes.put_price(S_adjusted, K, T, r, sigma)
    
    @staticmethod
    def implied_volatility(market_price: float, S: float, K: float, T: float, 
                          r: float, option_type: str = 'call', 
                          max_iterations: int = 100, tolerance: float = 1e-5) -> float:
        """
        Calculate implied volatility using Newton-Raphson
        
        Args:
            market_price: Observed option price
            S: Spot price
            K: Strike price
            T: Time to expiry
            r: Risk-free rate
            option_type: 'call' or 'put'
            max_iterations: Max Newton-Raphson iterations
            tolerance: Convergence tolerance
            
        Returns:
            Implied volatility
        """
        from .greeks import GreeksCalculator
        
        # Initial guess
        sigma = 0.5
        
        for i in range(max_iterations):
            if option_type.lower() == 'call':
                price = BlackScholes.call_price(S, K, T, r, sigma)
            else:
                price = BlackScholes.put_price(S, K, T, r, sigma)
            
            vega = GreeksCalculator.vega(S, K, T, r, sigma)
            
            diff = market_price - price
            
            if abs(diff) < tolerance:
                return sigma
            
            if vega == 0:
                break
            
            sigma = sigma + diff / vega
            
            # Bounds check
            sigma = max(0.01, min(sigma, 5.0))
        
        return sigma
    
    @staticmethod
    def price_option(params: Dict[str, Union[float, str]]) -> Dict[str, float]:
        """
        Price option from parameter dictionary
        
        Args:
            params: Dictionary with keys: S, K, T, r, sigma, type
            
        Returns:
            Dictionary with price and greeks
        """
        from .greeks import GreeksCalculator
        
        S = params['S']
        K = params['K']
        T = params['T']
        r = params['r']
        sigma = params['sigma']
        option_type = params.get('type', 'call')
        
        if option_type.lower() == 'call':
            price = BlackScholes.call_price(S, K, T, r, sigma)
        else:
            price = BlackScholes.put_price(S, K, T, r, sigma)
        
        greeks = GreeksCalculator.calculate_all_greeks(S, K, T, r, sigma, option_type)
        
        return {
            'price': price,
            'delta': greeks['delta'],
            'gamma': greeks['gamma'],
            'vega': greeks['vega'],
            'theta': greeks['theta'],
            'rho': greeks['rho']
        }