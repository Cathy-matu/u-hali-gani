import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.break_glass import BreakGlassVault, BreakGlassRequest
from app.models.user import User
from app.models.audit import AuditLog
from app.services.encryption.aes_gcm import generate_aes_key, encrypt_aes_gcm, decrypt_aes_gcm


def _resolve_user(db: Session, identifier: Any) -> Optional[User]:
    """Resolve user from UUID string, UUID object, or anonymous handle."""
    if not identifier:
        return None
    try:
        val = uuid.UUID(str(identifier))
        u = db.query(User).filter(User.id == val).first()
        if u:
            return u
    except (ValueError, TypeError):
        pass
    return db.query(User).filter(User.anon_handle == str(identifier)).first()


# 2-of-2 Secret Sharing Implementation
def split_key_2_of_2(master_key: bytes) -> Tuple[bytes, bytes]:
    """
    Split 32-byte key into two independent key shares using XOR secret sharing.
    Information-theoretically secure: Share 1 alone or Share 2 alone yields zero information.
    """
    if len(master_key) != 32:
        raise ValueError("Master key must be 32 bytes")
    share1 = os.urandom(32)
    share2 = bytes(a ^ b for a, b in zip(master_key, share1))
    return share1, share2


def reconstruct_key_2_of_2(share1: bytes, share2: bytes) -> bytes:
    """Reconstruct 32-byte master key from two valid shares."""
    if len(share1) != 32 or len(share2) != 32:
        raise ValueError("Both shares must be exactly 32 bytes")
    return bytes(a ^ b for a, b in zip(share1, share2))


# In-memory protected Key Custody Vault simulation
_COUNSELLOR_KEY_CUSTODY: Dict[str, bytes] = {}
_DEAN_KEY_CUSTODY: Dict[str, bytes] = {}


def protect_and_store_share(share: bytes, custodian_type: str) -> str:
    """Store key share in independent protected custody boundary and return reference ID."""
    ref_id = f"sec_share_{custodian_type}_{uuid.uuid4().hex}"
    boundary_key = (
        settings.COUNSELLOR_CUSTODY_SECRET if custodian_type == "counsellor"
        else settings.DEAN_CUSTODY_SECRET
    ).encode("utf-8")[:32].ljust(32, b"0")
    
    ct, nonce, tag = encrypt_aes_gcm(share, boundary_key)
    packed = json.dumps({"ct": ct, "nonce": nonce, "tag": tag}).encode("utf-8")
    
    if custodian_type == "counsellor":
        _COUNSELLOR_KEY_CUSTODY[ref_id] = packed
    else:
        _DEAN_KEY_CUSTODY[ref_id] = packed
    return ref_id


def retrieve_custody_share(ref_id: str, custodian_type: str) -> bytes:
    """Retrieve and unwrap key share from custodian boundary."""
    custody_store = _COUNSELLOR_KEY_CUSTODY if custodian_type == "counsellor" else _DEAN_KEY_CUSTODY
    if ref_id not in custody_store:
        raise ValueError(f"Key share reference {ref_id} not found in {custodian_type} custody")
    
    packed = custody_store[ref_id]
    data = json.loads(packed.decode("utf-8"))
    
    boundary_key = (
        settings.COUNSELLOR_CUSTODY_SECRET if custodian_type == "counsellor"
        else settings.DEAN_CUSTODY_SECRET
    ).encode("utf-8")[:32].ljust(32, b"0")
    
    share = decrypt_aes_gcm(data["ct"], data["nonce"], data["tag"], boundary_key)
    return share


