import streamlit as st
import random
import time

st.markdown(
    """
    <style>
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        z-index: 100;
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Simple chat")


# option = st.selectbox(
#     "Which role would you like the chatbot to act as?",
#     ("Researcher", "Stand-up comedian", "Motivational speaker", "Son"),
# )
# st.write("You selected:", option)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    print(st.session_state)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Fixed option box at the bottom of the screen
st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
role = st.selectbox(
    "Which role would you like the chatbot to act as?",
    ("Researcher", "Stand-up comedian", "Motivational speaker", "Son"),
)
st.write("You selected:", role)
st.markdown("</div>", unsafe_allow_html=True)
