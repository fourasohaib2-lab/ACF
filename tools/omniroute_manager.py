#!/usr/bin/env python3

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("OMNIROUTE_URL", "http://127.0.0.1:20128").rstrip("/")
API_KEY = os.getenv("OMNIROUTE_API_KEY")


def request(method, path, data=None):
    url = BASE_URL + path

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8", errors="replace")

            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                result = raw

            return response.status, result

    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = raw

        return e.code, result

    except Exception as e:
        return None, {"error": repr(e)}


def show(title, status, data):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    if status is not None:
        print("HTTP:", status)

    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_connection():
    status, data = request("GET", "/api/provider-nodes")
    show("PROVIDER NODES", status, data)

    if status == 200:
        print("\nOK: accès management autorisé.")
        return True

    if status == 401:
        print("\nERREUR 401: authentification absente ou incorrecte.")
        return False

    if status == 403:
        print("\nERREUR 403: le token fourni n'est PAS un management token OmniRoute.")
        return False

    return False


def list_provider_nodes():
    status, data = request("GET", "/api/provider-nodes")
    show("LIST PROVIDER NODES", status, data)


def list_provider_models():
    status, data = request("GET", "/api/provider-nodes/models")
    show("PROVIDER MODELS", status, data)


def test_qwen_direct():
    model = "/mnt/beegfs/sfoura/models/Qwen3-Coder-Next-GGUF/Q5_K_M/Qwen3-Coder-Next-Q5_K_M-00001-of-00003.gguf"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Respond only with ACF-QWEN-OK",
            }
        ],
        "max_tokens": 8,
        "stream": False,
    }

    status, data = request_qwen(payload)

    show("DIRECT QWEN TEST", status, data)


def request_qwen(data):
    url = "http://127.0.0.1:18080/v1/chat/completions"

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            raw = response.read().decode("utf-8", errors="replace")

            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                result = raw

            return response.status, result

    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = raw

        return e.code, result

    except Exception as e:
        return None, {"error": repr(e)}


def test_omniroute():
    model = "/mnt/beegfs/sfoura/models/Qwen3-Coder-Next-GGUF/Q5_K_M/Qwen3-Coder-Next-Q5_K_M-00001-of-00003.gguf"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Respond only with OMNIROUTE-QWEN-OK",
            }
        ],
        "max_tokens": 8,
        "stream": False,
    }

    status, data = request("POST", "/v1/chat/completions", payload)

    show("OMNIROUTE TEST", status, data)


def main():
    print("=" * 80)
    print("OMNIROUTE PYTHON MANAGER")
    print("=" * 80)
    print("OmniRoute:", BASE_URL)
    print("API key:", "PRESENT" if API_KEY else "ABSENT")

    if not API_KEY:
        print("\nOMNIROUTE_API_KEY n'est pas définie.")
        sys.exit(1)

    print("\n[1] Test accès management")
    management_ok = test_connection()

    print("\n[2] Test provider nodes")
    list_provider_nodes()

    print("\n[3] Test provider models")
    list_provider_models()

    print("\n[4] Test Qwen direct")
    test_qwen_direct()

    print("\n[5] Test OmniRoute")
    test_omniroute()

    if not management_ok:
        print()
        print("=" * 80)
        print("IMPORTANT")
        print("=" * 80)
        print("Le script fonctionne, mais OMNIROUTE_API_KEY est une clé client normale et non un management token.")
        print("Il faut utiliser le token de management attendu par les endpoints /api/provider-nodes.")


if __name__ == "__main__":
    main()
