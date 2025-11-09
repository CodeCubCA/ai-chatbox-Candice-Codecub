"""
AI Learning Assistant - Using Streamlit and Google Gemini API
This is an intelligent learning companion that can help you answer questions, explain concepts, and provide learning advice
"""

import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import base64
from io import BytesIO
import PyPDF2
from streamlit_paste_button import paste_image_button

# Load environment variables
load_dotenv()

# Initialize Gemini client
def init_gemini_client():
    """Initialize Google Gemini API client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ Please set the GEMINI_API_KEY environment variable")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.5-flash')

# Page configuration
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 AI Learning Assistant")
st.markdown("Hello! I'm your intelligent learning companion, here to help you answer questions, explain concepts, and provide learning advice.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm Edward, your AI Learning Assistant. What's your name? I'd love to get to know you and help you with whatever you want to learn! 💡"
    })

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "pasted_image" not in st.session_state:
    st.session_state.pasted_image = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display attached files if any
        if "files" in message:
            for file_info in message["files"]:
                if file_info["type"] == "image":
                    st.image(file_info["data"], caption=file_info["name"], use_container_width=True)
                elif file_info["type"] == "text":
                    with st.expander(f"📄 {file_info['name']}"):
                        st.text(file_info["content"][:1000] + ("..." if len(file_info["content"]) > 1000 else ""))

# File upload area (above chat input)
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("📎 Upload a file (image, PDF, or text)", type=["png", "jpg", "jpeg", "gif", "pdf", "txt", "py", "js", "html", "css", "json"], key="file_uploader")
with col2:
    paste_result = paste_image_button(
        label="📋 Paste Image (Ctrl+V)",
        background_color="#FF4B4B",
        hover_background_color="#FF6B6B",
        errors="ignore"
    )

# Handle pasted image
if paste_result.image_data is not None:
    st.session_state.pasted_image = Image.open(BytesIO(paste_result.image_data))
    st.success("✅ Image pasted! Now ask your question below.")

# Display pasted image preview
if st.session_state.pasted_image is not None:
    st.image(st.session_state.pasted_image, caption="Pasted Image Preview", width=300)

# User input
if prompt := st.chat_input("Enter your question..."):
    # Process uploaded file if any
    user_message = {"role": "user", "content": prompt}
    file_context = ""

    # Check for pasted image first
    if st.session_state.pasted_image is not None:
        file_info = []
        file_info.append({
            "type": "image",
            "name": "pasted_image.png",
            "data": st.session_state.pasted_image
        })
        file_context = f"\n\n[User pasted an image from clipboard. Please acknowledge that you can see the image and describe what you observe, or answer any questions about it.]"
        user_message["files"] = file_info
        # Clear pasted image after use
        st.session_state.pasted_image = None
    elif uploaded_file is not None:
        file_info = []
        file_type = uploaded_file.type

        # Handle image files
        if file_type.startswith("image/"):
            image = Image.open(uploaded_file)
            file_info.append({
                "type": "image",
                "name": uploaded_file.name,
                "data": image
            })
            file_context = f"\n\n[User uploaded an image: {uploaded_file.name}. Please acknowledge that you can see the image and describe what you observe, or answer any questions about it.]"

        # Handle PDF files
        elif file_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            file_info.append({
                "type": "text",
                "name": uploaded_file.name,
                "content": pdf_text
            })
            file_context = f"\n\n[User uploaded a PDF: {uploaded_file.name}]\nContent:\n{pdf_text[:2000]}{'...' if len(pdf_text) > 2000 else ''}"

        # Handle text files
        elif file_type.startswith("text/") or uploaded_file.name.endswith(('.py', '.js', '.html', '.css', '.json', '.txt')):
            text_content = uploaded_file.read().decode("utf-8")
            file_info.append({
                "type": "text",
                "name": uploaded_file.name,
                "content": text_content
            })
            file_context = f"\n\n[User uploaded a file: {uploaded_file.name}]\nContent:\n{text_content[:2000]}{'...' if len(text_content) > 2000 else ''}"

        if file_info:
            user_message["files"] = file_info

    # Add user message to chat history
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)
        if "files" in user_message:
            for file_info in user_message["files"]:
                if file_info["type"] == "image":
                    st.image(file_info["data"], caption=file_info["name"], use_container_width=True)
                elif file_info["type"] == "text":
                    with st.expander(f"📄 {file_info['name']}"):
                        st.text(file_info["content"][:1000] + ("..." if len(file_info["content"]) > 1000 else ""))

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Initialize client
            model = init_gemini_client()

            # Prepare message history (add system prompt)
            user_name_context = f" The user's name is {st.session_state.user_name}." if st.session_state.user_name else " If the user hasn't introduced themselves yet, ask for their name in a friendly way."
            system_prompt = f"You are Edward, a friendly and patient AI learning assistant. You use he/him pronouns. Your task is to help students learn and understand various topics. Please explain concepts in a clear, easy-to-understand way, and provide examples when necessary. Maintain an encouraging and supportive attitude.{user_name_context} When the user tells you their name, remember it and use it occasionally in conversation to make the interaction more personal. When users upload files (images, PDFs, code, etc.), acknowledge that you've received them and provide helpful analysis, explanations, or answers about the content."

            # Build conversation history for Gemini
            chat_history = []
            for msg in st.session_state.messages[:-1]:  # Exclude the last message (current user input)
                msg_content = msg["content"]
                # Add file context for messages with files
                if msg["role"] == "user" and "files" in msg:
                    for file_info in msg["files"]:
                        if file_info["type"] == "image":
                            msg_content += f"\n\n[User uploaded an image: {file_info['name']}. Note: You cannot actually see images, but you should acknowledge the upload and ask the user to describe it or tell you what they need help with regarding the image.]"
                        elif file_info["type"] == "text":
                            msg_content += f"\n\n[User uploaded file: {file_info['name']}]\nContent:\n{file_info['content'][:2000]}{'...' if len(file_info['content']) > 2000 else ''}"

                chat_history.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [msg_content]
                })

            # Start chat with history
            chat = model.start_chat(history=chat_history)

            # Prepare current user message with system prompt
            current_message = system_prompt + "\n\n" + prompt + file_context

            # Call Gemini API (streaming output)
            response = chat.send_message(current_message, stream=True)

            # Display streaming response
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # Try to extract user's name if they mentioned it
            if not st.session_state.user_name and prompt:
                # Simple name detection patterns
                name_patterns = ["my name is", "i'm", "i am", "call me", "this is"]
                prompt_lower = prompt.lower()
                for pattern in name_patterns:
                    if pattern in prompt_lower:
                        # Extract potential name (simple approach)
                        parts = prompt_lower.split(pattern)
                        if len(parts) > 1:
                            potential_name = parts[1].strip().split()[0] if parts[1].strip() else None
                            if potential_name and len(potential_name) > 1:
                                st.session_state.user_name = potential_name.capitalize()
                                break

        except Exception as e:
            full_response = f"Sorry, an error occurred: {str(e)}"
            message_placeholder.markdown(full_response)

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm Edward, your AI Learning Assistant. What's your name? I'd love to get to know you and help you with whatever you want to learn! 💡"
        })
        st.session_state.user_name = None
        st.rerun()

    # Display user name if known
    if st.session_state.user_name:
        st.markdown(f"### 👤 User: {st.session_state.user_name}")

    st.markdown("---")
    st.markdown("### 💡 Usage Tips")
    st.markdown("""
    - Ask me any learning-related questions
    - Ask me to explain complex concepts
    - Let me help you review knowledge points
    - Seek learning method suggestions
    - Ask me to create quizzes to test your understanding
    """)

    st.markdown("---")
    st.markdown("### 📊 Conversation Stats")
    st.markdown(f"Message count: {len(st.session_state.messages)}")

    st.markdown("---")
    st.markdown("### 🤖 About Edward")
    st.markdown("**Name**: Edward (he/him)")
    st.markdown("**Model**: Google Gemini 2.5 Flash")
    st.markdown("**Tech Stack**: Streamlit + Google Gemini API")
