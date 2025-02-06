import asyncio
import time
from time import sleep

import uuid
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
import psutil
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import config


router = APIRouter()


mail_config = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=465,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
)


class Email(BaseModel):
    addresses: list[EmailStr]


@router.get("/redis")
async def redis_set(request: Request):
    value = await request.app.state.redis.get("fastapi_redis")

    if value is None:
        sleep(5)
        hi = "hey, redis!"
        await request.app.state.redis.set("fastapi_redis", hi, ex=60)
        return hi
    return value


# 邮件发送服务
@router.post("/send_email")
async def send_email(email: Email, background_tasks: BackgroundTasks):
    start_time = time.time()

    body_html = """
        <h2>FastAPI</h2>
        <p>FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+.</p>
    """

    message = MessageSchema(
        subject="FastAPI",
        recipients=email.addresses,
        body=body_html,
        subtype=MessageType.html,
    )
    fm = FastMail(mail_config)
    # await fm.send_message(message)
    background_tasks.add_task(fm.send_message, message)

    end_time = time.time()
    return {"address": email.addresses, "time": end_time - start_time}


# WebSocket服务
@router.websocket("/ws2")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            # 发送消息
            # 这里可以对data进行各种处理，例如接入LLM
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print(f"{websocket} disconnected")


connections_chat: list[WebSocket] = []


# 简易聊天室
@router.websocket("/ws3/{name}")
async def websocket_endpoint_chat(websocket: WebSocket, name: str):
    await websocket.accept()
    connections_chat.append(websocket)
    await websocket.send_text(f"Hello {name}, welcome to the chat room!")
    try:
        while True:
            data = await websocket.receive_text()
            for client in connections_chat:
                await client.send_text(f"{name} said: {data}")

    except WebSocketDisconnect:
        print(f"{websocket} disconnected")
        connections_chat.remove(websocket)
        for client in connections_chat:
            await client.send_text(f"{name} left the chat room!")


# CPU占用率实时显示
clients: list[WebSocket] = []


@router.websocket("/ws_cpu")
async def websocket_endpoint_cpu(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = psutil.cpu_percent(interval=1)
            data = str(data)
            for client in clients:
                await client.send_text(data)

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print(f"{websocket} disconnected")
        clients.remove(websocket)


@router.get("/chart")
async def chart(request: Request):
    return request.app.state.templates.TemplateResponse(
        request=request, name="chart.html"
    )


class WSManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)

    async def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)


# 通过邮件发送链接激活用户
@router.get("/generate_code")
async def generate_code(request: Request, email: EmailStr):
    code = str(uuid.uuid4().int)[:4]
    await request.app.state.redis.set(email, code, ex=300)
    return code
    # background_tasks.add_task(send_email, email, code)
    # background_tasks.add_task(send_code_by_sms, phone_number, code)


@router.post("/verify_code")
async def verify_code(request: Request, email: EmailStr, code: str):
    random_code = await request.app.state.redis.get(email)
    if random_code == code:
        return {f"{email} verified successful. code: {code}"}
        # activate_user(email)
    print("code not match")
    return {f"{email} verified failed. code: {code}"}


SECRET_KET = "my-secret-key"


@router.get("/generate_link")
async def generate_link(email: EmailStr):
    s1 = URLSafeTimedSerializer(SECRET_KET, salt="activate")
    token = s1.dumps({"email": email})
    return token


@router.get("/verify_link")
async def verify_link(token: str):
    s1 = URLSafeTimedSerializer(SECRET_KET, salt="activate")
    try:
        data = s1.loads(token, max_age=300)
        return data["email"]
    except SignatureExpired:
        return "Verification link has expired"
    except Exception:
        return "Invalid verification link"
