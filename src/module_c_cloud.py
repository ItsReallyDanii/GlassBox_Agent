import os
import hashlib
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin setup using a local Key
try:
    if not firebase_admin._apps:
        cred_path = "serviceAccountKey.json"
        
        # We only attempt initialization if the key file is actually present to prevent 
        # the entire runtime from crashing for users testing it locally without Firebase
        if os.path.exists(cred_path):
            print(f"Initializing Firebase with {cred_path}...")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Successfully connected to Firestore Database.")
        else:
            print(f"WARNING: {cred_path} not found. Cloud logging will simulate locally.")
            db = None
    else:
        db = firestore.client()
except Exception as e:
    print(f"Failed to initialize Firebase Admin: {e}")
    db = None

def log_ticket(user_issue: str, action_coords: dict, resolution_status: str, system_meta: dict = None) -> None:
    """
    Logs the agent resolution metrics to Firebase Firestore collection 'IT_Tickets'.
    Enhanced with enterprise Trust Layer audits including deterministic hashing
    and metadata for multi-monitor tracking and security compliance.
    """
    meta = system_meta or {}
    
    # Generate cryptographic hash of the action for audit immutability
    audit_string = f"{user_issue}_{action_coords.get('x', 0)}_{action_coords.get('y', 0)}_{resolution_status}"
    audit_hash = hashlib.sha256(audit_string.encode('utf-8')).hexdigest()
    
    # Construct the Ticket payload
    ticket_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z", # UTC ISO 8601 formatting
        "user_issue": user_issue,
        "action_coords": action_coords,
        "human_authorized": resolution_status,
        "audit_hash": audit_hash,
        "system_meta": meta
    }
    
    if db:
        try:
            doc_ref = db.collection("IT_Tickets").document()
            doc_ref.set(ticket_data)
            print(f"\n[CLOUD SYNC / TRUST LAYER] Ticket securely documented: ID {doc_ref.id} | Hash: {audit_hash[:8]}")
        except Exception as e:
            print(f"\n[CLOUD ERROR] Failed to push data to Firestore: {e}")
    else:
         print("\n[SIMULATED CLOUD SYNC] (Trust Layer Audit Sandbox)")
         print(f"Data to be sent to 'IT_Tickets' collection: \n {ticket_data}")

if __name__ == "__main__":
    test_issue = "I am ready to send my application but I can't find the finish button."
    test_coords = {"x": 100, "y": 200, "width": 50, "height": 20}
    
    log_ticket(
        user_issue=test_issue,
        action_coords=test_coords,
        resolution_status="AUTHORIZED",
        system_meta={"monitor": "Primary Simulated"}
    )
