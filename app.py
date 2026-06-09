import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Study Buddy", page_icon="📚")
st.title("📚 Study Buddy")
st.caption("Upload your notes or lecture PDFs and ask questions about them.")

# Generate a unique session ID per browser session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar — file upload
with st.sidebar:
    st.header("Upload a document")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file:
        if st.button("Ingest document"):
            with st.spinner("Reading and indexing..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Done! {data['pages']} pages, {data['chunks']} chunks indexed.")
                else:
                    st.error("Upload failed.")

    st.divider()
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "sources" in msg:
            st.caption(f"📄 Sources: Pages {msg['sources']}")

# Chat input
question = st.chat_input("Ask something about your documents...")

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # Get answer from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "question": question,
                    "session_id": st.session_state.session_id
                }
            )

        if response.status_code == 200:
            data = response.json()
            st.write(data["answer"])
            st.caption(f"📄 Sources: Pages {data['sources']}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["answer"],
                "sources": data["sources"]
            })
        else:
            st.error("Something went wrong.")