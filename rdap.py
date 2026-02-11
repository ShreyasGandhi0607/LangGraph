import asyncio
from typing import Dict, Optional, List

import httpx


# Known stable RDAP endpoints
RDAP_SERVERS = {
    "com": "https://rdap.verisign.com/com/v1/domain/",
    "net": "https://rdap.verisign.com/net/v1/domain/",
    "org": "https://rdap.publicinterestregistry.org/rdap/org/domain/",
    "in": "https://rdap.registry.in/rdap/domain/",
    "ai": "https://rdap.nic.ai/rdap/domain/",
}


class RDAPService:
    def __init__(self, timeout: int = 10, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=self.timeout)

    # ----------------------------
    # Utility
    # ----------------------------

    def _get_tld(self, domain: str) -> str:
        return domain.strip().lower().split(".")[-1]

    async def _discover_rdap_server(self, tld: str) -> Optional[str]:
        """
        Uses IANA RDAP bootstrap file to discover correct RDAP base URL.
        """
        bootstrap_url = "https://data.iana.org/rdap/dns.json"

        try:
            response = await self.client.get(bootstrap_url)
            data = response.json()

            for service in data.get("services", []):
                tlds = service[0]
                servers = service[1]

                if tld in tlds and servers:
                    base = servers[0].rstrip("/")
                    return f"{base}/domain/"

        except Exception:
            pass

        return None

    async def _get_rdap_url(self, domain: str) -> Optional[str]:
        tld = self._get_tld(domain)

        if tld in RDAP_SERVERS:
            return RDAP_SERVERS[tld] + domain

        discovered = await self._discover_rdap_server(tld)
        if discovered:
            return discovered + domain

        return None

    # ----------------------------
    # Core Lookup
    # ----------------------------

    async def lookup(self, domain: str) -> Dict:
        url = await self._get_rdap_url(domain)

        if not url:
            return {
                "domain": domain,
                "supported": False,
                "error": "TLD not supported",
            }

        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url)

                # Most registries return 4xx if domain not found
                if response.status_code != 200:
                    return {
                        "domain": domain,
                        "available": True,
                        "registered": False,
                    }

                data = response.json()

                # Some registries return error inside JSON
                if data.get("objectClassName") != "domain":
                    return {
                        "domain": domain,
                        "available": True,
                        "registered": False,
                    }

                return self._parse(domain, data)

            except httpx.TimeoutException:
                if attempt == self.max_retries - 1:
                    return {
                        "domain": domain,
                        "error": "Request timeout",
                    }
                await asyncio.sleep(1)

            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    return {
                        "domain": domain,
                        "error": f"Connection error: {str(e)}",
                    }
                await asyncio.sleep(1)

            except Exception as e:
                return {
                    "domain": domain,
                    "error": f"Unexpected error: {str(e)}",
                }

    # ----------------------------
    # Parsing
    # ----------------------------

    def _parse(self, domain: str, data: Dict) -> Dict:
        result = {
            "domain": domain,
            "available": False,
            "registered": True,
            "creation_date": None,
            "expiration_date": None,
            "updated_date": None,
            "status": data.get("status", []),
            "nameservers": [],
            "registrar": None,
            "iana_id": None,
            "abuse_email": None,
            "abuse_phone": None,
        }

        # Events
        for event in data.get("events", []):
            action = event.get("eventAction")
            if action == "registration":
                result["creation_date"] = event.get("eventDate")
            elif action == "expiration":
                result["expiration_date"] = event.get("eventDate")
            elif action in ("last changed", "last update of RDAP database"):
                result["updated_date"] = event.get("eventDate")

        # Nameservers
        for ns in data.get("nameservers", []):
            if ns.get("ldhName"):
                result["nameservers"].append(ns["ldhName"])

        # Registrar
        for entity in data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                result["iana_id"] = (
                    entity.get("publicIds", [{}])[0].get("identifier")
                )

                vcard = entity.get("vcardArray", [])
                if len(vcard) > 1:
                    for field in vcard[1]:
                        if field[0] == "fn":
                            result["registrar"] = field[3]
                        elif field[0] == "email":
                            result["abuse_email"] = field[3]
                        elif field[0] == "tel":
                            result["abuse_phone"] = field[3]

        return result

    # ----------------------------
    # Batch Lookup
    # ----------------------------

    async def lookup_many(self, domains: List[str]) -> List[Dict]:
        tasks = [self.lookup(domain) for domain in domains]
        return await asyncio.gather(*tasks)

    async def close(self):
        await self.client.aclose()