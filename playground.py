from time import sleep
from fastapi import APIRouter, Request




router = APIRouter()


@router.get("/redis")
async def redis_set(request: Request):
    value = await request.app.state.redis.get("fastapi_redis")
    
    if value is None:
        sleep(5)
        hi = "hey, redis!"
        await request.app.state.redis.set("fastapi_redis", hi, ex=60)
        return hi
    return value