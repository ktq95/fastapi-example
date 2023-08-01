from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from .config import settings
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') 
# URL is the login path of your API to get the access token
# extracts and validates the access token from the Authorization header of the request
# if token is present and correctly formatted, it will be passed into whichever function uses Depends(oauth2_scheme)

# Key parameters
SECRET_KEY = settings.secret_key 
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(payload: dict):
    to_encode = payload.copy()
    expiry_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiry_time})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# Checks if there is a bearer token in the header    
def get_current_user(token: str = Depends(oauth2_scheme)):
    cred_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                   detail=f"Could not validate credentials",
                                   headers={"WWW-Authenticate" : "Bearer"})
    
    return verify_access_token(token, cred_exception)


# decode JWT to get user id
def verify_access_token(token: str, cred_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        decoded_id = str(payload.get("user_id"))

        if decoded_id is None:
            raise cred_exception
        token_data = schemas.TokenData(id=decoded_id)
    
    except JWTError:
        raise cred_exception
    
    return token_data

    
