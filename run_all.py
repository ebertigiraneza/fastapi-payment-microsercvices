# run_all.py              
    
import uvicorn
from multiprocessing import Process

def run_service(app: str, port: int):
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False, workers=1)

services = [
    ("wallet.app:app", 8000),
    ("authentification.app:app", 8001),
    ("deposit.app:app", 8002),
    ("withdraw.app:app", 8003)
]

for app, port in services:
    p = Process(target=run_service, args=(app, port))
    p.start()     