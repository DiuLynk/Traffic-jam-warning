import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')
session = requests.Session()
login_res = session.post("http://127.0.0.1:5000/api/auth/login", json={"username": "admin", "password": "admin@123"})
print("Login status:", login_res.json())

cams_res = session.get("http://127.0.0.1:5000/api/cameras")
data = cams_res.json()
cams = data.get("cameras", [])
print(f"\n{'CAM_ID':<8} | {'NAME':<24} | {'IN_ROI':<8} | {'CUMULATIVE':<11} | {'PCU':<6} | {'SPEED':<7} | {'CONGESTION':<15}")
print("-" * 90)
for c in cams:
    m = c.get("metrics", {})
    cid = c.get("id")
    name = c.get("name")
    in_roi = m.get("total_vehicles", 0)
    cum = m.get("cumulative_vehicles", 0)
    pcu = m.get("pcu", 0.0)
    spd = m.get("speed", 0.0)
    cg = m.get("congestion_name", "N/A")
    print(f"{cid:<8} | {name:<24} | {in_roi:<8} | {cum:<11} | {pcu:<6.1f} | {spd:<7.1f} | {cg:<15}")
