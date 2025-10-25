"""Debug signature verification"""
import oqs

# Test Dilithium directly
print("Testing Dilithium signature...")

algorithm = "Dilithium5"
message = b"Sign this message"

# Generate keys
signer = oqs.Signature(algorithm)
public_key = signer.generate_keypair()
private_key = signer.export_secret_key()

print(f"Public key length: {len(public_key)}")
print(f"Private key length: {len(private_key)}")

# Sign with private key
signer_with_key = oqs.Signature(algorithm, secret_key=private_key)
signature = signer_with_key.sign(message)
print(f"Signature length: {len(signature)}")

# Verify with public key
verifier = oqs.Signature(algorithm)
is_valid = verifier.verify(message, signature, public_key)
print(f"Signature valid: {is_valid}")
print(f"Type of is_valid: {type(is_valid)}")

# Try with wrong message
tampered_message = b"Different message"
is_invalid = verifier.verify(tampered_message, signature, public_key)
print(f"Tampered signature valid: {is_invalid}")