class BreakGlassVaultService:
    @staticmethod
    def store_emergency_contact(
        db: Session,
        university_id: str,
        user_uuid: str,
        contact_data: Dict[str, Any]
    ) -> BreakGlassVault:
        """
        Store emergency contact information in the dual-key break-glass vault.
        Contact data is encrypted with AES-256-GCM and split into 2 independent shares.
        """
        user = _resolve_user(db, user_uuid)
        clean_user_id = user.id if user else uuid.UUID(str(user_uuid))
        clean_univ_id = user.university_id if user else uuid.UUID(str(university_id))

        # Master encryption key
        master_key = generate_aes_key()
        
        # Split into 2-of-2 shares
        share_counsellor, share_dean = split_key_2_of_2(master_key)
        
        # Protect shares in separate custody boundaries
        counsellor_ref = protect_and_store_share(share_counsellor, "counsellor")
        dean_ref = protect_and_store_share(share_dean, "dean")
        
        # Encrypt contact JSON with master key
        payload_bytes = json.dumps(contact_data).encode("utf-8")
        ct, nonce, tag = encrypt_aes_gcm(payload_bytes, master_key, associated_data=str(clean_user_id).encode())
        
        # Clear master key from memory
        del master_key
        del share_counsellor
        del share_dean
        
        # Check existing record
        vault_record = db.query(BreakGlassVault).filter(
            BreakGlassVault.user_uuid == clean_user_id,
            BreakGlassVault.university_id == clean_univ_id
        ).first()
        
        if vault_record:
            vault_record.encrypted_contact = ct
            vault_record.nonce = nonce
            vault_record.authentication_tag = tag
            vault_record.counsellor_key_share_reference = counsellor_ref
            vault_record.dean_admin_key_share_reference = dean_ref
        else:
            vault_record = BreakGlassVault(
                university_id=clean_univ_id,
                user_uuid=clean_user_id,
                encrypted_contact=ct,
                nonce=nonce,
                authentication_tag=tag,
                counsellor_key_share_reference=counsellor_ref,
                dean_admin_key_share_reference=dean_ref
            )
            db.add(vault_record)
        
        db.commit()
        db.refresh(vault_record)
        return vault_record

    @staticmethod
    def create_request(
        db: Session,
        university_id: str,
        user_uuid: str,
        requesting_counsellor_uuid: str,
        reason: str,
        escalation_case_id: Optional[str] = None
    ) -> BreakGlassRequest:
        """Step 1: Authorized counsellor initiates break-glass emergency request."""
        user = _resolve_user(db, user_uuid)
        clean_user_id = user.id if user else uuid.UUID(str(user_uuid))
        clean_univ_id = user.university_id if user else uuid.UUID(str(university_id))

        counsellor = _resolve_user(db, requesting_counsellor_uuid)
        clean_counsellor_id = counsellor.id if counsellor else uuid.UUID(str(requesting_counsellor_uuid))

        clean_esc_id = None
        if escalation_case_id:
            try:
                clean_esc_id = uuid.UUID(str(escalation_case_id))
            except (ValueError, TypeError):
                clean_esc_id = None

        vault = db.query(BreakGlassVault).filter(
            BreakGlassVault.user_uuid == clean_user_id,
            BreakGlassVault.university_id == clean_univ_id
        ).first()
        
        if not vault:
            raise ValueError("No emergency vault record found for this student")
        
        if not reason or len(reason.strip()) < 10:
            raise ValueError("A substantial clinical emergency justification is mandatory")

        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
        bg_request = BreakGlassRequest(
            university_id=clean_univ_id,
            vault_id=vault.id,
            user_uuid=clean_user_id,
            escalation_case_id=clean_esc_id,
            requesting_counsellor_uuid=clean_counsellor_id,
            reason=reason,
            status="PENDING_APPROVAL",
            expires_at=expires_at
        )
        db.add(bg_request)
        
        # Audit log for creation
        audit = AuditLog(
            university_id=clean_univ_id,
            actor_uuid=clean_counsellor_id,
            actor_role="counsellor",
            action="BREAK_GLASS_REQUESTED",
            resource_type="break_glass_vault",
            resource_id=str(vault.id),
            details={"request_id": str(bg_request.id), "reason": reason}
        )
        db.add(audit)
        db.commit()
        db.refresh(bg_request)
        return bg_request

    @staticmethod
    def approve_and_decrypt(
        db: Session,
        university_id: str,
        request_id: str,
        approving_dean_uuid: str
    ) -> Dict[str, Any]:
        """
        Step 2: Authorized Dean of Students / Admin approves.
        Reconstructs key from the two independent custody shares ONLY after dual authorization.
        """
        try:
            req_uuid = uuid.UUID(str(request_id))
        except (ValueError, TypeError):
            raise ValueError("Invalid request ID format")

        dean = _resolve_user(db, approving_dean_uuid)
        clean_dean_id = dean.id if dean else uuid.UUID(str(approving_dean_uuid))

        bg_request = db.query(BreakGlassRequest).filter(
            BreakGlassRequest.id == req_uuid
        ).first()
        
        if not bg_request:
            raise ValueError("Break-glass request not found")
        
        if bg_request.status != "PENDING_APPROVAL":
            raise ValueError(f"Request is not pending approval (status: {bg_request.status})")
        
        if str(bg_request.requesting_counsellor_uuid) == str(clean_dean_id):
            raise ValueError("Dual authorization required: Approver must be distinct from requester")
        
        vault = db.query(BreakGlassVault).filter(BreakGlassVault.id == bg_request.vault_id).first()
        if not vault:
            raise ValueError("Vault record associated with request not found")

        try:
            # 1. Retrieve Counsellor Key Share from Counsellor Custody
            share_counsellor = retrieve_custody_share(vault.counsellor_key_share_reference, "counsellor")
            
            # 2. Retrieve Dean Key Share from Dean Custody
            share_dean = retrieve_custody_share(vault.dean_admin_key_share_reference, "dean")
            
            # 3. Reconstruct Master Key using 2-of-2 threshold
            master_key = reconstruct_key_2_of_2(share_counsellor, share_dean)
            
            # 4. Decrypt AES-256-GCM ciphertext
            decrypted_bytes = decrypt_aes_gcm(
                vault.encrypted_contact,
                vault.nonce,
                vault.authentication_tag,
                master_key,
                associated_data=str(vault.user_uuid).encode()
            )
            contact_data = json.loads(decrypted_bytes.decode("utf-8"))
            
            # Update request state
            bg_request.approving_dean_admin_uuid = clean_dean_id
            bg_request.status = "APPROVED_DECRYPTED"
            bg_request.decryption_outcome = "SUCCESS"
            bg_request.decrypted_at = datetime.now(timezone.utc)
            
            # Immutable Audit Event
            audit = AuditLog(
                university_id=bg_request.university_id,
                actor_uuid=clean_dean_id,
                actor_role="dean_of_students",
                action="BREAK_GLASS_APPROVED_AND_DECRYPTED",
                resource_type="break_glass_vault",
                resource_id=str(vault.id),
                details={
                    "request_id": str(bg_request.id),
                    "counsellor_uuid": str(bg_request.requesting_counsellor_uuid),
                    "dean_uuid": str(clean_dean_id),
                    "outcome": "SUCCESS"
                }
            )
            db.add(audit)
            db.commit()
            
            return {
                "request_id": str(bg_request.id),
                "user_uuid": str(vault.user_uuid),
                "decrypted_contact": contact_data,
                "status": "APPROVED_DECRYPTED",
                "requesting_counsellor_uuid": str(bg_request.requesting_counsellor_uuid),
                "approving_dean_admin_uuid": str(clean_dean_id),
                "decrypted_at": bg_request.decrypted_at.isoformat()
            }
        except Exception as e:
            bg_request.status = "FAILED"
            bg_request.decryption_outcome = f"FAILED: {str(e)}"
            db.add(AuditLog(
                university_id=bg_request.university_id,
                actor_uuid=clean_dean_id,
                actor_role="dean_of_students",
                action="BREAK_GLASS_DECRYPTION_FAILED",
                resource_type="break_glass_vault",
                resource_id=str(vault.id),
                details={"error": str(e), "request_id": str(bg_request.id)}
            ))
            db.commit()
            raise ValueError(f"Emergency disclosure decryption failed: {str(e)}")
