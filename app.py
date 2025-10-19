"""
AI Learning Assistant - Using Streamlit and Groq API
This is an intelligent learning companion that can help you answer questions, explain concepts, and provide learning advice
"""

import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
def init_groq_client():
    """Initialize Groq API client"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ Please set the GROQ_API_KEY environment variable")
        st.stop()
    return Groq(api_key=api_key)

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
        "content": "Hello! I'm your AI Learning Assistant. Whatever you want to learn or any questions you have, feel free to ask me! 💡"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Initialize client
            client = init_groq_client()

            # Prepare message history (add system prompt)
            messages = [
                {
                    "role": "system",
                    "content": "You are a friendly, patient AI learning assistant. Your task is to help students learn and understand various topics. Please explain concepts in a clear, easy-to-understand way, and provide examples when necessary. Maintain an encouraging and supportive attitude."
                }
            ]
            # Add conversation history
            messages.extend(st.session_state.messages)

            # Call Groq API (streaming output)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )

            # Display streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

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
            "content": "Hello! I'm your AI Learning Assistant. Whatever you want to learn or any questions you have, feel free to ask me! 💡"
        })
        st.rerun()

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
    st.markdown("**Model**: llama-3.3-70b-versatile")
    st.markdown("**Tech Stack**: Streamlit + Groq API")
