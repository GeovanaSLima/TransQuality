from app.imports import *

from app.schemas import *
from app.config import settings
from app.oauth import *
from app.models import *
from app.userSerializers import *
from app.utils import *
from app.forms import *


#############################################################################################################################
############# API Configurations

app = FastAPI()

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
images_dir =os.path.join(static_dir, 'images', 'staticfiles')

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/images", StaticFiles(directory=images_dir), name="images")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Load environment variables from .env file
load_dotenv()

############# MongoDB configuration

client = MongoClient("mongodb+srv://geovanasslima:a1a2a3a4a5@cluster-geovanas.px1vwit.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())

# Call the connect_to_mongodb function to establish the connection
# client = connect_to_mongodb()

db = client.get_database(settings.MONGO_INITDB_DATABASE)

### Collections Setup
responses_collection = db.responses

users_collection = db.users
users_collection.create_index([("username", pymongo.ASCENDING)], unique=True)

forms_collection = db.forms
forms_collection.create_index([("form_id", pymongo.ASCENDING)], unique=True)

questions_collection = db.questions
questions_collection.create_index([("question_number", pymongo.ASCENDING)], unique=True)

# Access token setup
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")

#############################################################################################################################

############# Functions

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


#############################################################################################################################

############################################### FastAPI Routes Config

##### User Info
@app.get("/home", response_class=HTMLResponse)
async def index(request: Request, msg: str = '', current_user: User = Depends(get_current_user_from_token)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user, "msg": msg})


#---------------------------------------------- User Info

@app.get("/user-info", response_class=HTMLResponse)
async def user_info(request: Request, current_user: User = Depends(get_current_user_from_token)):
        return templates.TemplateResponse("userInfo.html", {"request": request, "current_user": current_user})


@router.put("/update-password")
def update_password(new_password: str, current_password: str, current_user: User = Depends(get_current_user_from_token)):
    
    if not Hasher.verify_password(current_password, current_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Hash the new password
    hashed_password = Hasher.get_password_hash(new_password)

    # Update the user's password in the MongoDB system
    users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"password": hashed_password}},
    )
    return RedirectResponse("/home", status_code=status.HTTP_302_FOUND)


