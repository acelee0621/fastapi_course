import time
from time import sleep

from fastapi import APIRouter, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel,EmailStr

from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
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
    USE_CREDENTIALS=True
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
    #await fm.send_message(message)
    background_tasks.add_task(fm.send_message, message)
    
    end_time = time.time()
    return {"address":email.addresses,"time": end_time - start_time}


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
        
        
        
connections_chat:list[WebSocket] = []
        
        
# 简易聊天室
@router.websocket("/ws3{name}")
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
