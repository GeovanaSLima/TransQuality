import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

# setMainDir()

from app.config import settings
from app.models import User
from app.schemas import CreateUserSchema
from main import *
from app.oauth import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher():
    @staticmethod
    def verify_password(plain_password, password):
        return pwd_context.verify(plain_password, password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
    

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")  #changed to accept access token from httpOnly Cookie
        print("access_token is",authorization)

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


def retrieve_questionnaire(id:int, db):
    item = db.find({'form_id': id})
    return item


def get_user_by_username(username: str, db):
    user = db.find_one({'username': username})
    return user


def create_new_user(user, collection):
    print("Creating new user:", user)
    new_user = {
        'username': user.username,
        'name': user.name,
        'password': Hasher.get_password_hash(user.password),
        'role': user.role,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }
    print("New user data:", new_user)
    collection.insert_one(new_user)
    print("User inserted successfully")
    return new_user
    

def get_current_user_from_token(token: str = Depends(oauth2_scheme), access_token: str = Cookie(default='')): 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.JWT_PRIVATE_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        print("username/email extracted is ",username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username,db=users_collection)
    if user is None:
        raise credentials_exception
    return user


def get_next_form_id() -> int:
    highest_form = forms_collection.find_one({}, sort=[("form_id", -1)])

    if highest_form is not None:
        highest_form_id = highest_form["form_id"]
    else:
        highest_form_id = 0
    
    return highest_form_id + 1


def get_highest_question(form_id) -> int:
    pipeline = [
        {'$match': {'form_id': form_id}},
        {'$group': {'_id': '$form_id', 'highest_question_number': {'$max': '$question_number'}}},
        {'$sort': {'highest_question_number': -1}},
        {'$limit': 1}
    ]

    result = list(responses_collection.aggregate(pipeline))

    if result:
        highest_question_number = result[0]['highest_question_number']
        return highest_question_number
    else:
        {"success": False}


def get_form_info(form_id, user_id):
    minor_count = responses_collection.count_documents({
        'form_id': form_id,
        'reserve': 'minor'
    })

    major_count = responses_collection.count_documents({
        'form_id': form_id,
        'reserve': 'major'
    })

    critical_count = responses_collection.count_documents({
        'form_id': form_id,
        'reserve': 'critical'
    })
            
    complete = get_highest_question(form_id) == questions_collection.count_documents({})

    form_doc = {
        'form_id': form_id,
        'user_id': user_id,
        'complete': complete,
        'minor': minor_count,
        'major': major_count,
        'critical': critical_count,
        'question_number': get_highest_question(form_id),
        'created_at': datetime.utcnow()
    }

    return form_doc


def generate_random_filename(file_extension):
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(10))
    return f"{random_string}.{file_extension}"



pdf_config_dict ={
    "PAGE_HEIGHT": letter[1],
    "PAGE_WIDTH": letter[0],
    "Styles": getSampleStyleSheet(),
    "Canvas": Canvas(f"Report_{datetime.utcnow().strftime('%d-%m-%Y')}", pagesize=letter),
    "Pageinfo": "TransQuality",
    "Title": "Report",
    "Image": "static/images/logo/PNG/logo-transquality.png"
}


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold', 20)
    canvas.drawCentredString(300, 750, pdf_config_dict["Title"])
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(x=520, y=15, text=f"Page 1 / {pdf_config_dict['Pageinfo']}")
    canvas.drawImage(pdf_config_dict["Image"], x=20, y=750, width=190, height=35)
    canvas.drawString(547, 28, datetime.utcnow().strftime('%d/%m/%Y'))
    canvas.restoreState()


def later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(x=520, y=15, text=f"Page {doc.page} / {pdf_config_dict['Pageinfo']}")
    canvas.drawImage(pdf_config_dict["Image"], x=20, y=750, width=110, height=35)
    canvas.drawString(547, 28, datetime.utcnow().strftime('%d/%m/%Y'))
    canvas.restoreState()
