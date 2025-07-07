# run_all.py              
    
import uvicorn
from multiprocessing import Process

def run_service(app: str, port: int):
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False, workers=1)

services = [
    ("wallet.main:app", 8000),
    ("authentification.main:app", 8001),
    ("deposit.main:app", 8002),
    ("withdraw.main:app", 8003)
]

for app, port in services:
    p = Process(target=run_service, args=(app, port))
    p.start()    

from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi import FastAPI

from wallet.main import app as wallet
from authentification.main import app as authentification
from deposit.main import app as deposit
from withdraw.main import app as withdraw

main_app = FastAPI()

main_app.mount("/wallet", WSGIMiddleware(wallet))
main_app.mount("/auth", WSGIMiddleware(authentification))
main_app.mount("/deposit", WSGIMiddleware(deposit))
main_app.mount("/withdraw", WSGIMiddleware(withdraw))