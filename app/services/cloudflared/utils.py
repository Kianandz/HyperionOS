import base64
import json


def decode_tunnel_token(token: str):
    try:
        padded = token + "=" * (-len(token) % 4)
        decoded = json.loads(base64.b64decode(padded).decode("utf-8"))
        return {"account_id": decoded.get("a"), "tunnel_id": decoded.get("t")}
    except Exception:
        return None
