from fastapi import FastAPI, Request,Form, HTTPException,File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,RedirectResponse, HTMLResponse,JSONResponse
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import spacy
import pdfplumber


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
client = MongoClient('mongodb://localhost:27017/')
db = client['homepage']
collection = db['users']

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

def create_user(username, password):
    user = {
        "username": username,
        "password": password,
    }
    collection.insert_one(user)

# Define a function to check if the user exists and validate the password
def check_login(username, password):
    user = collection.find_one({"username": username, "password": password})
    return user is not None

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if check_login(username, password):
        # Redirect to another page or return some other response
        return JSONResponse(content={"message": "Login successful"})
    else:
        return JSONResponse(content={"message": "Login failed"}, status_code=401)

@app.get("/parser")
async def parser(request: Request):
    return templates.TemplateResponse("parser.html", {"request": request})


def create_user(username, password):
    user1 = {
        "username": username,
        "password": password,
    }
    collection.insert_one(user1)

@app.post("/register")
def post_register(username: str = Form(...), password: str = Form(...), repassword: str = Form(...)):
    if password != repassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = collection.find_one({"username": username})
    if existing_user:
        return JSONResponse(content={"message": "Username already taken"}, status_code=400)
    create_user(username, password)
    return JSONResponse(content={"message": "Registration successful"})


nlp=spacy.load("model-best ad")

def get_ents(text):
    doc = nlp(text)
    res = []

    for ent in doc.ents:
        res.append({"label": ent.label_, "value": ent.text})

    return res


@app.post("/resumeparser")
async def process_resume_text(file: UploadFile = File(None), text: str = Form(...) ):
        res = []
        if text:
            doc = nlp(text)
            for ent in doc.ents:
                res.append({"label": ent.label_, "value": ent.text})

        # Process file input
        if file:
            if file.content_type == "application/pdf":
                pdf_data = await file.read()
                pdf = pdfplumber.open(BytesIO(pdf_data))
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                doc = nlp(text)
                for ent in doc.ents:
                    res.append({"label": ent.label_, "value": ent.text})
            elif file.content_type == "text/plain":
                text_data = await file.read()
                doc = nlp(text_data.decode())  # Assuming the text is in plain text format
                for ent in doc.ents:
                    res.append({"label": ent.label_, "value": ent.text})
            else:
                return JSONResponse(content={"error": "Unsupported file format. Only PDFs are allowed."}, status_code=400)

        return res


@app.get("/", response_class=HTMLResponse)
def home(req: Request):
    return templates.TemplateResponse("parser.html", {"request": req})






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)