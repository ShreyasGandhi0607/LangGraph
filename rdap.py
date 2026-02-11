import httpx
import asyncio


# Known RDAP servers
RDAP_SERVERS = {
    "com": "https://rdap.verisign.com/com/v1/domain/",
    "net": "https://rdap.verisign.com/net/v1/domain/",
    "org": "https://rdap.publicinterestregistry.org/rdap/org/domain/",
    "in": "https://rdap.registry.in/domain/",
    "ai": "https://rdap.nic.ai/domain/",
}


class RDAPService:

    def __init__(self, timeout=10):
        self.timeout = timeout

    def _get_tld(self, domain):
        return domain.split(".")[-1].lower()

    async def _discover_rdap_server(self, tld):
        """
        Fallback via IANA bootstrap
        """
        bootstrap_url = "https://data.iana.org/rdap/dns.json"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(bootstrap_url)

        data = response.json()

        for service in data["services"]:
            tlds = service[0]
            servers = service[1]
            if tld in tlds:
                return servers[0]

        return None

    async def _get_rdap_url(self, domain):
        tld = self._get_tld(domain)

        if tld in RDAP_SERVERS:
            return RDAP_SERVERS[tld] + domain

        # Fallback discovery
        discovered = await self._discover_rdap_server(tld)
        if discovered:
            return discovered.rstrip("/") + "/domain/" + domain

        return None

    async def lookup(self, domain):
        url = await self._get_rdap_url(domain)

        if not url:
            return {
                "domain": domain,
                "supported": False,
                "error": "TLD not supported"
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)

        if response.status_code == 404:
            return {"domain": domain, "available": True}

        if response.status_code != 200:
            return {
                "domain": domain,
                "error": f"RDAP error {response.status_code}"
            }

        data = response.json()
        return self._parse(data, domain)

    def _parse(self, data, domain):
        result = {
            "domain": domain,
            "available": False,
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
            if event["eventAction"] == "registration":
                result["creation_date"] = event["eventDate"]
            elif event["eventAction"] == "expiration":
                result["expiration_date"] = event["eventDate"]
            elif event["eventAction"] == "last changed":
                result["updated_date"] = event["eventDate"]

        # Nameservers
        for ns in data.get("nameservers", []):
            result["nameservers"].append(ns.get("ldhName"))

        # Registrar info
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
                        if field[0] == "email":
                            result["abuse_email"] = field[3]
                        if field[0] == "tel":
                            result["abuse_phone"] = field[3]

        return result