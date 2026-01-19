import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import uuid

st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖", layout="wide")
st.markdown("## 🤖 AI Chat Assistant")

BACKEND_URL = "http://127.0.0.1:8000"


if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "system", "content": "You are a helpful AI assistant"}]

if "history_messages" not in st.session_state:
    st.session_state.history_messages = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False


with st.sidebar:
    mode = st.radio("▶️ Select Mode",["😺 Chat With AI", "📺 Image Generation"])

    st.divider()
    st.subheader("👁️‍🗨️ Your Chats")

    res = requests.get(f"{BACKEND_URL}/chat-sessions")
    if res.status_code == 200:
        for chat in res.json():
            if st.button(chat["title"], key=chat["chat_id"]):
                st.session_state.current_chat_id = chat["chat_id"]
                hist = requests.get(f"{BACKEND_URL}/get-chat-history/{chat['chat_id']}")
                if hist.status_code == 200:
                    st.session_state.chat_messages = hist.json()
                st.rerun()

    st.divider()

    if st.button("🗑️ Clear Current Chat"):
        requests.delete(f"{BACKEND_URL}/delete-chat-history/{st.session_state.current_chat_id}")
        st.session_state.chat_messages = [{"role": "system", "content": "You are a helpful AI assistant"}]
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()



if mode == "😺 Chat With AI":

    col1, col2 = st.columns([6, 2])

    with col1:
        with st.expander("📎 Upload"):
            file = st.file_uploader("Upload",type=["png", "jpg", "jpeg", "csv", "xlsx", "json", "pdf"],
                label_visibility="collapsed")

    with col2:
        if st.button("➕ New Chat"):
            st.session_state.current_chat_id = str(uuid.uuid4())
            st.session_state.chat_messages = [{"role": "system", "content": "You are a helpful AI assistant"}]
            st.rerun()

    if file:
        if file.type.endswith("csv"):
            st.dataframe(pd.read_csv(file))
        elif file.type.endswith("xlsx"):
            st.dataframe(pd.read_excel(file))
        elif file.type.endswith("json"):
            st.dataframe(pd.read_json(file))
        elif file.type.startswith("image"):
            st.image(Image.open(file), width=200)
        elif file.type.endswith("pdf"):
            st.info("PDF uploaded successfully")

    for msg in st.session_state.chat_messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Type your message")

    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})

        response = requests.post(f"{BACKEND_URL}/chat",
            data={"msg": user_input,"chat_id": st.session_state.current_chat_id},
            files={"file": file} if file else None)

        if response.status_code == 200:
            reply = response.json()["reply"]
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.error(response.text)


if mode == "📺 Image Generation":

    st.subheader("🎨 Image Generation")

    prompt = st.text_area("Describe the image",placeholder="A futuristic city at night, cyberpunk style")

    if st.button("Generate Image"):

        if not prompt.strip():
            st.warning("Please enter a prompt")
        else:
            with st.spinner("Generating image..."):
                res = requests.post(f"{BACKEND_URL}/generate-image",json={"prompt": prompt})

            if res.status_code == 200 and "image" in res.headers.get("content-type", ""):
                img = Image.open(io.BytesIO(res.content))
                st.image(img, caption="Generated Image", width=700)

                st.download_button("⬇️ Download Image",
                    data=res.content,
                    file_name="generated_image.png",
                    mime="image/png")
            else:
                st.error("Image generation failed")
                st.text(res.text)


