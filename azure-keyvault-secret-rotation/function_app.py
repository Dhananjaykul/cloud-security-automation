"""SecureMart demonstration: Key Vault secret *version* rotation, not target-system rotation."""
import json
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def rotate_demo_secret(secret_name: str) -> tuple[str, str]:
    """Create a new Key Vault version with a synthetic credential; never log its value."""
    client = SecretClient(
        vault_url=os.environ["KEY_VAULT_URL"],
        credential=DefaultAzureCredential(),
    )
    current = client.get_secret(secret_name)
    new_secret = client.set_secret(
        secret_name,
        secrets.token_urlsafe(32),
        expires_on=datetime.now(timezone.utc) + timedelta(days=90),
    )
    return current.properties.version, new_secret.properties.version


@app.route(route="rotate-secret", methods=["POST"])
def rotate_secret(req: func.HttpRequest) -> func.HttpResponse:
    try:
        name = os.environ["SECRET_NAME"]
        previous_version, new_version = rotate_demo_secret(name)
        logging.info("Rotation succeeded for secret %s", name)
        return func.HttpResponse(
            json.dumps({"status": "success", "secret_name": name,
                        "previous_version": previous_version, "new_version": new_version}),
            status_code=200, mimetype="application/json",
        )
    except Exception:
        logging.exception("Rotation failed")
        return func.HttpResponse('{"status":"failed"}', status_code=500,
                                 mimetype="application/json")


@app.event_grid_trigger(arg_name="event")
def rotate_secret_on_expiry(event: func.EventGridEvent):
    logging.info("Received Key Vault Event Grid event")
    if event.event_type != "Microsoft.KeyVault.SecretNearExpiry":
        logging.info("Ignoring unrelated event type")
        return
    secret_name = event.subject.rstrip("/").split("/")[-1]
    if secret_name.lower() != os.environ["SECRET_NAME"].lower():
        logging.info("Ignoring unrelated secret event")
        return
    # LAB ONLY: no idempotency check or validation of target-system credential.
    previous_version, new_version = rotate_demo_secret(os.environ["SECRET_NAME"])
    logging.info("Event Grid rotation completed: %s -> %s", previous_version, new_version)
