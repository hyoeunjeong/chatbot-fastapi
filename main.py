from fastapi import FastAPI, Request, Form, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import sqlite3
import httpx

# ▶️ 인증 함수 및 사용자 DB
from auth import (
    create_user, authenticate_user, create_session,
    get_current_user, users_db
)

# 🔧 앱 설정
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 🔗 외부 API URL
BOOTCAMP_API_URL = "https://dev.wenivops.co.kr/services/openai-api"

# DB 파일 경로
DB_FILE = "chat_logs.db"


# ---- 1) DB 초기화 ----
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # 대화 로그 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    # 운세 결과 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            fortune TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ---- 2) Pydantic 모델 ----
class ChatLogMessage(BaseModel):
    username: str
    message: str

class StoredChatMessage(ChatLogMessage):
    id: int
    timestamp: datetime

class ChatResultMessage(BaseModel):
    username: str
    fortune: str

class StoredChatResult(ChatResultMessage):
    id: int
    timestamp: datetime


# ---- 3) 대화 로그 API ----
@app.post("/chats", response_model=StoredChatMessage)
def save_chat(msg: ChatLogMessage):
    ts = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages (username, message, timestamp) VALUES (?, ?, ?)",
        (msg.username, msg.message, ts)
    )
    msg_id = cur.lastrowid
    conn.commit()
    conn.close()
    return StoredChatMessage(
        id=msg_id,
        username=msg.username,
        message=msg.message,
        timestamp=datetime.fromisoformat(ts)
    )

@app.get("/chats", response_model=List[StoredChatMessage])
def get_chats(username: Optional[str] = None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if username:
        cur.execute(
            "SELECT id, username, message, timestamp FROM chat_messages WHERE username = ? ORDER BY id ASC",
            (username,)
        )
    else:
        cur.execute(
            "SELECT id, username, message, timestamp FROM chat_messages ORDER BY id ASC"
        )
    rows = cur.fetchall()
    conn.close()
    return [
        StoredChatMessage(
            id=r[0], username=r[1], message=r[2],
            timestamp=datetime.fromisoformat(r[3])
        ) for r in rows
    ]


# ---- 4) 운세 결과 API ----
@app.post("/results", response_model=StoredChatResult)
def save_result(res: ChatResultMessage):
    ts = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_results (username, fortune, timestamp) VALUES (?, ?, ?)",
        (res.username, res.fortune, ts)
    )
    result_id = cur.lastrowid
    conn.commit()
    conn.close()
    return StoredChatResult(
        id=result_id,
        username=res.username,
        fortune=res.fortune,
        timestamp=datetime.fromisoformat(ts)
    )

@app.get("/results", response_model=List[StoredChatResult])
def get_results(username: Optional[str] = None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if username:
        cur.execute(
            "SELECT id, username, fortune, timestamp FROM chat_results "
            "WHERE username = ? ORDER BY id DESC",
            (username,)
        )
    else:
        cur.execute(
            "SELECT id, username, fortune, timestamp FROM chat_results "
            "ORDER BY id DESC"
        )
    rows = cur.fetchall()
    conn.close()
    return [
        StoredChatResult(
            id=r[0], username=r[1], fortune=r[2],
            timestamp=datetime.fromisoformat(r[3])
        ) for r in rows
    ]


# ===== 5) 기존 기능(인증·챗봇·결과 페이지) =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "❌ 아이디 또는 비밀번호가 올바르지 않습니다."
        })
    session_id = create_session(username)
    return templates.TemplateResponse("loading_result.html", {
        "request": request,
        "message": "로그인 중입니다...",
        "redirect_url": f"/login/success?session_id={session_id}"
    })

@app.get("/login/success", response_class=HTMLResponse)
async def login_success(request: Request, session_id: str):
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse("/login")
    resp = templates.TemplateResponse("result.html", {
        "request": request,
        "message": "🎉 로그인 성공!",
        "data": {"id": user.id, "username": user.username, "email": user.email}
    })
    resp.set_cookie("session_id", session_id, httponly=True, max_age=3600)
    return resp

@app.get("/sign_up", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    result = create_user(username, email, password)
    if not result.get("success"):
        return templates.TemplateResponse("sign_up.html", {
            "request": request,
            "error": result.get("message")
        })
    return templates.TemplateResponse("loading_result.html", {
        "request": request,
        "message": "회원가입 처리 중입니다...",
        "redirect_url": f"/register/success?username={username}"
    })

@app.get("/register/success", response_class=HTMLResponse)
async def register_success(request: Request, username: str):
    user = next((u for u in users_db.values() if u.username == username), None)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "message": "🎉 회원가입 완료!",
        "data": {"id": user.id, "username": user.username, "email": user.email}
    })

@app.get("/find_id", response_class=HTMLResponse)
async def find_id_page(request: Request):
    return templates.TemplateResponse("find_id.html", {"request": request})

@app.post("/find_id", response_class=HTMLResponse)
async def find_id(request: Request, email: str = Form(...)):
    match = [u.username for u in users_db.values() if u.email == email]
    msg = f"📧 아이디: {match[0]}" if match else "해당 이메일로 등록된 계정이 없습니다."
    return templates.TemplateResponse("loading_result.html", {
        "request": request,
        "message": msg,
        "redirect_url": "/"
    })

@app.get("/find_pw", response_class=HTMLResponse)
async def find_pw_page(request: Request):
    return templates.TemplateResponse("find_pw.html", {"request": request})

@app.post("/find_pw", response_class=HTMLResponse)
async def find_pw(request: Request, username: str = Form(...), email: str = Form(...)):
    user = next((u for u in users_db.values() if u.username == username and u.email == email), None)
    msg = "📬 임시 비밀번호가 이메일로 발송되었습니다." if user else "일치하는 사용자 정보가 없습니다."
    return templates.TemplateResponse("loading_result.html", {
        "request": request,
        "message": msg,
        "redirect_url": "/"
    })

@app.get("/fortune", response_class=HTMLResponse)
@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request, session_id: Optional[str] = Cookie(None)):
    user = get_current_user(session_id) if session_id else None
    return templates.TemplateResponse("chatbot.html", {"request": request, "user": user})

class ChatMessage(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/chat/send")
async def chatbot_response(request: ChatMessage):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(BOOTCAMP_API_URL, json=request.messages, timeout=20.0)
            res.raise_for_status()
            data = res.json()
            return {"answer": data["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ▶️ 단일 운세 결과 페이지
@app.get("/result", response_class=HTMLResponse)
async def result_page(request: Request, fortune: str, session_id: Optional[str] = Cookie(None)):
    user = get_current_user(session_id) if session_id else None
    return templates.TemplateResponse("result.html", {
        "request": request,
        "fortune": fortune,
        "user": user
    })

# ▶️ 내 운세 기록 페이지
@app.get("/my-results", response_class=HTMLResponse)
async def my_results_page(request: Request, session_id: Optional[str] = Cookie(None)):
    user = get_current_user(session_id) if session_id else None
    return templates.TemplateResponse("results.html", {
        "request": request,
        "user": user
    })


# ▶️ 로컬 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
