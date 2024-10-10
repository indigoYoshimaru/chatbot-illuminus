import shlex
import subprocess
from pathlib import Path

import modal

image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "streamlit",  # For frontend UI
    "loguru",  # For logging
    "langchain",  # Core framework for RAG
    "langchain-core",  # Core components for chains and prompts
    "langchain-community",  # Community-supported tools like Ollama
    "langchain-nomic",  # Nomic embeddings (or replace with your desired embedding library)
    "chromadb",  # Vector store for retrieval
    "typing-extensions",  # Type hinting support
    "pydantic",
).apt_install("curl", "unzip")

app = modal.App("chat-with-choi-app", image=image)

streamlit_script_local_path = Path("chatbot/web/chat.py")
streamlit_script_remote_path = Path("/root/chatbot/web/chat.py")

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "chat.py not found! Place the script with your streamlit app in the same directory."
    )

streamlit_script_mount = modal.Mount.from_local_file(
    streamlit_script_local_path,
    streamlit_script_remote_path,
)


@app.function(
    allow_concurrent_inputs=2,
    mounts=[streamlit_script_mount],
)
@modal.web_server(8000)
def run():
    import os
    
    import subprocess

    # Install Ollama inside the container
    subprocess.run(
        [
            "curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama"
        ], check=True
    )
    # subprocess.run(
    #     ["unzip", "ollama-linux.zip"], check=True
    # )
    # subprocess.run(
    #     ["mv", "ollama", "/usr/local/bin/ollama"], check=True
    # )

    # Start Ollama server in the background
    subprocess.Popen(["ollama", "serve"])
    target = shlex.quote(str(streamlit_script_remote_path))
    cmd = f"python -m streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)

    os.system("python -m streamlit run chatbot/web/chat.py")

