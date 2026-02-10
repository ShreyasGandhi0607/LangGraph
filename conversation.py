from graph import app


def print_conversation(state):
    print("\n" + "=" * 50)
    print("CONVERSATION")
    print("=" * 50)
    for msg in state["messages"]:
        role = msg["role"].upper()
        print(f"{role}: {msg['content']}")
    print("=" * 50 + "\n")


def run_conversation(user_inputs):
    """
    user_inputs: list[str]
    Each entry simulates one user turn
    """

    state = {
        "messages": []
    }

    for user_msg in user_inputs:
        # User sends a message
        state["messages"].append({
            "role": "user",
            "content": user_msg
        })

        # Invoke graph with updated state
        state = app.invoke(state)

        # Print conversation after each turn
        print_conversation(state)

    return state


if __name__ == "__main__":
    # -------------------------------
    # TEST 1: SINGLE TASK (PROCURE)
    # -------------------------------
    print("\n### TEST 1: SINGLE TASK (PROCURE) ###")

    run_conversation([
        "I want to procure code.com",
        "My account id is 12345"
    ])

    # -------------------------------
    # TEST 2: MULTI TASK
    # -------------------------------
    print("\n### TEST 2: MULTI TASK (PROCURE + TRANSFER) ###")

    run_conversation([
        "Procure code.com and transfer example.org",
        "Account id is 123",
        "Auth code is XYZ-999"
    ])