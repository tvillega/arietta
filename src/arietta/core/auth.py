import hashlib
import hmac
import time

import jwt
import requests
from flask import abort, request


def verify_github_signature(webhook_secret):
    """Validates the X-Hub-Signature-256 header sent by GitHub."""
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        abort(403, description="Missing signature header")

    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        abort(403, description="Unsupported signature algorithm")

    mac = hmac.new(
        webhook_secret.encode("utf-8"),
        msg=request.data,
        digestmod=hashlib.sha256
    )

    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403, description="Signature mismatch")

def generate_jwt(private_key_path, app_id):
    """Generates a JWT for authenticating as the GitHub App."""
    with open(private_key_path, "r") as key_file:
        private_key = key_file.read()

    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 540,
        "iss": app_id
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_access_token(installation_id, private_key_path, app_id):
    """Obtains an installation access token for repository API requests."""
    jwt_token = generate_jwt(private_key_path, app_id)
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "vnd.github+json"
    }
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers
    )
    return response.json().get("token")
