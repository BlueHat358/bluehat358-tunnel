import requests
import time

# API untuk pengecekan proxy
PROXY_HEALTH_CHECK_API = "https://api-proxy.bluehat358.us.kg"
HOST = "speed.cloudflare.com"
TLS = "true"

# File input & output
INPUT_FILE = "proxy_list.txt"
TEMP_FILE = "proxy_list_temp.txt"
OUTPUT_FILE = "proxy_list_active.txt"

def check_proxy(ip, port):
    """Cek apakah IP adalah proxy menggunakan API."""
    url = f"{PROXY_HEALTH_CHECK_API}?ip={ip}&port={port}&host={HOST}&tls={TLS}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get("proxyip", False)  # True jika proxy aktif
    except Exception as e:
        print(f"Error checking {ip}:{port} -> {e}")
        return False

def main():
    with open(INPUT_FILE, "r") as infile, open(TEMP_FILE, "w") as tempfile:
        for line in infile:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                ip, port = parts[0], parts[1]
                if check_proxy(ip, port):
                    tempfile.write(line)
                time.sleep(1)  # Hindari spam API

    # Setelah semua selesai, pindahkan hasil ke proxy_list_active.txt
    with open(TEMP_FILE, "r") as tempfile, open(OUTPUT_FILE, "w") as outfile:
        outfile.write(tempfile.read())

if __name__ == "__main__":
    main()
