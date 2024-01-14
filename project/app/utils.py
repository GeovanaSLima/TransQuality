from app.imports import *

from .config import settings
from .models import User
from .schemas import CreateUserSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher():
    @staticmethod
    def verify_password(plain_password, password):
        return pwd_context.verify(plain_password, password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


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
    

pdf_config_dict ={
    "PAGE_HEIGHT": letter[1],
    "PAGE_WIDTH": letter[0],
    "Styles": getSampleStyleSheet(),
    "Canvas": Canvas(f"Report_{datetime.utcnow().strftime('%d-%m-%Y')}", pagesize=letter),
    "Pageinfo": "TransQuality",
    "Title": "Report",
    "Image": "static/images/icons/logo_transquality.png"
}


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold', 20)
    canvas.drawCentredString(300, 750, pdf_config_dict["Title"])
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(x=520, y=15, text=f"Page 1 / {pdf_config_dict['Pageinfo']}")
    canvas.drawImage(pdf_config_dict["Image"], x=20, y=750, width=110, height=35)
    canvas.drawString(547, 28, datetime.utcnow().strftime('%d/%m/%Y'))
    canvas.restoreState()

def later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(x=520, y=15, text=f"Page {doc.page} / {pdf_config_dict['Pageinfo']}")
    canvas.drawImage(pdf_config_dict["Image"], x=20, y=750, width=110, height=35)
    canvas.drawString(547, 28, datetime.utcnow().strftime('%d/%m/%Y'))
    canvas.restoreState()
