from graph import app

config = {
    "configurable": {
        "thread_id": "conversation-test-1"
    }
}

state = {
    "messages": []
}

print("\n### TURN 1 ###")
state = run_turn(
    state,
    "Procure code.com and transfer example.org",
    config
)

print("\n### TURN 2 ###")
state = run_turn(
    state,
    "Account id is 123",
    config
)

print("\n### TURN 3 ###")
state = run_turn(
    state,
    "Auth code is XYZ-999",
    config
)

print("\n### FINAL STATE ###")
for m in state["messages"]:
    print(m["role"], ":", m["content"])