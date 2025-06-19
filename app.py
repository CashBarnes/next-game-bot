import streamlit as st
from chat.chatbot import get_response
from utils.memory import UserMemory

st.set_page_config(page_title="NextGameBot", layout="centered")
st.title("NextGameBot")

# Persist memory across reruns
if "memory" not in st.session_state:
    st.session_state.memory = UserMemory()

# Other session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input handling
user_input = st.chat_input("What are you in the mood to play? (Type 'likes', 'dislikes', or 'reset' for memory options)")
if user_input:
    user_input_lower = user_input.strip().lower()

    if user_input_lower in ["exit", "quit"]:
        st.stop()

    elif user_input_lower == "likes":
        likes = st.session_state.memory.get_likes()
        msg = "Liked games: " + (", ".join(likes) if likes else "None")
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("NextGameBot", msg))

    elif user_input_lower == "dislikes":
        dislikes = st.session_state.memory.get_dislikes()
        msg = "Disliked games: " + (", ".join(dislikes) if dislikes else "None")
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("NextGameBot", msg))

    elif user_input_lower == "reset":
        st.session_state.memory.reset()
        msg = "Memory cleared."
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("NextGameBot", msg))

    else:
        response = get_response(user_input, st.session_state.memory)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("NextGameBot", response))

# Display history
for speaker, msg in st.session_state.chat_history:
    st.chat_message("user" if speaker == "You" else "assistant").markdown(msg)
