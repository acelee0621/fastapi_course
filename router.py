from fastapi import APIRouter

import netdisk
import playground

routers = APIRouter()
routers.include_router(netdisk.router)
routers.include_router(playground.router)
