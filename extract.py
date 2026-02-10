import json

def extract_fields(state: GlobalState):
    msg = llm.invoke(
        SLOT_PROMPT.format(
            intent=state.intent,
            domain_name=state.domain_name,
            account_id=state.account_id,
            auth_code=state.auth_code,
            settings_type=state.settings_type,
            user_message=state.messages[-1]["content"]
        )
    )

    raw = msg.content if hasattr(msg, "content") else msg

    try:
        result = json.loads(raw)
    except Exception:
        result = {}

    if not isinstance(result, dict):
        result = {}

    for k, v in result.items():
        if hasattr(state, k) and v and getattr(state, k) is None:
            setattr(state, k, v)

    return state