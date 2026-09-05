import subprocess
import base64
import json
import requests

CLOUDFLARED_SERVICE_NAME = "cloudflared"

def set_cloudflared_token(token: str):
    try:
        subprocess.run(["sudo", "cloudflared", "service", "uninstall"], capture_output=True)
        res = subprocess.run(
            ["sudo", "cloudflared", "service", "install", token],
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            return {"status": "error", "message": res.stderr.strip() or res.stdout.strip()}
        return {"status": "success", "message": "Cloudflared Tunnel connected!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_cloudflared_status():
    try:
        res = subprocess.run(["sudo", "systemctl", "is-active", CLOUDFLARED_SERVICE_NAME], capture_output=True, text=True)
        active = res.stdout.strip() == "active"
        return {"status": "active" if active else "inactive"}
    except Exception as e:
        return {"status": "inactive", "error": str(e)}

def get_cf_account_id(api_token: str):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.get("https://api.cloudflare.com/client/v4/accounts", headers=headers)
        data = res.json()
        accounts = data.get("result") or []
        if data.get("success") and accounts:
            return {
                "status": "success",
                "account_id": accounts[0]["id"],
                "account_name": accounts[0].get("name"),
                "multiple_accounts": len(accounts) > 1
            }
    except Exception as e:
        print("Warning: /accounts lookup gagal, coba fallback ke Zone bypass:", e)

    try:
        url = "https://api.cloudflare.com/client/v4/zones?per_page=1"
        res = requests.get(url, headers=headers)
        res.raise_for_status()

        zones = res.json().get("result", [])
        if not zones:
            return {
                "status": "error",
                "message": "Account ID tidak ditemukan. Pastikan token punya izin 'Account Settings: Read' atau minimal 'Zone: Read'."
            }

        account = zones[0].get("account", {})
        account_id = account.get("id")
        if not account_id:
            return {"status": "error", "message": "Gagal mengekstrak Account ID dari Zone."}

        return {"status": "success", "account_id": account_id, "account_name": account.get("name")}
    except Exception as e:
        return {"status": "error", "message": f"Gagal mendapatkan Account ID: {str(e)}"}

def fetch_cf_tunnels(api_token: str, account_id: str = None):
    if not account_id:
        acc_res = get_cf_account_id(api_token)
        if acc_res["status"] == "error":
            return acc_res
        account_id = acc_res["account_id"]

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        tunnels = res.json().get("result", [])
        return {"status": "success", "account_id": account_id, "tunnels": tunnels}
    except Exception as e:
        return {"status": "error", "message": f"Gagal mengambil daftar Tunnel: {str(e)}"}

def fetch_cf_tunnel_token(account_id: str, tunnel_id: str, api_token: str):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/token"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        token = res.json().get("result")
        return {"status": "success", "token": token}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def decode_tunnel_token(token: str):
    try:
        padded = token + '=' * (-len(token) % 4)
        decoded = json.loads(base64.b64decode(padded).decode('utf-8'))
        return {"account_id": decoded.get("a"), "tunnel_id": decoded.get("t")}
    except Exception:
        return None

def find_zone_for_hostname(hostname: str, api_token: str):
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    try:
        res = requests.get(
            "https://api.cloudflare.com/client/v4/zones?status=active&per_page=50",
            headers=headers
        )
        data = res.json()
        if not data.get("success"):
            errors = data.get("errors", [])
            msg = errors[0].get("message") if errors else "Gagal mengambil daftar zone"
            return {"status": "error", "message": msg}

        zones = {z["name"]: z["id"] for z in data.get("result", [])}
        parts = hostname.split(".")

        for i in range(len(parts) - 1):
            candidate = ".".join(parts[i:])
            if candidate in zones:
                return {"status": "success", "zone_id": zones[candidate], "domain_name": candidate}

        return {"status": "error", "message": f"Tidak ada zone aktif di akun ini yang cocok untuk '{hostname}'."}
    except Exception as e:
        return {"status": "error", "message": f"Gagal mencari zone: {str(e)}"}

def get_tunnel_routes(account_id: str, tunnel_id: str, api_token: str):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        ingress = res.json().get("result", {}).get("config", {}).get("ingress", [])
        routes = [r for r in ingress if "hostname" in r]
        return {"status": "success", "routes": routes}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_tunnel_routes(account_id: str, tunnel_id: str, api_token: str, routes: list):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    ingress_payload = routes + [{"service": "http_status:404"}]
    payload = {"config": {"ingress": ingress_payload}}

    try:
        res = requests.put(url, headers=headers, json=payload)
        res.raise_for_status()
        return {"status": "success", "message": "Routes updated successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_cloudflared():
    try:
        subprocess.run(["sudo", "systemctl", "start", CLOUDFLARED_SERVICE_NAME], check=True)
        return {"status": "success", "message": "Cloudflared berhasil dijalankan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def stop_cloudflared():
    try:
        subprocess.run(["sudo", "systemctl", "stop", CLOUDFLARED_SERVICE_NAME], check=True)
        return {"status": "success", "message": "Cloudflared berhasil dimatikan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}