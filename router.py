from fastapi import APIRouter

import netdisk
import playground
from account.router import router

routers = APIRouter()
routers.include_router(netdisk.router)
routers.include_router(playground.router)
routers.include_router(router, prefix="/account", tags=["Account"])
