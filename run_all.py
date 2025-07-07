# run_all.py        
import subprocess

# Pour chaque service, lancez Uvicorn avec reload désactivé
services = [
    "uvicorn wallet.app:app --host 0.0.0.0 --port 8004 --reload=false",
    "uvicorn authentification.app:app --host 0.0.0.0 --port 8005 --reload=false"
    "uvicorn deposit.app:app --host 0.0.0.0 --port 8006 --reload=false",
    "uvicorn withdraw.app:app --host 0.0.0.0 --port 8007 --reload=false"
]

for cmd in services:
    subprocess.Popen(cmd, shell=True)        