#---------------------------------------------- Error Handlers

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return await handle_error(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return await handle_error(request, exc)


async def handle_error(request, exc):
    status_code = exc.status_code
    error_message = exc.detail

    return templates.TemplateResponse("error.html", {"request": request, "status_code": status_code, "error_message": error_message})


#---------------------------------------------- Questionnaire Handle

@app.get("/new-questionnaire")
async def new_questionnaire(request: Request, current_user: User = Depends(get_current_user_from_token)):
    form_id = get_next_form_id()
    question_number = 1
    return RedirectResponse(url=f"/questionnaire/{form_id}/{question_number}", status_code=status.HTTP_302_FOUND)


@app.get("/questionnaire/{form_id}/{question_number}")
async def questionnaire(
    request: Request,
    form_id: int,
    question_number: int,
    current_user: User = Depends(get_current_user_from_token)
):
    loop = asyncio.get_event_loop()
    question = await loop.run_in_executor(
        None, questions_collection.find_one, {"question_number": question_number}
    )
    print("question_number:", question_number)
    try:
        answers = responses_collection.find_one({
            "form_id": form_id,
            "user_id": str(current_user["_id"]),
            "question_number": question_number
        })

        if answers:
            return templates.TemplateResponse("question.html", {
                "request": request,
                "current_user": current_user,
                "form_id": form_id,
                "question": question,
                "question_number": int(question_number),
                "responses": answers
            })
        else:
            return templates.TemplateResponse("question.html", {
                "request": request,
                "current_user": current_user,
                "form_id": form_id,
                "question_number": int(question_number),
                "question": question,
                "responses": ""
            })

    except Exception as e:
        print(e)
        return {"success": False}
    

@app.post("/save_responses")
async def save_responses(request: Request, response: ResponseItem, current_user: User = Depends(get_current_user_from_token)):
    try:
        user_id = str(current_user["_id"])

        form = forms_collection.find_one({"form_id": response.form_id, "user_id": user_id})

        existing_response = responses_collection.find_one(
            {"form_id": response.form_id, "user_id": user_id, "question_number": response.question_number}
        )

        if existing_response:
            # Check if the answers are different
            if (
                existing_response["answer"] != response.answer
                or existing_response["reserve"] != response.reserve
                or existing_response["observation"] != response.observation
                or existing_response["image"] != response.image
            ):
                # Update the existing response
                responses_collection.update_one(
                    {"_id": existing_response["_id"]},
                    {
                        "$set": {
                            "answer": response.answer,
                            "reserve": response.reserve,
                            "observation": response.observation,
                            "image": response.image,
                        }
                    },
                )

                update_form(get_form_info(response.form_id, user_id))

        else:
            
            responses_collection.insert_one({
                "form_id": response.form_id,
                "user_id": user_id,
                "question_number": response.question_number,
                "answer": response.answer,
                "reserve": response.reserve,
                "observation": response.observation,
                "image": response.image,
            })

            if form:
                update_form(get_form_info(response.form_id, user_id))
            else:
                forms_collection.insert_one(get_form_info(response.form_id, user_id))

        return {"success": True, "form_id": response.form_id}

    except Exception as e:
        print(e)
        return {"success": False}


@app.get("/delete/{form_id}",response_class=HTMLResponse)
def delete_form(form_id: int, request: Request, current_user: User = Depends(get_current_user_from_token)):
    print(" delete form method called :"+str(form_id))

    result_responses = responses_collection.delete_many({"form_id": int(form_id), "user_id": str(current_user["_id"])})
    result_form = forms_collection.delete_one({"form_id": int(form_id), "user_id": str(current_user["_id"])})

    if result_form.deleted_count > 0:
        success_message = "Form successfully deleted."
    else:
        success_message = "Form not found." 
    
    return RedirectResponse("/submissions", status_code=303)

@app.put("/update-question")
def update_question(question: ResponseItem, current_user: User = Depends(get_current_user_from_token)):
    print('Update api called....'+str(question.question_number))

    result = responses_collection.update_one(
        {"form_id": question["form_id"], 
         "user_id": question["user_id"], 
         "question_number": question["question_number"]
        },
        {"$set" : 
         {"response": question["response"], 
          "reserve": question["reserve"], 
          "observation": question["observation"], 
          "image": question["image"]
         }
        })

    return {"success": True}


@app.put("/update-form")
def update_form(form: FormItem, current_user: User = Depends(get_current_user_from_token)):

    result = forms_collection.update_one(
        {"form_id": form['form_id'], 
         "user_id": form['user_id']}, 
         {"$set":{
             "complete": form["complete"],
             "minor": form["minor"],
             "major": form["major"],
             "critical": form["critical"],
             "question_number": form["question_number"],
             "created_at": datetime.utcnow()
         }})

    return {"success": True}


@app.post("/upload-files/{form_id}/{question_number}")
async def create_upload_files(request: Request, form_id: int, question_number: int, files: List[UploadFile] = File(...)):
    for file in files:
        contents = await file.read()
        file_extension = file.filename.split(".")[-1]
        new_filename = generate_random_filename(file_extension)
        file_path = f"static/images/staticfiles/{new_filename}"  # Specify the complete file path

        with open(file_path, "wb") as f:
            f.write(contents)

        question = responses_collection.find_one_and_update(
            {"form_id": form_id, "question_number": question_number},
            {"$set": {"image": file_path}}
        )

        if question is None:
            # Handle the case when the question is not found
            raise HTTPException(status_code=404, detail="Question not found")

    return {"success": True, "images": file_path}



@app.get("/submissions", response_class=HTMLResponse)
async def show_submissions(request: Request, current_user: User = Depends(get_current_user_from_token)):
    user_id = str(current_user["_id"])
    forms = forms_collection.find({"user_id": user_id})
    submissions = []
    for form in forms:
        form_id = form["form_id"]
        complete = form["complete"]
        minor = form["minor"]
        major = form["major"]
        critical = form["critical"]
        question_number = form["question_number"]
        created_at = form["created_at"]
        submission = {
            "form_id": form_id,
            "complete": complete,
            "question_number": question_number,
            "created_at": created_at,
            "minor": minor,
            "major": major,
            "critical": critical
            
        }
        submissions.append(submission)
    return templates.TemplateResponse("submissions.html", {"request": request, "current_user": current_user, "submissions": submissions})




@app.get("/generate-pdf/{form_id}")
async def generate_pdf(form_id: int, request: Request, current_user: User = Depends(get_current_user_from_token)):
    
    form = forms_collection.find_one({"form_id": form_id, "user_id": str(current_user["_id"])})
    responses = responses_collection.find({"form_id": form_id, "user_id": str(current_user["_id"])})

    buf = io.BytesIO()

    # Create a SimpleDocTemplate object with the buffer and specified page size
    doc = SimpleDocTemplate(buf, pagesize=letter)

    # Get the default sample styles
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_h2 = styles["Heading2"]
    style_h3 = styles["Heading3"]

    story = []

    count_minor = f"Minor: {form['minor']}"
    count_major = f"Major: {form['major']}"
    count_critical = f"Critical: {form['critical']}"
    counts = Paragraph(f"{count_minor}    |    {count_major}    |    {count_critical}", style_normal)

    ## Adding Header
    story.append(counts)
    story.append(Spacer(1, 6))
    line = HRFlowable(width="100%", thickness=1, lineCap='round', spaceBefore=10, spaceAfter=10)
    story.append(line)

    ## Page Title

    for response in responses:
        question = questions_collection.find_one({"question_number": response["question_number"]})
        question_index = f"Question {question['question_number']}"
        question_them_localisation = f"{question['theme']} - {question['location']}"
        question_text = question["question"]

        # Question Info - Text
        index = Paragraph(question_index, style_h2)
        q_t_loc = Paragraph(question_them_localisation, style_h3)
        q_text = Paragraph(question_text, style_h3)

        # Responses Info - Text
        r_answer = Paragraph(f"Answer: {response['answer']}", style_normal)
        r_reserve = Paragraph(f"Reservation: {response['reserve']}", style_normal)
        r_obs = Paragraph(f"Observation: {response['observation']}", style_normal)
        r_image = None

        if response["image"] != "":
            image_path = response["image"]
            
            r_image = Image(image_path, width=400, height=250)
        
        print(f"{response['image']}")
        print(r_image)


        ## Adding Info - Question
        story.append(index)
        story.append(Spacer(0.2, 0.2))  # Adjust the spacing as needed
        story.append(q_t_loc)
        story.append(Spacer(0.2, 0.2))  # Adjust the spacing as needed
        story.append(q_text)
        story.append(Spacer(1, 6)) 

        ## Adding Info - Responses
        story.append(r_answer)
        story.append(Spacer(1, 2))
        story.append(r_reserve)
        story.append(Spacer(1, 2))
        story.append(r_obs)
        story.append(Spacer(2, 6))
        story.append(r_image)
        story.append(Spacer(1, 2))

    # Build the document with the story content
    doc.build(
        story,
        onFirstPage=first_page,
        onLaterPages=later_pages
    )

    buf.seek(0)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(buf.getvalue())

    return FileResponse(temp_file.name, filename=f"Report_{datetime.utcnow().strftime('%d-%m-%Y')}.pdf")



#---------------------------------------------- Register User Handler
@app.get("/register")
async def register_user(request: Request, message: str = '', current_user: User = Depends(get_current_user_from_token)):
    return templates.TemplateResponse("register.html", {"request": request, "message": message})


@app.post('/register')
async def register(request: Request, current_user: User = Depends(get_current_user_from_token)):
    form = UserCreateForm(request)
    await form.load_data()

    if await form.is_valid():
        user = CreateUserSchema(
            username=form.username, name=form.name, password=form.password, role=form.role, created_at=datetime.utcnow()
        )

        try:
            new_user = {
                'username': user.username,
                'name': user.name,
                'password': Hasher.get_password_hash(user.password),
                'role': user.role,
                'created_at': user.created_at,
            }
            # print("New user data:", new_user)
            users_collection.insert_one(new_user)
            # print("User inserted successfully")
            return responses.RedirectResponse(
                "/home/?msg=Successfully-Registered", status_code=status.HTTP_302_FOUND
            )
        except DuplicateKeyError:
            form.__dict__.get("errors").append("Duplicate username or email")
            print(DuplicateKeyError)
            return templates.TemplateResponse("register.html", form.__dict__)
        except Exception as e:
            # Log the exception
            logging.exception('An error occurred during user registration')
            print("An error occurred during user registration:", e)

    return templates.TemplateResponse("register.html", form.__dict__)


#---------------------------------------------- Login User Handler
@app.route("/", methods=["GET", "POST"])
async def login_page(request: Request, message: str = ''):
    if request.method == "GET":
        return templates.TemplateResponse("login.html", {"request": request, "message": message})
    elif request.method == "POST":
        form = LoginForm(request)
        await form.load_data()
        if await form.is_valid():
            try:
                form.__dict__.update(msg="Login Successful:")
                response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
                login_access_token(response=response, form_data=form)
                return response
            except HTTPException:
                form.__dict__.update(msg="")
                form.__dict__.get("errors").append("Incorrect Username or Password")
                return templates.TemplateResponse("login.html", form.__dict__)
            

@app.post("/token", response_model=Token)
def login_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()): 
    user = authenticate_user(form_data.username, form_data.password, users_collection)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    # return {"access_token": access_token, "token_type": "bearer"}
    return {"token_type": "bearer"}


@router.get("/logout")
async def logout(response: Response):

    try:
        message = "Logout successful"
        response = RedirectResponse(url=f"/?message={message}", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("access_token")
    except Exception as e:
        message = "Logout failed"
        response = RedirectResponse(url=f"/?message={message}".replace(" ", "-").lower(), status_code=status.HTTP_302_FOUND)
    return response


### Including Routers
app.include_router(router)
