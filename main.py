from chat.chatbot import get_response

def main():
    print("Welcome to NextGameBot!")
    memory = {}  # state between turns

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        response, memory = get_response(user_input, memory)
        print(f"NextGameBot: {response}")

if __name__ == "__main__":
    main()
