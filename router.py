from fastapi import APIRouter

import netdisk

routers = APIRouter()
routers.include_router(netdisk.router)
