# -----------------------------------------------------------
# IMPORTANT: This MUST be the first import (fixes VDI SSL issue)
# -----------------------------------------------------------
import pip_system_certs.wrapt_requests

import httpx
from typing import Dict, Optional


# -----------------------------------------------------------
# RDAP Servers (Correct Registry Endpoints)
# -----------------------------------------------------------
RDAP_SERVERS = {
    "com": "https://rdap.verisign.com/com/v1/domain/",
    "net": "https://rdap.verisign.com/net/v1/domain/",
    "org": "https://rdap.publicinterestregistry.org/rdap/domain/",
    "in":  "https://rdap.registry.in/rdap/domain/",
    "ai":  "https://rdap.nic.ai/domain/",
    "io":  "https://rdap.nic.io/domain/",
}


# -----------------------------------------------------------
# Main Function: Check Domain
# -----------------------------------------------------------
def check_domain(domain: str) -> Dict[str, Optional[str]]:
    """
    Check domain registration status using RDAP.
    """

    domain = domain.strip().lower()

    if "." not in domain:
        return _error("Invalid domain format")

    tld = domain.split(".")[-1]

    if tld not in RDAP_SERVERS:
        return _error(f"Unsupported TLD: .{tld}")

    url = RDAP_SERVERS[tld] + domain

    headers = {
        "User-Agent": "Mozilla/5.0 (DomainChecker/1.0)",
        "Accept": "application/rdap+json, application/json"
    }

    try:
        response = httpx.get(
            url,
            headers=headers,
            timeout=10,
            follow_redirects=True
        )

        data = response.json()

        # Some registries return 200 even if NOT registered
        if "errorCode" in data:
            return {
                "registered": False,
                "registrar": None,
                "expiration_date": None,
                "error": None
            }

        registrar = _extract_registrar(data)
        expiration_date = _extract_expiration_date(data)

        return {
            "registered": True,
            "registrar": registrar,
            "expiration_date": expiration_date,
            "error": None
        }

    except httpx.RequestError as e:
        return _error(f"Network error: {str(e)}")

    except Exception as e:
        return _error(f"Unexpected error: {str(e)}")


# -----------------------------------------------------------
# Helper: Extract Registrar
# -----------------------------------------------------------
def _extract_registrar(rdap_data: dict) -> Optional[str]:
    try:
        for entity in rdap_data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [])
                if len(vcard) > 1:
                    for field in vcard[1]:
                        if field[0] == "fn":
                            return field[3]
        return "Unknown"
    except Exception:
        return "Unknown"


# -----------------------------------------------------------
# Helper: Extract Expiration Date
# -----------------------------------------------------------
def _extract_expiration_date(rdap_data: dict) -> Optional[str]:
    try:
        for event in rdap_data.get("events", []):
            if event.get("eventAction") == "expiration":
                return event.get("eventDate")
        return "N/A"
    except Exception:
        return "N/A"


# -----------------------------------------------------------
# Helper: Standard Error Response
# -----------------------------------------------------------
def _error(message: str) -> Dict[str, Optional[str]]:
    return {
        "registered": None,
        "registrar": None,
        "expiration_date": None,
        "error": message
    }


# -----------------------------------------------------------
# Local Test Runner
# -----------------------------------------------------------
if __name__ == "__main__":
    test_domains = [
        "google.com",
        "wikipedia.org",
        "nic.in",
        "openai.com",
        "example.ai",
        "github.io"
    ]

    for d in test_domains:
        print(f"\nChecking: {d}")
        result = check_domain(d)
        print(result)