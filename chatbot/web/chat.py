import streamlit as st
import time
from chatbot.backend import *
from chatbot.backend.bot_graph import run_workflow

# if "backend_initialized" not in st.session_state:
#     prompt_controller, llm, retriever = init()
#     st.session_state.backend_initialized = True

# if prompt_controller and llm and retriever:


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
def response_generator(question, role):
    response = run_workflow(question=question, role=role, verbose=True)

    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Chat with Choi")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
role = st.selectbox(
    "Which role would you like the chatbot to act as?",
    ("Researcher", "Stand-up comedian", "Motivational speaker", "Son", "Auto-detect"),
)
# st.write("You selected:", role)
st.markdown("</div>", unsafe_allow_html=True)

# Accept user input
if prompt := st.chat_input("What's up?"):
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    print(st.session_state)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(question=prompt, role=role))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

