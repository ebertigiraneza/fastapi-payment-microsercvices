import subprocess
import time

services = [
    ("wallet.main:app", 8001),
    ("auth.main:app", 8002),
    ("deposit.main:app", 8003),
    ("withdraw.main:app", 8004)
]

# Démarrer le gateway
subprocess.Popen([
    "uvicorn", 
    "main:main_app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload", "false"
])

# Démarrer les microservices
for app, port in services:
    subprocess.Popen([
        "uvicorn",
        app,
        "--host", "0.0.0.0",
        "--port", str(port),
        "--no-reload"
    ])
    time.sleep(1)