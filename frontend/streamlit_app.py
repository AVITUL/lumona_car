import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def load_env():
    project_root = Path(__file__).parent.parent

    env_path = project_root / "dev.env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        raise FileNotFoundError(f"Environment file not found at {env_path}")


load_env()

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

from app.core.indexing.indexer import indexer
from app.core.retrieving.retriever import retriever

if "messages" not in st.session_state:
    st.session_state.messages = []
if "references" not in st.session_state:
    st.session_state.references = ""

st.set_page_config(layout="wide")

with st.sidebar:
    st.header("Index Documents")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="pdf_uploader")

    if uploaded_file:
        file_key = f"processed_{uploaded_file.name}"
        if file_key not in st.session_state:
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)

            temp_path = temp_dir / uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            with st.spinner("Indexing document..."):
                indexer.index_document(str(temp_path))
            st.success(f"Indexed: {uploaded_file.name}")
            temp_path.unlink()

            st.session_state[file_key] = True

st.header("Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()

        status_placeholder.text("Building query...")
        answer = retriever.get_answer(
            question, ""
        )  # Context parameter is empty for now

        st.session_state.messages.append({"role": "assistant", "content": answer})
        status_placeholder.markdown(answer)

        st.session_state.references = "\n".join(
            line for line in answer.split("\n") if line.startswith("[") and "](" in line
        )

with st.sidebar.container():
    st.header("References")
    st.markdown(st.session_state.references)
