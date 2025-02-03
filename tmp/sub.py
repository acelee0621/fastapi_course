from fastapi import FastAPI

grand_son_app = FastAPI()


@grand_son_app.get("/")  # /son/grand/
async def root():
    return {"message": "I'm the grand son app!"}


@grand_son_app.get("/info")  # /son/grand/info
async def info():
    return {"message": "I'm the grand son app info!"}