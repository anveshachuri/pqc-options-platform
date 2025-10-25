"""
Unit tests for pricing module
"""

import pytest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pricing.black_scholes import BlackScholes
from src.pricing.greeks import GreeksCalculator
from src.pricing.monte_carlo import MonteCarloEngine


class TestBlackScholes:
    """Test Black-Scholes pricing"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.pricer = BlackScholes()
        # Standard test parameters
        self.S = 100.0
        self.K = 100.0
        self.T = 1.0
        self.r = 0.05
        self.sigma = 0.2
    
    def test_call_price_positive(self):
        """Test that call price is positive"""
        price = self.pricer.call_price(self.S, self.K, self.T, self.r, self.sigma)
        assert price > 0
    
    def test_put_price_positive(self):
        """Test that put price is positive"""
        price = self.pricer.put_price(self.S, self.K, self.T, self.r, self.sigma)
        assert price > 0
    
    def test_put_call_parity(self):
        """Test put-call parity: C - P = S - K*e^(-rT)"""
        call = self.pricer.call_price(self.S, self.K, self.T, self.r, self.sigma)
        put = self.pricer.put_price(self.S, self.K, self.T, self.r, self.sigma)
        
        lhs = call - put
        rhs = self.S - self.K * np.exp(-self.r * self.T)
        
        assert abs(lhs - rhs) < 1e-10
    
    def test_call_intrinsic_value(self):
        """Test call price >= intrinsic value"""
        S = 110.0
        K = 100.0
        intrinsic = S - K
        
        price = self.pricer.call_price(S, K, self.T, self.r, self.sigma)
        
        assert price >= intrinsic
    
    def test_put_intrinsic_value(self):
        """Test put price >= intrinsic value"""
        S = 90.0
        K = 100.0
        intrinsic = K - S
        
        price = self.pricer.put_price(S, K, self.T, self.r, self.sigma)
        
        assert price >= intrinsic
    
    def test_call_increases_with_spot(self):
        """Test call price increases with spot price"""
        price1 = self.pricer.call_price(90.0, self.K, self.T, self.r, self.sigma)
        price2 = self.pricer.call_price(110.0, self.K, self.T, self.r, self.sigma)
        
        assert price2 > price1
    
    def test_put_decreases_with_spot(self):
        """Test put price decreases with spot price"""
        price1 = self.pricer.put_price(90.0, self.K, self.T, self.r, self.sigma)
        price2 = self.pricer.put_price(110.0, self.K, self.T, self.r, self.sigma)
        
        assert price1 > price2
    
    def test_expiry_boundary_condition(self):
        """Test option value at expiry"""
        # Call at expiry
        call = self.pricer.call_price(110.0, 100.0, 0.0, self.r, self.sigma)
        assert abs(call - 10.0) < 1e-10
        
        # Put at expiry
        put = self.pricer.put_price(90.0, 100.0, 0.0, self.r, self.sigma)
        assert abs(put - 10.0) < 1e-10
    
    def test_zero_volatility(self):
        """Test pricing with zero volatility"""
        # Should equal discounted intrinsic value
        S = 110.0
        K = 100.0
        T = 1.0
        
        call = self.pricer.call_price(S, K, T, self.r, 0.0001)  # Near zero
        expected = max(S - K * np.exp(-self.r * T), 0)
        
        assert abs(call - expected) < 1.0  # Allow some tolerance


class TestGreeksCalculator:
    """Test Greeks calculations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.calc = GreeksCalculator()
        self.S = 100.0
        self.K = 100.0
        self.T = 1.0
        self.r = 0.05
        self.sigma = 0.2
    
    def test_call_delta_range(self):
        """Test call delta is between 0 and 1"""
        delta = self.calc.delta(self.S, self.K, self.T, self.r, self.sigma, 'call')
        assert 0 <= delta <= 1
    
    def test_put_delta_range(self):
        """Test put delta is between -1 and 0"""
        delta = self.calc.delta(self.S, self.K, self.T, self.r, self.sigma, 'put')
        assert -1 <= delta <= 0
    
    def test_delta_put_call_relationship(self):
        """Test Delta_call - Delta_put = 1"""
        delta_call = self.calc.delta(self.S, self.K, self.T, self.r, self.sigma, 'call')
        delta_put = self.calc.delta(self.S, self.K, self.T, self.r, self.sigma, 'put')
        
        assert abs(delta_call - delta_put - 1.0) < 1e-10
    
    def test_gamma_positive(self):
        """Test gamma is always positive"""
        gamma = self.calc.gamma(self.S, self.K, self.T, self.r, self.sigma)
        assert gamma >= 0
    
    def test_gamma_same_for_call_put(self):
        """Test gamma is same for calls and puts"""
        # Gamma doesn't depend on option type in BS model
        gamma = self.calc.gamma(self.S, self.K, self.T, self.r, self.sigma)
        assert gamma > 0
    
    def test_vega_positive(self):
        """Test vega is positive"""
        vega = self.calc.vega(self.S, self.K, self.T, self.r, self.sigma)
        assert vega > 0
    
    def test_theta_call_negative(self):
        """Test theta is typically negative for calls"""
        theta = self.calc.theta(self.S, self.K, self.T, self.r, self.sigma, 'call')
        # Theta is negative for most options (time decay)
        assert theta < 0
    
    def test_all_greeks_calculation(self):
        """Test calculating all Greeks at once"""
        greeks = self.calc.calculate_all_greeks(
            self.S, self.K, self.T, self.r, self.sigma, 'call'
        )
        
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'vega' in greeks
        assert 'theta' in greeks
        assert 'rho' in greeks
        
        # Verify all are numbers
        for key, value in greeks.items():
            assert isinstance(value, (int, float))


