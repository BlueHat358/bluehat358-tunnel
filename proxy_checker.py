import requests
import time
import threading
from queue import Queue

PROXY_HEALTH_CHECK_API = "https://bluehat358-api-proxy.nawank358.workers.dev"
INPUT_FILE = "proxy_list.txt"
OUTPUT_FILE = "proxy_list_active.txt"
THREAD_COUNT = 10  # Batasi jumlah thread agar tidak kena rate limit
REQUEST_DELAY = 1  # Delay antara setiap permintaan untuk menghindari rate limit

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_proxy(ip, port, host="speed.cloudflare.com", tls="true", max_retries=3):
    url = f"{PROXY_HEALTH_CHECK_API}?ip={ip}&port={port}&host={host}&tls={tls}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()  # Raise exception untuk status code 4xx/5xx
            data = response.json()

            if "error" in data:
                return False
            return data.get("proxyip", False)  # True jika proxy aktif, False jika tidak
        except (requests.RequestException, ValueError) as e:
            print(f"Error checking proxy {ip}:{port} - {e}")
            time.sleep(2)  # Tunggu sebelum mencoba ulang
    
    return False

def worker(queue, result_lock, active_proxies):
    while not queue.empty():
        proxy_data = queue.get()
        ip, port, country, provider = proxy_data
        time.sleep(REQUEST_DELAY)  # Delay untuk menghindari rate limit
        is_active = check_proxy(ip, port)
        status = "✅ Active" if is_active else "❌ Dead"
        print(f"{ip},{port} {status}")
        
        if is_active:
            with result_lock:
                active_proxies.append(f"{ip},{port},{country},{provider}\n")
        queue.task_done()

def main():
    queue = Queue()
    active_proxies = []
    result_lock = threading.Lock()
    
    try:
        with open(INPUT_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 4:  # Pastikan ada IP, port, country, dan provider
                    queue.put(parts[:4])  # Masukkan ke dalam queue
    except FileNotFoundError:
        print(f"File {INPUT_FILE} tidak ditemukan.")
        return
    
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, args=(queue, result_lock, active_proxies))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    with open(OUTPUT_FILE, "w") as out_f:
        out_f.writelines(active_proxies)
    
    print(f"✅ Proxy checking completed. {len(active_proxies)} active proxies saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
