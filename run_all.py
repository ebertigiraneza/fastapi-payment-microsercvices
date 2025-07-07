# run_all.py        
 
import subprocess

services = [
    "gunicorn wallet.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000",
    "gunicorn authentification.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001",
    "gunicorn deposit.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002",
    "gunicorn withdraw.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8003"
]

for cmd in services:
    subprocess.Popen(cmd, shell=True)           