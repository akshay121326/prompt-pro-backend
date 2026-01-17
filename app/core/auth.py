from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional
from app.core.config import settings

# Initialize Firebase Admin SDK
# Check if app is already initialized to avoid errors during reloads
if not firebase_admin._apps:
    if settings.FIREBASE_CREDENTIALS_PATH:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    else:
        # Development mode without explicit credentials (e.g., using ADC or mock) 
        # or warn if not configured.
        print("WARNING: Firebase credentials path not set. Auth may fail if not using ADC.")
        try:
             firebase_admin.initialize_app()
        except Exception as e:
            print(f"Failed to initialize firebase default app: {e}")

security = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the Firebase ID token and returns the decoded token (user info).
    """
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
