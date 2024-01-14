from app.imports import *

from .userSerializers import *
import main
from .config import settings
from .utils import *


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else: 
        datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def get_user(username: str, db):
    user = db.find_one({'username': username})
    return user


def authenticate_user(username: str, password: str, db):
    user = get_user(username=username, db=db)
    print(user)
    if not user:
        return False
    if not Hasher.verify_password(password, user['password']):
        return False
    return user



@AuthJWT.load_config
def get_config():
    return settings



class NotVerified(Exception):
    pass



class UserNotFound(Exception):
    pass



def require_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = userEntity(main.users_collection.find_one({"_id": ObjectId(str(user_id))}))

        if not user:
            raise UserNotFound("User not found")
        
        if not user["verified"]:
            raise NotVerified("User not verified")
        
    except Exception as e:
        error = e.__class__.__name__
        print(error)
        if error == "MissingTokenError":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error while connecting")
        
        if error == "UserNotFound":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        if error == "NotVerified":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please check your account")
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your token is expired, pleas try again")
    
    return user_id
