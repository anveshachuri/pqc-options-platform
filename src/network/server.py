"""
Secure Server for processing encrypted pricing requests
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
from datetime import datetime
from typing import Dict, Any
import sys
import os
import base64

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.kyber_crypto import KyberCrypto
from crypto.key_manager import KeyManager
from pricing.black_scholes import BlackScholes


class SecureServer:
    """Secure server for options pricing"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000,
                 keys_directory: str = "keys/server"):
        self.app = Flask(__name__)
        CORS(self.app)
        self.host = host
        self.port = port
        self.crypto = KyberCrypto()
        self.key_manager = KeyManager(keys_directory)
        self.pricer = BlackScholes()
        self.server_fingerprint = None
        self.public_key = None
        self.private_key = None
        self.stats = {
            'requests_received': 0,
            'requests_processed': 0,
            'requests_failed': 0,
            'total_computation_time': 0.0
        }
        self._setup_routes()
    
    def initialize_keys(self):
        keys = self.key_manager.list_keys()
        if not keys:
            self.public_key, self.private_key = self.crypto.generate_keypair()
            self.server_fingerprint = self.key_manager.save_keys(
                self.public_key, self.private_key, "encryption"
            )
            print(f"✓ Generated new server keys: {self.server_fingerprint}")
        else:
            self.server_fingerprint = keys[0]['fingerprint']
            self.public_key, self.private_key = self.key_manager.load_keys(
                self.server_fingerprint
            )
            print(f"✓ Loaded existing server keys: {self.server_fingerprint}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route("/", methods=["GET"])
        def root():
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Post-Quantum Secure Options Server</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: #f4f6f8;
                        color: #333;
                        margin: 0;
                        padding: 0;
                    }}
                    header {{
                        background: #1a73e8;
                        color: #fff;
                        padding: 20px;
                        text-align: center;
                    }}
                    main {{
                        padding: 40px 20px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }}
                    h1 {{
                        margin-bottom: 10px;
                    }}
                    p {{
                        margin: 5px 0;
                    }}
                    .buttons {{
                        margin-top: 20px;
                        display: flex;
                        gap: 15px;
                        flex-wrap: wrap;
                        justify-content: center;
                    }}
                    .buttons a {{
                        text-decoration: none;
                        padding: 12px 20px;
                        background: #1a73e8;
                        color: white;
                        font-weight: bold;
                        border-radius: 6px;
                        transition: background 0.3s;
                    }}
                    .buttons a:hover {{
                        background: #155ab6;
                    }}
                    form {{
                        margin-top: 30px;
                        display: flex;
                        flex-direction: column;
                        gap: 10px;
                        width: 300px;
                    }}
                    input, select {{
                        padding: 8px;
                        border-radius: 5px;
                        border: 1px solid #ccc;
                    }}
                    button {{
                        padding: 12px;
                        border: none;
                        border-radius: 6px;
                        background-color: #28a745;
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                        transition: background 0.3s;
                    }}
                    button:hover {{
                        background-color: #1e7e34;
                    }}
                    #response {{
                        margin-top: 20px;
                        word-wrap: break-word;
                        background: #eee;
                        padding: 15px;
                        border-radius: 6px;
                        width: 90%;
                        max-width: 600px;
                    }}
                    footer {{
                        margin-top: 50px;
                        font-size: 0.9em;
                        color: #777;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <header>
                    <h1>🔒 Post-Quantum Secure Options Pricing Server</h1>
                </header>
                <main>
                    <p><strong>Server ID:</strong> {self.server_fingerprint}</p>
                    <p><strong>Algorithm:</strong> Kyber-1024 (NIST Level 5)</p>
                    
                    <div class="buttons">
                        <a href="/health" target="_blank">Health Check</a>
                        <a href="/public_key" target="_blank">Server Public Key</a>
                        <a href="/stats" target="_blank">Server Stats</a>
                    </div>

                    <h2>Price an Option</h2>
                    <form id="pricingForm">
                        <input type="number" step="0.01" name="S" placeholder="Spot Price (S)" required>
                        <input type="number" step="0.01" name="K" placeholder="Strike Price (K)" required>
                        <input type="number" step="0.01" name="T" placeholder="Time to Maturity (T in years)" required>
                        <input type="number" step="0.01" name="r" placeholder="Risk-free Rate (r)" required>
                        <input type="number" step="0.01" name="sigma" placeholder="Volatility (sigma)" required>
                        <select name="type">
                            <option value="call">Call</option>
                            <option value="put">Put</option>
                        </select>
                        <button type="submit">Get Price</button>
                    </form>
                    <div id="response"></div>

                    <footer>
                        Developed using Flask • Kyber Crypto • Secure PQC Options
                    </footer>
                </main>

                <script>
                    const form = document.getElementById('pricingForm');
                    const responseDiv = document.getElementById('response');
                    
                    form.addEventListener('submit', async (e) => {{
                        e.preventDefault();
                        const formData = new FormData(form);
                        const payload = {{
                            header: {{
                                version: "1.0",
                                timestamp: new Date().toISOString(),
                                message_id: crypto.randomUUID(),
                                client_id: "browser_client"
                            }},
                            payload: {{
                                version: "1.0",
                                algorithm: "Kyber1024",
                                ciphertext: btoa(JSON.stringify(Object.fromEntries(formData)))
                            }}
                        }};
                        responseDiv.textContent = "Processing...";
                        try {{
                            const res = await fetch("/price_option", {{
                                method: "POST",
                                headers: {{
                                    "Content-Type": "application/json"
                                }},
                                body: JSON.stringify(payload)
                            }});
                            const data = await res.json();
                            responseDiv.textContent = JSON.stringify(data, null, 2);
                        }} catch(err) {{
                            responseDiv.textContent = "Error: " + err;
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            return render_template_string(html)
        
        # Health endpoint
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'server_id': self.server_fingerprint,
                'stats': self.stats
            })
        
        # Public key endpoint
        @self.app.route('/public_key', methods=['GET'])
        def get_public_key():
            import base64
            return jsonify({
                'fingerprint': self.server_fingerprint,
                'public_key': base64.b64encode(self.public_key).decode('utf-8'),
                'algorithm': 'Kyber1024'
            })
        
        # Pricing endpoint
        @self.app.route('/price_option', methods=['POST'])
        def price_option():
            import time
            start_time = time.time()
            self.stats['requests_received'] += 1
            try:
                encrypted_message = request.json
                if not self._validate_message(encrypted_message):
                    self.stats['requests_failed'] += 1
                    return jsonify({'error': 'Invalid message format'}), 400
                decrypted_data = self._decrypt_request(encrypted_message)
                if not self._validate_pricing_params(decrypted_data):
                    self.stats['requests_failed'] += 1
                    return jsonify({'error': 'Invalid pricing parameters'}), 400
                pricing_result = self._calculate_price(decrypted_data)
                encrypted_response = self._encrypt_response(
                    pricing_result,
                    encrypted_message['header']['client_id']
                )
                self.stats['requests_processed'] += 1
                self.stats['total_computation_time'] += time.time() - start_time
                return jsonify(encrypted_response)
            except Exception as e:
                self.stats['requests_failed'] += 1
                print(f"Error processing request: {e}")
                return jsonify({'error': str(e)}), 500
        
        # Stats endpoint
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            avg_time = (self.stats['total_computation_time'] / 
                        self.stats['requests_processed'] 
                        if self.stats['requests_processed'] > 0 else 0)
            return jsonify({
                'requests_received': self.stats['requests_received'],
                'requests_processed': self.stats['requests_processed'],
                'requests_failed': self.stats['requests_failed'],
                'average_computation_time': f"{avg_time:.4f}s",
                'uptime': datetime.utcnow().isoformat()
            })
    
    # Validation / Encryption / Decryption
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        required_header_fields = ['version', 'timestamp', 'message_id', 'client_id']
        required_payload_fields = ['version', 'algorithm', 'ciphertext']
        if 'header' not in message or 'payload' not in message:
            return False
        for field in required_header_fields:
            if field not in message['header']:
                return False
        for field in required_payload_fields:
            if field not in message['payload']:
                return False
        return True
    
    def _decrypt_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        encrypted_payload = message['payload']
        # In this demo, browser sends base64 encoded JSON, decode directly
        if isinstance(encrypted_payload['ciphertext'], str):
            decoded = json.loads(base64.b64decode(encrypted_payload['ciphertext']).decode())
            return {k: float(v) if v.replace('.','',1).isdigit() else v for k,v in decoded.items()}
        return {}
    
    def _validate_pricing_params(self, params: Dict[str, Any]) -> bool:
        required_fields = ['S', 'K', 'T', 'r', 'sigma', 'type']
        for field in required_fields:
            if field not in params:
                return False
        if params['S'] <= 0 or params['K'] <= 0:
            return False
        if params['T'] < 0 or params['T'] > 10:
            return False
        if params['sigma'] <= 0 or params['sigma'] > 5:
            return False
        return True
    
    def _calculate_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = self.pricer.price_option(params)
        result['timestamp'] = datetime.utcnow().isoformat()
        result['server_id'] = self.server_fingerprint
        result['params'] = params
        return result
    
    def _encrypt_response(self, result: Dict[str, Any], client_id: str) -> Dict[str, Any]:
        try:
            client_public_key = self.key_manager.load_public_key(client_id)
        except FileNotFoundError:
            client_public_key = self.public_key
        plaintext = json.dumps(result).encode('utf-8')
        encrypted_payload = self.crypto.hybrid_encrypt(plaintext, client_public_key)
        response = {
            'header': {
                'version': '1.0',
                'timestamp': datetime.utcnow().isoformat(),
                'message_id': str(uuid.uuid4()),
                'server_id': self.server_fingerprint
            },
            'payload': encrypted_payload
        }
        return response
    
    def run(self):
        print(f"\n{'='*60}")
        print(f"🔒 Post-Quantum Secure Options Pricing Server")
        print(f"{'='*60}")
        print(f"Server ID: {self.server_fingerprint}")
        print(f"Algorithm: Kyber-1024 (NIST Level 5)")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"{'='*60}\n")
        self.app.run(host=self.host, port=self.port, debug=False)


if __name__ == "__main__":
    server = SecureServer()
    server.initialize_keys()
    server.run()
