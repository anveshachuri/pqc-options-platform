from src.pricing.black_scholes import BlackScholes

# Initialize Black-Scholes
bs = BlackScholes()

# Test 1: Call option
call_price = bs.call_price(S=100, K=100, T=1, r=0.05, sigma=0.2)
print(f"Call option price: ${call_price:.4f}")

# Test 2: Put option
put_price = bs.put_price(S=100, K=100, T=1, r=0.05, sigma=0.2)
print(f"Put option price: ${put_price:.4f}")

# Test 3: Call option with dividends (q = 2%)
call_div = bs.price_with_dividends(S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02, option_type='call')
print(f"Call option price with dividends: ${call_div:.4f}")

# Test 4: Put option with dividends
put_div = bs.price_with_dividends(S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02, option_type='put')
print(f"Put option price with dividends: ${put_div:.4f}")
