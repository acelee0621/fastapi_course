from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from Tasks.email import send_email


SECRET_KET = "my-secret-key"
EXPIRED_SECONDS = 3600


async def generate_link(email: EmailStr):
    s1 = URLSafeTimedSerializer(SECRET_KET, salt="activate")
    token = s1.dumps({"email": email})
    return token


async def verify_link(token: str):
    serializer = URLSafeTimedSerializer(SECRET_KET)
    try:
        data = serializer.loads(token, max_age=EXPIRED_SECONDS)
        return data["email"]
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Verification link has expired",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid verification link",
        )


async def send_verification_email(email: EmailStr, link: str):
    data = f'''
    <h1>Activate your account</h1>
    <p>Click <a href="{link}">here</a> to activate your account</p>
    '''

    try:
        await send_email(email=email, content_data=data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )
