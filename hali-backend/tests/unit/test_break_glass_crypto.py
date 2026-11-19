import json
import pytest
from app.services.encryption.aes_gcm import generate_aes_key, encrypt_aes_gcm, decrypt_aes_gcm
from app.services.break_glass.vault_service import split_key_2_of_2, reconstruct_key_2_of_2


def test_2_of_2_secret_sharing_reconstruction():
    master_key = generate_aes_key()
    share1, share2 = split_key_2_of_2(master_key)
    
    assert len(share1) == 32
    assert len(share2) == 32
    assert share1 != master_key
    assert share2 != master_key

    reconstructed = reconstruct_key_2_of_2(share1, share2)
    assert reconstructed == master_key


def test_aes_gcm_encryption_and_decryption_with_2_shares():
    master_key = generate_aes_key()
    share1, share2 = split_key_2_of_2(master_key)

    secret_payload = json.dumps({"contact": "0711223344", "name": "Guardian"}).encode("utf-8")
    ct, nonce, tag = encrypt_aes_gcm(secret_payload, master_key, associated_data=b"user_123")

    # Share 1 alone CANNOT decrypt
    with pytest.raises(ValueError):
        decrypt_aes_gcm(ct, nonce, tag, share1, associated_data=b"user_123")

    # Share 2 alone CANNOT decrypt
    with pytest.raises(ValueError):
        decrypt_aes_gcm(ct, nonce, tag, share2, associated_data=b"user_123")

    # Reconstructed key from BOTH shares succeeds
    recovered_key = reconstruct_key_2_of_2(share1, share2)
    decrypted = decrypt_aes_gcm(ct, nonce, tag, recovered_key, associated_data=b"user_123")
    assert json.loads(decrypted.decode("utf-8")) == {"contact": "0711223344", "name": "Guardian"}


def test_aes_gcm_tamper_detection():
    master_key = generate_aes_key()
    ct, nonce, tag = encrypt_aes_gcm(b"Secret Note", master_key)

    # Tampered tag
    tampered_tag = ("A" if tag[0] != "A" else "B") + tag[1:]
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_aes_gcm(ct, nonce, tampered_tag, master_key)

