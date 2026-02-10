def handle_procurement(state: GlobalState) -> dict:
    domain = state.domain_name
    account_id = state.account_id

    # (Later) real API calls go here
    # availability = check_domain_availability(domain)
    # ownership = check_domain_owner(domain)

    return {
        "status": "SUCCESS",
        "action": "PROCURE_DOMAIN",
        "domain": domain,
        "account_id": account_id,
        "order_id": "ORD-123456",
        "message": f"Procure Domain completed for {domain}."
    }
    
def handle_transfer(state: GlobalState) -> dict:
    domain = state.domain_name
    account_id = state.account_id
    auth_code = state.auth_code

    return {
        "status": "SUCCESS",
        "action": "TRANSFER_DOMAIN",
        "domain": domain,
        "account_id": account_id,
        "transfer_id": "TRF-987654",
        "message": f"Transfer initiated for {domain}."
    }
