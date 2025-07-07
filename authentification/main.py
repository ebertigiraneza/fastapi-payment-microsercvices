# authentification/main.py
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from shared.databases import database
from shared.models import User
from shared.databases import engine, Base
from shared.dependances import (
    verify_password,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from pydantic import BaseModel    
import uuid
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ConfigDict
from contextlib import asynccontextmanager


app = FastAPI(swagger_ui_init_oauth=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Autorise tous les headers, y compris Authorization
)

class UserLogin(BaseModel):
    email: str
    password: str
    
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    Base.metadata.create_all(bind=engine) 
    yield
    await database.disconnect()
    
app = FastAPI(lifespan=lifespan)    

@app.post("/login")
async def login(
    username: str = Form(...), 
    password: str = Form(...),
):
    """Endpoint compatible avec Swagger ET tests"""
    user = await database.fetch_one(
        User.__table__.select().where(User.email == username)
    )
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": create_access_token({"sub": user.id}),
        "token_type": "bearer" 
    }

@app.post("/register")
async def register_user(user: UserCreate):
    existing_user = await database.fetch_one(
        User.__table__.select().where(User.username == user.username)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    
    new_user = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }
    
    query = User.__table__.insert().values(**new_user)
    await database.execute(query)
    
    return {"message": "User created successfully"}

@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/test")
async def test():
    return {"message": "Test successful"}

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="API Authentification",
        version="1.0",
        routes=app.routes,
    )
    
    # Correction des références manquantes
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}
    
    # Ajoutez vos schémas manuellement si nécessaire
    openapi_schema["components"]["schemas"].update({
        "HTTPValidationError": {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/ValidationError"
                    }
                }
            }
        },
        "ValidationError": {
            "type": "object",
            "properties": {
                "loc": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "msg": {
                    "type": "string"
                },
                "type": {
                    "type": "string"
                }
            },
            "required": ["loc", "msg", "type"]
        }
    })
    
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi