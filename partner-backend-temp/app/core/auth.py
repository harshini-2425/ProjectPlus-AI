from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

@dataclass
class CurrentUser:
    id: int
    role: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        subject = payload.get('sub')
        role = payload.get('role')
        if subject is None or role is None:
            raise ValueError
        return CurrentUser(id=int(subject), role=str(role))
    except (JWTError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication credentials', headers={'WWW-Authenticate': 'Bearer'}) from exc

def require_roles(*roles):
    async def dependency(user: CurrentUser = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough permissions')
        return user
    return dependency
