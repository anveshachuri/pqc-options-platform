"""
Setup script to initialize the project
"""

import os
import sys
import subprocess
from pathlib import Path


def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        'src/crypto',
        'src/pricing',
        'src/network',
        'dashboard',
        'benchmarks',
        'tests',
        'keys/server',
        'keys/client',
        'docs',
        'results'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py for Python packages
        if directory.startswith('src/'):
            init_file = Path(directory) / '__init__.py'
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Directory structure created")


def generate_keys():
    """Generate initial cryptographic keys"""
    print("\n🔑 Generating cryptographic keys...")
    
    sys.path.append(os.getcwd())
    from src.crypto.kyber_crypto import KyberCrypto
    from src.crypto.key_manager import KeyManager
    
    crypto = KyberCrypto()
    
    # Generate server keys
    server_km = KeyManager('keys/server')
    pub, priv = crypto.generate_keypair()
    server_fp = server_km.save_keys(pub, priv, 'encryption')
    print(f"  ✓ Server keys: {server_fp}")
    
    # Generate client keys
    client_km = KeyManager('keys/client')
    pub, priv = crypto.generate_keypair()
    client_fp = client_km.save_keys(pub, priv, 'encryption')
    print(f"  ✓ Client keys: {client_fp}")
    
    return server_fp, client_fp


def run_tests():
    """Run test suite"""
    print("\n🧪 Running tests...")
    try:
        result = subprocess.run(['pytest', 'tests/', '-v'], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("⚠️ Some tests failed")
            print(result.stderr)
    except FileNotFoundError:
        print("⚠️ pytest not found. Run: pip install pytest")


def main():
    """Main setup function"""
    print("="*70)
    print("🚀 Post-Quantum Options Pricing Platform Setup")
    print("="*70)
    
    # Create directories
    create_directory_structure()
    
    # Generate keys
    try:
        server_fp, client_fp = generate_keys()
    except Exception as e:
        print(f"❌ Key generation failed: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return
    
    # Run tests
    run_tests()
    
    print("\n" + "="*70)
    print("✅ Setup complete!")
    print("="*70)
    print("\n📋 Next steps:")
    print("  1. Start server:    python src/network/server.py")
    print("  2. Open dashboard:  streamlit run dashboard/app.py")
    print("  3. Run benchmarks:  python benchmarks/performance_benchmark.py")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()