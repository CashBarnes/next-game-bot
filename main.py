from chat.chatbot import get_response
from utils.user_memory import UserMemory


def main():
    print("Welcome to NextGameBot!")
    memory = UserMemory()  # make sure memory is initialized here

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        if user_input.lower() == "likes":
            print("Liked games:", ", ".join(memory.get_likes()) or "None")
            continue

        if user_input.lower() == "dislikes":
            print("Disliked games:", ", ".join(memory.get_dislikes()) or "None")
            continue

        if user_input.lower() == "reset":
            memory.reset()
            print("Memory cleared.")
            continue

        response = get_response(user_input, memory)
        print(f"NextGameBot: {response}\n")


if __name__ == "__main__":
    main()
