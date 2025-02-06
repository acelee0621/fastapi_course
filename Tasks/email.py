from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from config import config


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


async def send_email(email: Email | str, content_data: str):
    body_html = content_data

    message = MessageSchema(
        subject="Activate your account",
        recipients=email.model_dump().get("addresses"),
        body=body_html,
        subtype=MessageType.html,
    )
    fm = FastMail(mail_config)
    await fm.send_message(message)
    print(f"Email sent to {email.model_dump().get('addresses')} successful")
    return None
