def handle_memory_command(command: str) -> str | None:
    """Handle explicit memory commands."""

    normalized = command.casefold().strip()

    # Remember the user's name
    if normalized.startswith("my name is "):
        name = command[len("my name is "):].strip()

        if not name:
            return "I did not catch your name. Please try again."

        remember("name", name)

        return f"Understood. I will remember that your name is {name}."

    # Remember something explicitly
    if normalized.startswith("remember that "):
        information = command[len("remember that "):].strip()

        if not information:
            return "What would you like me to remember?"

        # Store the complete statement for now
        remember("last_memory", information)

        return f"Understood. I will remember that {information}."

    # Recall name
    if normalized in {
        "what is my name",
        "what's my name",
        "who am i",
    }:
        name = recall("name")

        if name:
            return f"Your name is {name}."

        return "I do not know your name yet."

    # Recall the last explicitly saved memory
    if normalized in {
        "what did i ask you to remember",
        "what did i tell you to remember",
        "what do you remember",
    }:
        memory = recall("last_memory")

        if memory:
            return f"You asked me to remember that {memory}."

        return "You haven't asked me to remember anything yet."

    return None