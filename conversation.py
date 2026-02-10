from graph import app

THREAD_ID = "conversation-test-001"


def invoke_app(state):
    """
    ALWAYS invoke graph with checkpoint config
    """
    return app.invoke(
        state,
        config={
            "configurable": {
                "thread_id": THREAD_ID
            }
        }
    )


def print_assistant(state):
    for msg in reversed(state["messages"]):
        if msg["role"] == "assistant":
            print("ASSISTANT:", msg["content"])
            return


def run():
    state = {"messages": []}

    print("\n### TURN 1 ###")
    state["messages"].append({
        "role": "user",
        "content": "Procure code.com and transfer example.org"
    })
    state = invoke_app(state)
    print_assistant(state)

    print("\n### TURN 2 ###")
    state["messages"].append({
        "role": "user",
        "content": "Account id is 123"
    })
    state = invoke_app(state)
    print_assistant(state)

    print("\n### TURN 3 ###")
    state["messages"].append({
        "role": "user",
        "content": "Auth code is XYZ-999"
    })
    state = invoke_app(state)

    print("\n### FINAL OUTPUT ###")
    for msg in state["messages"]:
        if msg["role"] == "assistant":
            print("ASSISTANT:", msg["content"])


if __name__ == "__main__":
    run()