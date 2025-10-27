import subprocess

def gpu_summary() -> str:
    try:
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=name,power.draw,power.limit,utilization.gpu,memory.total", "--format=csv,noheader,nounits"]).decode().strip()
        return "GPU Info:\n" + out
    except Exception as e:
        return f"GPU info unavailable: {e}"
