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