import requests
import time
import threading
from queue import Queue

PROXY_HEALTH_CHECK_API = "https://bluehat358-api-proxy.nawank358.workers.dev"
INPUT_FILE = "proxy_list.txt"
OUTPUT_FILE = "proxy_list_active.txt"
THREAD_COUNT = 10  # Batasi jumlah thread agar tidak kena rate limit

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_proxy(ip, port, host="speed.cloudflare.com", tls="true", max_retries=3):
    url = f"{PROXY_HEALTH_CHECK_API}?ip={ip}&port={port}&host={host}&tls={tls}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            data = response.json()

            if "error" in data:
                return False
            return data.get("proxyip", False)  # True jika proxy aktif, False jika tidak
        except requests.RequestException:
            time.sleep(2)  # Tunggu sebelum mencoba ulang
    
    return False

def worker(queue, result_lock, active_proxies):
    while not queue.empty():
        ip, port = queue.get()
        is_active = check_proxy(ip, port)
        status = "✅ Active" if is_active else "❌ Dead"
        print(f"{ip},{port} {status}")
        
        if is_active:
            with result_lock:
                active_proxies.append(f"{ip},{port}\n")
        queue.task_done()

def main():
    queue = Queue()
    active_proxies = []
    result_lock = threading.Lock()
    
    with open(INPUT_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            queue.put(parts[:2])  # Masukkan ke dalam queue
    
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, args=(queue, result_lock, active_proxies))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    with open(OUTPUT_FILE, "w") as out_f:
        out_f.writelines(active_proxies)
    
    print("✅ Proxy checking completed.")

if __name__ == "__main__":
    main()
