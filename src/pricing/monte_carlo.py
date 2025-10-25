"""
Monte Carlo Options Pricing Engine
"""

import numpy as np
from typing import Tuple, Dict


class MonteCarloEngine:
    """Monte Carlo simulation for options pricing"""
    
    @staticmethod
    def european_option(S: float, K: float, T: float, r: float, sigma: float,
                       option_type: str = 'call', n_simulations: int = 10000) -> Tuple[float, float]:
        """
        Price European option using Monte Carlo
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            n_simulations: Number of Monte Carlo paths
            
        Returns:
            Tuple of (price, standard_error)
        """
        # Generate random paths
        Z = np.random.standard_normal(n_simulations)
        ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        # Calculate payoffs
        if option_type.lower() == 'call':
            payoffs = np.maximum(ST - K, 0)
        else:
            payoffs = np.maximum(K - ST, 0)
        
        # Discount to present value
        price = np.exp(-r * T) * np.mean(payoffs)
        standard_error = np.exp(-r * T) * np.std(payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    @staticmethod
    def asian_option(S: float, K: float, T: float, r: float, sigma: float,
                    option_type: str = 'call', n_simulations: int = 10000,
                    n_steps: int = 252) -> Tuple[float, float]:
        """
        Price Asian option (arithmetic average)
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            n_simulations: Number of paths
            n_steps: Number of time steps
            
        Returns:
            Tuple of (price, standard_error)
        """
        dt = T / n_steps
        
        # Generate paths
        paths = np.zeros((n_simulations, n_steps + 1))
        paths[:, 0] = S
        
        for t in range(1, n_steps + 1):
            Z = np.random.standard_normal(n_simulations)
            paths[:, t] = paths[:, t-1] * np.exp(
                (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
            )
        
        # Calculate average price for each path
        avg_prices = np.mean(paths, axis=1)
        
        # Calculate payoffs
        if option_type.lower() == 'call':
            payoffs = np.maximum(avg_prices - K, 0)
        else:
            payoffs = np.maximum(K - avg_prices, 0)
        
        # Discount to present value
        price = np.exp(-r * T) * np.mean(payoffs)
        standard_error = np.exp(-r * T) * np.std(payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    @staticmethod
    def barrier_option(S: float, K: float, T: float, r: float, sigma: float,
                      barrier: float, barrier_type: str = 'down-and-out',
                      option_type: str = 'call', n_simulations: int = 10000,
                      n_steps: int = 252) -> Tuple[float, float]:
        """
        Price barrier option using Monte Carlo
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry
            r: Risk-free rate
            sigma: Volatility
            barrier: Barrier level
            barrier_type: 'down-and-out', 'down-and-in', 'up-and-out', 'up-and-in'
            option_type: 'call' or 'put'
            n_simulations: Number of paths
            n_steps: Number of time steps
            
        Returns:
            Tuple of (price, standard_error)
        """
        dt = T / n_steps
        
        # Generate paths
        paths = np.zeros((n_simulations, n_steps + 1))
        paths[:, 0] = S
        
        for t in range(1, n_steps + 1):
            Z = np.random.standard_normal(n_simulations)
            paths[:, t] = paths[:, t-1] * np.exp(
                (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
            )
        
        # Check barrier conditions
        if 'down' in barrier_type.lower():
            barrier_hit = np.any(paths <= barrier, axis=1)
        else:  # up
            barrier_hit = np.any(paths >= barrier, axis=1)
        
        # Calculate payoffs based on barrier type
        ST = paths[:, -1]
        if option_type.lower() == 'call':
            payoffs = np.maximum(ST - K, 0)
        else:
            payoffs = np.maximum(K - ST, 0)
        
        # Apply barrier condition
        if 'out' in barrier_type.lower():
            payoffs[barrier_hit] = 0  # Knock out
        else:  # in
            payoffs[~barrier_hit] = 0  # Only pay if barrier hit
        
        # Discount to present value
        price = np.exp(-r * T) * np.mean(payoffs)
        standard_error = np.exp(-r * T) * np.std(payoffs) / np.sqrt(n_simulations)
        
        return price, standard_error
    
    @staticmethod
    def generate_paths(S: float, T: float, r: float, sigma: float,
                      n_paths: int = 100, n_steps: int = 252) -> np.ndarray:
        """
        Generate stock price paths using Geometric Brownian Motion
        
        Returns:
            Array of shape (n_paths, n_steps + 1)
        """
        dt = T / n_steps
        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 0] = S
        
        for t in range(1, n_steps + 1):
            Z = np.random.standard_normal(n_paths)
            paths[:, t] = paths[:, t-1] * np.exp(
                (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
            )
        
        return paths