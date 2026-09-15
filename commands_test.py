from commands import execute


test_commands = [
    "open notepad",
    "open calculator",
    "open youtube",
    "what time is it",
    "what is the date",
    "search google for Python tutorials",
    "search youtube for Python programming",
]


for command in test_commands:

    print()
    print("Command:", command)

    response = execute(command)

    print("JARVIS:", response)