import requests
import time
import random
import json

# --- Cấu hình ---
API_URL = "http://localhost:8888/predict"
TEST_DURATION_SECONDS = 120
PHASE_DURATION_SECONDS = 12
INITIAL_RPS = 30
FINAL_RPS = 150
CLIENT_ERROR_RATE_PERCENT = 35  # 15% request sẽ là lỗi 4xx (payload sai)
SERVER_ERROR_RATE_PERCENT = 10  # 10% request sẽ là lỗi 5xx (server crash)

# --- Dữ liệu mẫu ---
GOOD_SENTENCES = [
    "The weather today is beautiful and sunny.",
    "I am learning about MLOps and monitoring.",
    "This is a test to generate some traffic.",
    "Prometheus and Grafana are powerful tools.",
    "The model seems to be working correctly."
]

# Payload sai sẽ gây ra lỗi 4xx từ FastAPI/Pydantic
BAD_CLIENT_PAYLOADS = [
    {"wrong_key": "this will fail"},
    {"features": 12345},
    {}
]

# Payload đặc biệt để trigger lỗi 5xx trên server
SERVER_CRASH_PAYLOAD = {"features": "trigger_500_error"}

def simulate_traffic():
    print("--- Starting Traffic Simulation (with 4xx and 5xx errors) ---")
    print(f"Duration: {TEST_DURATION_SECONDS}s | RPS: {INITIAL_RPS} -> {FINAL_RPS}")
    
    start_time = time.time()
    num_phases = TEST_DURATION_SECONDS // PHASE_DURATION_SECONDS
    
    try:
        rps_increment = (FINAL_RPS - INITIAL_RPS) / (num_phases - 1)
    except ZeroDivisionError:
        rps_increment = 0

    for phase in range(num_phases):
        current_rps = int(INITIAL_RPS + (phase * rps_increment))
        print(f"\n--- Phase {phase + 1}/{num_phases} | Rate: ~{current_rps} RPS ---")

        for _ in range(PHASE_DURATION_SECONDS):
            for _ in range(current_rps):
                try:
                    # Quyết định gửi loại request nào
                    rand_num = random.randint(1, 100)
                    
                    if rand_num <= SERVER_ERROR_RATE_PERCENT:
                        # Gửi request gây lỗi 5xx
                        payload = SERVER_CRASH_PAYLOAD
                    elif rand_num <= (SERVER_ERROR_RATE_PERCENT + CLIENT_ERROR_RATE_PERCENT):
                        # Gửi request gây lỗi 4xx
                        payload = random.choice(BAD_CLIENT_PAYLOADS)
                    else:
                        # Gửi request thành công
                        payload = {"features": random.choice(GOOD_SENTENCES)}

                    response = requests.post(API_URL, json=payload, timeout=2)
                    print(f"  -> Sent request. Status: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"  -> Request failed: {e}")
            
            time.sleep(1)

    end_time = time.time()
    print("\n--- Simulation Finished ---")
    print(f"Total time elapsed: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    simulate_traffic()