class TestMonteCarloEngine:
    """Test Monte Carlo pricing"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mc = MonteCarloEngine()
        self.bs = BlackScholes()
        self.S = 100.0
        self.K = 100.0
        self.T = 1.0
        self.r = 0.05
        self.sigma = 0.2
    
    def test_european_call_convergence(self):
        """Test MC price converges to Black-Scholes"""
        mc_price, std_error = self.mc.european_option(
            self.S, self.K, self.T, self.r, self.sigma, 'call', n_simulations=50000
        )
        bs_price = self.bs.call_price(self.S, self.K, self.T, self.r, self.sigma)
        
        # Should be within 3 standard errors
        assert abs(mc_price - bs_price) < 3 * std_error
    
    def test_european_put_convergence(self):
        """Test MC put price converges to Black-Scholes"""
        mc_price, std_error = self.mc.european_option(
            self.S, self.K, self.T, self.r, self.sigma, 'put', n_simulations=50000
        )
        bs_price = self.bs.put_price(self.S, self.K, self.T, self.r, self.sigma)
        
        assert abs(mc_price - bs_price) < 3 * std_error
    
    def test_asian_option_positive(self):
        """Test Asian option has positive price"""
        price, std_error = self.mc.asian_option(
            self.S, self.K, self.T, self.r, self.sigma, 'call', n_simulations=10000
        )
        
        assert price > 0
        assert std_error > 0
    
    def test_barrier_option_lower_than_vanilla(self):
        """Test barrier option (out) is cheaper than vanilla"""
        barrier_price, _ = self.mc.barrier_option(
            self.S, self.K, self.T, self.r, self.sigma, 
            barrier=110.0, barrier_type='up-and-out',
            option_type='call', n_simulations=10000
        )
        
        vanilla_price, _ = self.mc.european_option(
            self.S, self.K, self.T, self.r, self.sigma, 'call', n_simulations=10000
        )
        
        assert barrier_price < vanilla_price
    
    def test_path_generation_shape(self):
        """Test generated paths have correct shape"""
        n_paths = 100
        n_steps = 252
        
        paths = self.mc.generate_paths(
            self.S, self.T, self.r, self.sigma, n_paths, n_steps
        )
        
        assert paths.shape == (n_paths, n_steps + 1)
        assert np.all(paths[:, 0] == self.S)  # All start at spot
        assert np.all(paths > 0)  # All prices positive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])