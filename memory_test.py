from memory import (
    remember,
    recall,
    forget,
    get_all_memories,
)


print("🧠 JARVIS MEMORY TEST")
print("---------------------")


# Save information
remember("name", "Dion")
remember("favorite_language", "Python")
remember("assistant_name", "JARVIS")


# Read information
print("\nName:", recall("name"))
print("Favorite language:", recall("favorite_language"))
print("Assistant:", recall("assistant_name"))


# Show everything
print("\nAll memories:")
print(get_all_memories())


# Delete one memory
forget("favorite_language")

print("\nAfter deleting favorite language:")
print(get_all_memories())