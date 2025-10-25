"""
Performance Benchmarking Suite
Compares PQC encryption vs classical methods
"""

import time
import numpy as np
import json
import sys
import os
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crypto.kyber_crypto import KyberCrypto
from src.crypto.security_utils import SecurityUtils
from src.pricing.black_scholes import BlackScholes

# For comparison with classical cryptography
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


class PerformanceBenchmark:
    """Benchmark cryptographic and pricing performance"""
    
    def __init__(self):
        self.kyber = KyberCrypto()
        self.pricer = BlackScholes()
        self.results = {}
    
    def measure_encryption_time(self, data_sizes: List[int] = None,
                               n_trials: int = 100) -> Dict:
        """
        Measure encryption time for different data sizes
        
        Args:
            data_sizes: List of data sizes in bytes
            n_trials: Number of trials per size
            
        Returns:
            Dictionary with timing results
        """
        if data_sizes is None:
            data_sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        
        print("\n📊 Benchmarking Encryption Performance...")
        print(f"{'Data Size':<15} {'Kyber-1024':<15} {'RSA-2048':<15} {'Speedup':<10}")
        print("=" * 60)
        
        results = {}
        
        # Generate keys
        kyber_pub, kyber_priv = self.kyber.generate_keypair()
        rsa_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        rsa_pub = rsa_key.public_key()
        
        for size in data_sizes:
            data = os.urandom(size)
            
            # Benchmark Kyber
            kyber_times = []
            for _ in range(n_trials):
                start = time.perf_counter()
                self.kyber.hybrid_encrypt(data, kyber_pub)
                kyber_times.append(time.perf_counter() - start)
            
            kyber_avg = np.mean(kyber_times) * 1000  # Convert to ms
            kyber_std = np.std(kyber_times) * 1000
            
            # Benchmark RSA (only for small data due to limitations)
            if size <= 190:  # RSA-2048 can only encrypt ~190 bytes directly
                rsa_times = []
                for _ in range(n_trials):
                    start = time.perf_counter()
                    rsa_pub.encrypt(
                        data,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    rsa_times.append(time.perf_counter() - start)
                
                rsa_avg = np.mean(rsa_times) * 1000
                speedup = rsa_avg / kyber_avg
            else:
                rsa_avg = None
                speedup = None
            
            # Store results
            size_label = self._format_size(size)
            results[size_label] = {
                'size_bytes': size,
                'kyber_avg_ms': kyber_avg,
                'kyber_std_ms': kyber_std,
                'rsa_avg_ms': rsa_avg,
                'speedup': speedup
            }
            
            # Print results
            rsa_str = f"{rsa_avg:.2f}ms" if rsa_avg else "N/A"
            speedup_str = f"{speedup:.2f}x" if speedup else "N/A"
            print(f"{size_label:<15} {kyber_avg:.2f}ms±{kyber_std:.2f} {rsa_str:<15} {speedup_str:<10}")
        
        self.results['encryption'] = results
        return results
    
    def measure_key_generation_time(self, n_trials: int = 100) -> Dict:
        """Measure key generation time"""
        print("\n🔑 Benchmarking Key Generation...")
        
        # Kyber
        kyber_times = []
        for _ in range(n_trials):
            start = time.perf_counter()
            self.kyber.generate_keypair()
            kyber_times.append(time.perf_counter() - start)
        
        kyber_avg = np.mean(kyber_times) * 1000
        kyber_std = np.std(kyber_times) * 1000
        
        # RSA
        rsa_times = []
        for _ in range(n_trials):
            start = time.perf_counter()
            rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            rsa_times.append(time.perf_counter() - start)
        
        rsa_avg = np.mean(rsa_times) * 1000
        rsa_std = np.std(rsa_times) * 1000
        
        results = {
            'kyber': {'avg_ms': kyber_avg, 'std_ms': kyber_std},
            'rsa': {'avg_ms': rsa_avg, 'std_ms': rsa_std},
            'speedup': rsa_avg / kyber_avg
        }
        
        print(f"Kyber-1024: {kyber_avg:.2f}ms ± {kyber_std:.2f}ms")
        print(f"RSA-2048:   {rsa_avg:.2f}ms ± {rsa_std:.2f}ms")
        print(f"Speedup:    {results['speedup']:.2f}x")
        
        self.results['keygen'] = results
        return results
    
    def measure_pricing_performance(self, n_trials: int = 1000) -> Dict:
        """Measure options pricing performance"""
        print("\n💰 Benchmarking Options Pricing...")
        
        # Test parameters
        params = {
            'S': 100.0,
            'K': 100.0,
            'T': 1.0,
            'r': 0.05,
            'sigma': 0.2,
            'type': 'call'
        }
        
        # Black-Scholes
        bs_times = []
        for _ in range(n_trials):
            start = time.perf_counter()
            self.pricer.price_option(params)
            bs_times.append(time.perf_counter() - start)
        
        bs_avg = np.mean(bs_times) * 1000000  # Convert to microseconds
        bs_std = np.std(bs_times) * 1000000
        
        results = {
            'black_scholes': {
                'avg_us': bs_avg,
                'std_us': bs_std,
                'throughput_per_sec': 1.0 / (bs_avg / 1000000)
            }
        }
        
        print(f"Black-Scholes: {bs_avg:.2f}μs ± {bs_std:.2f}μs")
        print(f"Throughput:    {results['black_scholes']['throughput_per_sec']:.0f} prices/sec")
        
        self.results['pricing'] = results
        return results
    
    def measure_end_to_end_latency(self, n_trials: int = 100) -> Dict:
        """Measure complete request-response cycle"""
        print("\n🔄 Benchmarking End-to-End Latency...")
        
        # Generate keys
        pub_key, priv_key = self.kyber.generate_keypair()
        
        # Test data
        pricing_request = json.dumps({
            'S': 100.0,
            'K': 100.0,
            'T': 1.0,
            'r': 0.05,
            'sigma': 0.2,
            'type': 'call'
        }).encode('utf-8')
        
        times = []
        for _ in range(n_trials):
            start = time.perf_counter()
            
            # Encrypt request
            encrypted = self.kyber.hybrid_encrypt(pricing_request, pub_key)
            
            # Decrypt request
            decrypted = self.kyber.hybrid_decrypt(encrypted, pub_key, priv_key)
            
            # Price option
            params = json.loads(decrypted.decode('utf-8'))
            result = self.pricer.price_option(params)
            
            # Encrypt response
            response = json.dumps(result).encode('utf-8')
            encrypted_response = self.kyber.hybrid_encrypt(response, pub_key)
            
            # Decrypt response
            final_result = self.kyber.hybrid_decrypt(encrypted_response, pub_key, priv_key)
            
            times.append(time.perf_counter() - start)
        
        avg_time = np.mean(times) * 1000
        std_time = np.std(times) * 1000
        
        results = {
            'avg_ms': avg_time,
            'std_ms': std_time,
            'throughput_per_sec': 1.0 / (avg_time / 1000)
        }
        
        print(f"End-to-End: {avg_time:.2f}ms ± {std_time:.2f}ms")
        print(f"Throughput: {results['throughput_per_sec']:.0f} requests/sec")
        
        self.results['end_to_end'] = results
        return results
    
    def measure_key_sizes(self) -> Dict:
        """Compare key sizes"""
        print("\n📏 Comparing Key Sizes...")
        
        # Kyber
        kyber_pub, kyber_priv = self.kyber.generate_keypair()
        
        # RSA
        rsa_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        rsa_pub_pem = rsa_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        rsa_priv_pem = rsa_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        results = {
            'kyber': {
                'public_key_bytes': len(kyber_pub),
                'private_key_bytes': len(kyber_priv),
                'total_bytes': len(kyber_pub) + len(kyber_priv)
            },
            'rsa': {
                'public_key_bytes': len(rsa_pub_pem),
                'private_key_bytes': len(rsa_priv_pem),
                'total_bytes': len(rsa_pub_pem) + len(rsa_priv_pem)
            }
        }
        
        print(f"Kyber-1024:")
        print(f"  Public:  {results['kyber']['public_key_bytes']:,} bytes")
        print(f"  Private: {results['kyber']['private_key_bytes']:,} bytes")
        print(f"  Total:   {results['kyber']['total_bytes']:,} bytes")
        
        print(f"\nRSA-2048:")
        print(f"  Public:  {results['rsa']['public_key_bytes']:,} bytes")
        print(f"  Private: {results['rsa']['private_key_bytes']:,} bytes")
        print(f"  Total:   {results['rsa']['total_bytes']:,} bytes")
        
        print(f"\nSize Ratio: {results['kyber']['total_bytes'] / results['rsa']['total_bytes']:.2f}x")
        
        self.results['key_sizes'] = results
        return results
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size as human readable string"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1048576:
            return f"{size_bytes // 1024}KB"
        else:
            return f"{size_bytes // 1048576}MB"
    
    def run_all_benchmarks(self) -> Dict:
        """Run complete benchmark suite"""
        print("\n" + "="*70)
        print("🚀 Post-Quantum Cryptography Performance Benchmark Suite")
        print("="*70)
        
        self.measure_key_sizes()
        self.measure_key_generation_time()
        self.measure_encryption_time()
        self.measure_pricing_performance()
        self.measure_end_to_end_latency()
        
        return self.results
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved to {filename}")
    
    def generate_summary_report(self) -> str:
        """Generate markdown summary report"""
        report = "# Performance Benchmark Report\n\n"
        report += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Key Generation Performance\n\n"
        if 'keygen' in self.results:
            kg = self.results['keygen']
            report += "| Algorithm | Avg Time | Std Dev |\n"
            report += "|-----------|----------|----------|\n"
            report += f"| Kyber-1024 | {kg['kyber']['avg_ms']:.2f}ms | ±{kg['kyber']['std_ms']:.2f}ms |\n"
            report += f"| RSA-2048 | {kg['rsa']['avg_ms']:.2f}ms | ±{kg['rsa']['std_ms']:.2f}ms |\n\n"
            report += f"**Speedup:** {kg['speedup']:.2f}x\n\n"
        
        report += "## Encryption Performance\n\n"
        if 'encryption' in self.results:
            report += "| Data Size | Kyber-1024 | RSA-2048 | Speedup |\n"
            report += "|-----------|------------|----------|----------|\n"
            for size_label, data in self.results['encryption'].items():
                kyber = f"{data['kyber_avg_ms']:.2f}ms"
                rsa = f"{data['rsa_avg_ms']:.2f}ms" if data['rsa_avg_ms'] else "N/A"
                speedup = f"{data['speedup']:.2f}x" if data['speedup'] else "N/A"
                report += f"| {size_label} | {kyber} | {rsa} | {speedup} |\n"
            report += "\n"
        
        report += "## End-to-End Latency\n\n"
        if 'end_to_end' in self.results:
            e2e = self.results['end_to_end']
            report += f"- **Average Latency:** {e2e['avg_ms']:.2f}ms ± {e2e['std_ms']:.2f}ms\n"
            report += f"- **Throughput:** {e2e['throughput_per_sec']:.0f} requests/sec\n\n"
        
        return report


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    benchmark.save_results()
    
    # Generate and save report
    report = benchmark.generate_summary_report()
    with open("benchmark_report.md", "w") as f:
        f.write(report)
    
    print("\n" + "="*70)
    print("✅ All benchmarks complete!")
    print("="*70)