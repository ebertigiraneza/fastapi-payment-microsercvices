from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module
import uvicorn

app = FastAPI()

# Autorise les requêtes CORS si nécessaire
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import dynamique des sous-applications
services = {
    "wallet": {"port": 8001, "path": "/wallet"},
    "auth": {"port": 8002, "path": "/auth"},
    "deposit": {"port": 8003, "path": "/deposit"},
    "withdraw": {"port": 8004, "path": "/withdraw"}
}

for name, config in services.items():
    module = import_module(f"{name}.main")
    app.mount(config["path"], module.app)
    print(f"Mounted {name} at {config['path']}")

@app.get("/")
def read_root():
    return {"message": "API Gateway", "services": list(services.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)