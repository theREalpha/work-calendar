from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from uuid import uuid4
from datetime import datetime, timedelta
from util.database import create_database, selfHash, add_user, get_user
from util.kintone import getRecords
from src.models import User, Record
create_database()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

session_storage = {}

@app.get("/", response_class=HTMLResponse)
async def indexH(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login.html",response_class=HTMLResponse)
async def loginH(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/records.html", response_class=HTMLResponse)
async def recordsH(request:Request):
    return templates.TemplateResponse("records.html", {"request": request})

@app.get("/favicon.ico")
async def get_favicon():
    return {"message": "Hello, World!"}

@app.get("/home")
async def home(request: Request, sessionID: str| None = None):
    if sessionID:
        if sessionID not in session_storage:
            return RedirectResponse(url="/login.html", status_code=302)
    else:  
        sessionID=request._cookies.get("sessionID",None)
        if not sessionID or sessionID not in session_storage:
            return RedirectResponse(url="/login.html", status_code=302)
    return templates.TemplateResponse("home.html", {"request": request, "sessionID": sessionID, "email": session_storage[sessionID]})   

## BACKEND ROUTES BELOW

@app.get("/ping")
async def ping():
    return JSONResponse({"message": "Server is Up and Running!"})

@app.post("/login")
async def login(email: str= Form(...), pswd: str= Form(...)):
    username, e_mail, pswd_hash = get_user(email)
    if selfHash(pswd.encode(), pswd_hash.split(":".encode())[0])!=pswd_hash:
        return JSONResponse({"status":"Login Fail", "email": email, "password": pswd})
    if email not in session_storage.values():
        sessionID = str(uuid4().hex)
        session_storage[sessionID]=email
        session_storage[email]=sessionID
    else:
        sessionID = session_storage[email]
    return RedirectResponse(url="/home?sessionID="+ sessionID, status_code=302)

@app.post("/register")
async def register(username:str = Form(...), email: str= Form(...), pswd: str= Form(...)):
    if add_user(username, email, selfHash(pswd.encode())):
        return RedirectResponse(url="/login.html", status_code=302)
    return JSONResponse({"status":"Registration Fail", "username": username, "email": email, "password": pswd})

@app.get("/fetchRecords")
async def fetchRecords(request: Request, email: str= None, sDate:str= None, eDate:str= None):
    sessionID= request._cookies.get("sessionID")
    if not sessionID or sessionID not in session_storage:
        return JSONResponse(status_code=401, content={"detail":"Unauthorized. Please Relogin."})
    if not email:
        return JSONResponse(status_code=404, content={"detail" : "Invalid Request"})
    else:
        if email != session_storage[sessionID]:
            return JSONResponse(status_code=403, content={"detail":"Unauthorized to look at other users"})
    if not sDate:
        sDate= datetime.today().strftime("%Y-%m-%d")
    if not eDate:
        eDate = (datetime.today()+timedelta(days=3)).strftime("%Y-%m-%d")
    records = getRecords(email, sDate, eDate)
    return templates.TemplateResponse("result.html", {"request": request, "records":records})
