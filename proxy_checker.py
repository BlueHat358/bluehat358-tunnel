import requests

PROXY_HEALTH_CHECK_API = "https://api-proxy.bluehat358.us.kg"
INPUT_FILE = "proxy_list.txt"
TEMP_FILE = "proxy_list_temp.txt"
OUTPUT_FILE = "proxy_list_active.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_proxy(ip, port, host="speed.cloudflare.com", tls="true"):
    url = f"{PROXY_HEALTH_CHECK_API}?ip={ip}&port={port}&host={host}&tls={tls}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()

        # Jika response berisi error, anggap proxy mati
        if "error" in data:
            print(f"⚠️ Error response from API for {ip}:{port} → {data['error']}")
            return False

        # Pastikan hasilnya dari Cloudflare & ProxyIP True
        if data.get("proxyip") is True:
            return True
        else:
            return False  # Proxy tidak valid atau bukan CF
    except requests.RequestException as e:
        print(f"⚠️ Request error for {ip}:{port} → {e}")
        return False

def main():
    with open(INPUT_FILE, "r") as f, open(TEMP_FILE, "w") as temp_f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue  # Skip jika format tidak valid

            ip, port = parts[:2]  # Ambil IP dan Port
            is_active = check_proxy(ip, port)

            # Log status ke output GitHub Actions
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
