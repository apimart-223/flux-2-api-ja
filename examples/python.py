"""Submit one FLUX.2 task and poll it to completion."""
import os, time, requests

BASE = "https://api.apimart.ai/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['APIMART_API_KEY']}", "Content-Type": "application/json"}

r = requests.post(f"{BASE}/images/generations", headers=HEADERS, timeout=60, json={
    "model": "flux-2-pro", "prompt": "a cozy reading nook by a rainy window", "n": 1,
})
r.raise_for_status()
task_id = (r.json().get("data") or {}).get("id")

while True:
    t = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS, timeout=60).json().get("data", {})
    if t.get("status") in ("completed", "failed"):
        print(t.get("status"), "cost=", t.get("cost"))
        break
    time.sleep(5)
