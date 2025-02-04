import redis.asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError


# redis连接池
#redis_pool = aioredis.ConnectionPool.from_url("redis://127.0.0.1:6379", decode_responses=True, db=0, maxsize=1000)
redis_pool = aioredis.ConnectionPool(
    host="127.0.0.1",
    port=6379,
    # password="123456",
    decode_responses=True,  # 转码字符串，redis默认返回字节码bytes
    encoding="utf-8",
    )


async def redis_connect():
    try:
        redis_client = aioredis.Redis(connection_pool=redis_pool)
        sig = await redis_client.ping()
        print(sig)
        return redis_client
    except ConnectionError:
        print("redis连接失败")
    except TimeoutError:
        print("redis连接超时")
    except Exception as e:
        print("redis连接异常", e)