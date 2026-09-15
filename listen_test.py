from listen import listen

while True:
    text = listen()

    if text:
        print("Detected:", text)

        if text == "exit":
            break