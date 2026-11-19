import base64
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_aes_key() -> bytes:
    """Generate 256-bit AES key."""
    return AESGCM.generate_key(bit_length=256)


def encrypt_aes_gcm(plaintext: bytes, key: bytes, associated_data: bytes = b"") -> Tuple[str, str, str]:
    """
    Encrypt data using AES-256-GCM.
    Returns: (base64_ciphertext, base64_nonce, base64_tag)
    Note: cryptography AESGCM appends 16-byte tag to the ciphertext.
    We split them cleanly for explicit vault record storage.
    """
    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes")
    
    nonce = os.urandom(12)  # 96-bit standard nonce for GCM
    aesgcm = AESGCM(key)
    full_cipher = aesgcm.encrypt(nonce, plaintext, associated_data)
    
    # Split ciphertext and authentication tag
    ciphertext = full_cipher[:-16]
    tag = full_cipher[-16:]
    
    return (
        base64.b64encode(ciphertext).decode("ascii"),
        base64.b64encode(nonce).decode("ascii"),
        base64.b64encode(tag).decode("ascii")
    )


def decrypt_aes_gcm(
    b64_ciphertext: str,
    b64_nonce: str,
    b64_tag: str,
    key: bytes,
    associated_data: bytes = b""
) -> bytes:
    """
    Decrypt data using AES-256-GCM and verify authentication tag.
    Raises ValueError on tampering or invalid key.
    """
    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes")
    
    ciphertext = base64.b64decode(b64_ciphertext.encode("ascii"))
    nonce = base64.b64decode(b64_nonce.encode("ascii"))
    tag = base64.b64decode(b64_tag.encode("ascii"))
    
    # Combine ciphertext and tag for AESGCM
    full_cipher = ciphertext + tag
    aesgcm = AESGCM(key)
    
    try:
        plaintext = aesgcm.decrypt(nonce, full_cipher, associated_data)
        return plaintext
    except Exception as e:
        raise ValueError(f"Decryption failed: authentication tag mismatch or corrupted data ({str(e)})")

