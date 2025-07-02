import uvicorn
import multiprocessing

def run_server(module: str, port: int):
    uvicorn.run(f"{module}.main:app", host="127.0.0.1", port=port, reload=True)

if __name__ == "__main__":
    servers = [
        ("wallet", 8004),
        ("authentification", 8005),
        ("deposit", 8006),
        ("withdraw", 8007)
    ]
    
    processes = []
    for module, port in servers:
        p = multiprocessing.Process(target=run_server, args=(module, port))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()