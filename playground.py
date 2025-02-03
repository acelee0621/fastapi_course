from fastapi import APIRouter,Security
from fastapi.security import SecurityScopes



router = APIRouter()


def print_scopes(security_scopes: SecurityScopes):
    print(security_scopes.scopes)
    
    
    
@router.get("/group/admin",dependencies=[Security(print_scopes, scopes=["admin"])])
async def get_admin():
    pass