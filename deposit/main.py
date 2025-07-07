# deposit/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from shared.databases import database
from shared.dependances import get_current_user, get_current_wallet
from shared.models import User, Wallet, Transaction
from sqlalchemy import select
from shared.schemas import  WalletAuth
from fastapi.middleware.cors import CORSMiddleware
from shared.security import settings
from contextlib import asynccontextmanager
import uuid
import httpx

app = FastAPI(
    root_path="/deposit",
    title="API PAYMENT DEPOSIT",
    description="Microservice de dépôt",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Autorise tous les headers, y compris Authorization
)

class DepositRequest(BaseModel):
    source_wallet: str
    target_wallet: str
    amount: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()
    
app = FastAPI(lifespan=lifespan)   

@app.post("/Wallet/deposit")
async def deposit(request: DepositRequest):
    
    status_default = "completed"
    wallet = await database.fetch_one(
        Wallet.__table__.select().where(Wallet.address == request.target_wallet)
    )
    
    if not wallet:
        status_default = "failed"
        raise HTTPException(status_code=404, detail="invalid wallet address")
    
    if request.amount <= 0:
        status_default = "failed"
        raise HTTPException(status_code=400, detail="Montant invalide")

    query = (
        Wallet.__table__
        .update()
        .where(Wallet.address == request.target_wallet)
        .values(balance=Wallet.balance + request.amount)
        .returning(Wallet.balance)
    )
    
    result = await database.fetch_one(query)
    if not result:
        status_default = "failed"
        raise HTTPException(status_code=404, detail="Compte non trouvé")
    
    transaction_data = {
        "id" :str(uuid.uuid4()),
        "wallet_address":wallet.address,
        "external_wallet":request.source_wallet,
        "amount":request.amount,
        "transaction_type":"deposit",
        "status": status_default,
        "description":f"Dépôt de {request.amount} sur le compte {request.target_wallet}"
    }
    
    query_transaction = Transaction.__table__.insert().values(**transaction_data)
    await database.execute(query_transaction)
    
    return {"message": "Dépôt effectué", "source_wallet": request.source_wallet, "target_wallet": request.target_wallet, "amount": request.amount}

# ----------------------------------------- external API call for deposit  -----------------------------------------

# ---------------------------------------------# Retry Mechanism for Failed Transactions ---------------------------------------------

from apscheduler.schedulers.background import BackgroundScheduler

async def retry_transaction(tx):
    try:
        await database.execute(
            Transaction.__table__
            .update()
            .where(Transaction.id == tx.id)
            .values(status="retried", retry_count=tx.retry_count + 1)
        )
    except Exception:
        await database.execute(
            Transaction.__table__
            .update()
            .where(Transaction.id == tx.id)
            .values(retry_count=tx.retry_count + 1)
        )

async def retry_failed_transactions():
    transactions = await database.fetch_all(
        select(Transaction)
        .where(Transaction.status == "failed")
        .where(Transaction.retry_count < 3)
    )
    
    for tx in transactions:
        await retry_transaction(tx)

scheduler = BackgroundScheduler()
scheduler.add_job(retry_failed_transactions, 'interval', minutes=30)
scheduler.start()


# ---------------------------------------------# OpenAPI Customization ---------------------------------------------

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="API DEPOSIT",
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