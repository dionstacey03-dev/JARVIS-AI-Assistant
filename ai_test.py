from ai import ask_ai


print("🤖 JARVIS AI TEST")
print("------------------")


while True:

    question = input("\nYou: ")

    if question.lower() in {"exit", "quit"}:
        break

    response = ask_ai(question)

    print("Jarvis:", response)