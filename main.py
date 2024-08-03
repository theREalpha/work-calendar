from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from uuid import uuid4
from datetime import datetime, timedelta
from util.database import create_database, selfHash, add_user, get_user
from util.kintone import fetchRecords
from src.models import User, Record
create_database()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

session_storage = {}

@app.get("/", response_class=HTMLResponse)
async def indexH(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.exception_handler(404)
async def notFound(request: Request, exception):
    return templates.TemplateResponse("404.html", {"request": request})

@app.get("/login.html")
async def loginH(request: Request):
    sessionID= request._cookies.get("sessionID",None)
    print(sessionID)
    if sessionID and sessionID in session_storage:
        return RedirectResponse(url="/home", status_code=302)
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
async def login(request: Request,response: Response, email: str= Form(...), pswd: str= Form(...), ):
    user = get_user(email)
    if not user: 
        return JSONResponse({"status":"Login Fail", "email": email, "password": pswd})
    pswd_hash = user[2]
    if selfHash(pswd.encode(), pswd_hash.split(":".encode())[0])!=pswd_hash:
        return JSONResponse({"status":"Login Fail", "email": email, "password": pswd})
    if email not in session_storage.values():
        sessionID = str(uuid4().hex)
        session_storage[sessionID]=email
        session_storage[email]=sessionID
    else:
        sessionID = session_storage[email]
    response = RedirectResponse(url="/home?sessionID="+ sessionID, status_code=302)
    response.set_cookie("sessionID", sessionID, max_age=86400)
    return response

@app.post("/register")
async def register(username:str = Form(...), email: str= Form(...), pswd: str= Form(...)):
    if add_user(username, email, selfHash(pswd.encode())):
        return RedirectResponse(url="/login.html", status_code=302)
    return JSONResponse({"status":"Registration Fail", "username": username, "email": email, "password": pswd})


@app.get("/getRecords")
async def getRecords(request: Request, email: str= None, sDate:str= None, eDate:str= None):
    sessionID= request._cookies.get("sessionID")
    if not sessionID or sessionID not in session_storage:
        return templates.TemplateResponse("invalidSession.html",{"request": request},status_code=401)
    if not email:
        return JSONResponse(status_code=404, content={"detail" : "Invalid Request"})
    else:
        if email != session_storage[sessionID]:
            return JSONResponse(status_code=403, content={"detail":"Unauthorized to look at other users"})
    if not sDate:
        sDate= datetime.today().strftime("%Y-%m-%d")
    if not eDate:
        eDate = (datetime.today()+timedelta(days=3)).strftime("%Y-%m-%d")
    resp = fetchRecords(email, sDate, eDate)
    if "records" not in resp:
        return JSONResponse(status_code=404, content=resp)

    return templates.TemplateResponse("result.html", {"request": request, "records":resp['records'], "count":resp['count']})
