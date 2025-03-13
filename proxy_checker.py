import requests
import time

PROXY_HEALTH_CHECK_API = "https://api-proxy.bluehat358.us.kg"
INPUT_FILE = "proxy_list.txt"
TEMP_FILE = "proxy_list_temp.txt"
OUTPUT_FILE = "proxy_list_active.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_proxy(ip, port, host="speed.cloudflare.com", tls="true", max_retries=3):
    url = f"{PROXY_HEALTH_CHECK_API}?ip={ip}&port={port}&host={host}&tls={tls}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            data = response.json()

            if "error" in data:
                print(f"⚠️ API Error for {ip}:{port} → {data['error']}")
                return False
            
            return data.get("proxyip", False)  # True jika proxy aktif, False jika tidak
        except requests.RequestException as e:
            print(f"⚠️ Request error for {ip}:{port} (Attempt {attempt+1}/{max_retries}) → {e}")
            time.sleep(5)  # Tunggu 5 detik sebelum retry
    
    return False  # Jika gagal semua retry, anggap proxy mati

def main():
    with open(INPUT_FILE, "r") as f, open(TEMP_FILE, "w") as temp_f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue  # Skip jika format tidak valid

            ip, port = parts[:2]  # Ambil IP dan Port
            is_active = check_proxy(ip, port)

            # Log status ke output
            status = "✅ Active" if is_active else "❌ Dead"
            print(f"{ip},{port} {status}")

            if is_active:
                temp_f.write(line)  # Simpan yang aktif ke file temp

    # Gantikan file active dengan file sementara
    with open(TEMP_FILE, "r") as temp_f, open(OUTPUT_FILE, "w") as out_f:
        out_f.writelines(temp_f.readlines())

    print("✅ Proxy checking completed.")

if __name__ == "__main__":
    main()
