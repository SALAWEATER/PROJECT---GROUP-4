import subprocess
import sys
import os
from threading import Thread
import time

def run_backend():
    backend_path = os.path.join("mentalhealth_app", "business")
    os.chdir(backend_path)
    subprocess.run([sys.executable, "-m", "uvicorn", "app:app", "--reload"])
    
def run_frontend():
    frontend_path = os.path.join("mentalhealth_app", "presentation")
    os.chdir(frontend_path)
    subprocess.run([sys.executable, "frontend.py"])

if __name__ == "__main__":
    # Store original working directory
    original_dir = os.getcwd()
    
    try:
        # Start backend
        backend_thread = Thread(target=run_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Wait for backend to initialize
        time.sleep(3)
        
        # Start frontend
        run_frontend()
    finally:
        # Restore original working directory
        os.chdir(original_dir)