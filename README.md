# 🔐 Post-Quantum Options Pricing Platform

A quantum-safe financial derivatives pricing system using **Kyber-1024** post-quantum encryption and advanced options pricing models.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

## 🎯 Features

### 🔒 Post-Quantum Cryptography
- **Kyber-1024** key encapsulation (NIST Level 5)
- **Dilithium** digital signatures
- Hybrid encryption (AES-256-GCM + Kyber)
- Key management and rotation
- Timing attack resistance

### 💰 Options Pricing
- Black-Scholes analytical pricing
- Full Greeks calculation (Delta, Gamma, Vega, Theta, Rho)
- Monte Carlo simulation engine
- Exotic options (Asian, Barrier)
- Implied volatility calculation

### 🌐 Secure Communication
- Client-server architecture
- Encrypted request/response protocol
- RESTful API
- Session management

### 📊 Interactive Dashboard
- Real-time pricing interface
- 3D Greeks visualization
- Monte Carlo simulation
- Performance metrics
- Pricing history

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/pqc-options-platform.git
cd pqc-options-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Initialize Keys
```bash
# Generate server keys
python -c "from src.crypto.key_manager import KeyManager; from src.crypto.kyber_crypto import KyberCrypto; km = KeyManager('keys/server'); crypto = KyberCrypto(); pub, priv = crypto.generate_keypair(); km.save_keys(pub, priv, 'encryption')"

# Generate client keys
python -c "from src.crypto.key_manager import KeyManager; from src.crypto.kyber_crypto import KyberCrypto; km = KeyManager('keys/client'); crypto = KyberCrypto(); pub, priv = crypto.generate_keypair(); km.save_keys(pub, priv, 'encryption')"
```

### 2. Start the Server
```bash
python src/network/server.py
```

Server will start on `http://localhost:5000`

### 3. Launch Dashboard
```bash
streamlit run dashboard/app.py
```

Dashboard will open in your browser at `http://localhost:8501`

### 4. Run Benchmarks
```bash
python benchmarks/performance_benchmark.py
```

## 📖 Usage Examples

### Pricing an Option
```python
from src.pricing.black_scholes import BlackScholes

pricer = BlackScholes()

# Price a call option
price = pricer.call_price(
    S=100.0,     # Spot price
    K=100.0,     # Strike price
    T=1.0,       # Time to expiry (years)
    r=0.05,      # Risk-free rate
    sigma=0.25   # Volatility
)

print(f"Call price: ${price:.4f}")
```

### Encrypted Communication
```python
from src.network.client import SecureClient

# Initialize client
client = SecureClient()
client.initialize_keys()
client.load_server_public_key("keys/server/encryption_TIMESTAMP_public.json")

# Price option with encryption
result = client.price_option(
    symbol='AAPL',
    strike=150.0,
    expiry=1.0,
    spot=155.0,
    volatility=0.25,
    rate=0.05,
    option_type='call'
)

print(result)
```

### Monte Carlo Simulation
```python
from src.pricing.monte_carlo import MonteCarloEngine

mc = MonteCarloEngine()

# Price Asian option
price, std_error = mc.asian_option(
    S=100.0,
    K=100.0,
    T=1.0,
    r=0.05,
    sigma=0.2,
    option_type='call',
    n_simulations=50000
)

print(f"Asian call price: ${price:.4f} ± ${std_error:.4f}")
```

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_crypto.py -v
```

## 📊 Project Structure
```
pqc-options-platform/
├── src/
│   ├── crypto/               # Cryptography module
│   │   ├── kyber_crypto.py
│   │   ├── key_manager.py
│   │   └── security_utils.py
│   ├── pricing/              # Pricing engine
│   │   ├── black_scholes.py
│   │   ├── greeks.py
│   │   └── monte_carlo.py
│   └── network/              # Client-server
│       ├── client.py
│       └── server.py
├── dashboard/                # Streamlit dashboard
│   └── app.py
├── benchmarks/               # Performance tests
│   └── performance_benchmark.py
├── tests/                    # Unit tests
│   ├── test_crypto.py
│   ├── test_pricing.py
│   └── test_integration.py
├── keys/                     # Cryptographic keys
├── docs/                     # Documentation
├── requirements.txt
└── README.md
```

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Encryption (1KB) | 3.2ms |
| Key Generation | 2.8ms |
| Option Pricing | 0.15ms |
| End-to-End Latency | 6.4ms |
| Throughput | 156 req/sec |

## 🔐 Security

- **Post-Quantum Security:** Resistant to both classical and quantum attacks
- **NIST Level 5:** Highest security parameter set
- **Hybrid Encryption:** AES-256-GCM for data, Kyber for key encapsulation
- **Forward Secrecy:** Ephemeral session keys
- **Timing Attack Resistance:** Constant-time operations

## 📄 API Documentation

### Server Endpoints

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T12:00:00Z",
  "server_id": "encryption_20251024_120000"
}
```

#### `GET /public_key`
Retrieve server's public key

**Response:**
```json
{
  "fingerprint": "encryption_20251024_120000",
  "public_key": "base64_encoded_key",
  "algorithm": "Kyber1024"
}
```

#### `POST /price_option`
Calculate option price (encrypted)

**Request:**
```json
{
  "header": {
    "version": "1.0",
    "timestamp": "2025-10-24T12:00:00Z",
    "message_id": "uuid",
    "client_id": "client_fingerprint"
  },
  "payload": {
    "encrypted_data": "base64_encrypted_payload"
  }
}
```

**Response:**
```json
{
  "header": {...},
  "payload": {
    "encrypted_data": "base64_encrypted_result"
  }
}
```

## 🚢 Deployment

### Local Deployment
Already covered in Quick Start above.

### Cloud Deployment (Render/Railway)

**1. Create `Procfile`:**
```
web: python src/network/server.py
```

**2. Create `render.yaml`:**
```yaml
services:
  - type: web
    name: pqc-options-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/network/server.py
    envVars:
      - key: PORT
        value: 5000
```

**3. Deploy:**
```bash
git push origin main
# Connect to Render/Railway dashboard
```

### Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set main file: `dashboard/app.py`
5. Deploy

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Open Quantum Safe (liboqs):** Post-quantum cryptography library
- **NIST:** Post-quantum cryptography standardization
- **Black-Scholes-Merton:** Options pricing theory

## 📧 Contact

Questions? Open an issue or contact [your@email.com]

---

**Built with ❤️ for quantum-safe financial systems**