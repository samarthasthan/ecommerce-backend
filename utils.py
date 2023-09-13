from fastapi import Depends, HTTPException, Header,status
import jwt

from routes import authentication_routes

def verify_token(authorization: str = Header(...)):
    try:
        token_type, token = authorization.split()
        if token_type != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        payload = jwt.decode(token, authentication_routes.JWT_SECRET, algorithms=["HS256"])
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
  
def verify_token_optional(authorization: str = Depends(verify_token)):
    if authorization is None:
        return None  # Header is missing, return None or handle it as needed
    # Verify the token and perform authentication here
    # If the token is valid, return the user's email
    email = verify_token(authorization)
    return email