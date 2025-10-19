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
        "content": "Hello! I'm Edward, your AI Learning Assistant. What's your name? I'd love to get to know you and help you with whatever you want to learn! 💡"
    })

if "user_name" not in st.session_state:
    st.session_state.user_name = None

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
            user_name_context = f" The user's name is {st.session_state.user_name}." if st.session_state.user_name else " If the user hasn't introduced themselves yet, ask for their name in a friendly way."
            messages = [
                {
                    "role": "system",
                    "content": f"You are Edward, a friendly and patient AI learning assistant. You use he/him pronouns. Your task is to help students learn and understand various topics. Please explain concepts in a clear, easy-to-understand way, and provide examples when necessary. Maintain an encouraging and supportive attitude.{user_name_context} When the user tells you their name, remember it and use it occasionally in conversation to make the interaction more personal."
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
    st.markdown("**Model**: llama-3.3-70b-versatile")
    st.markdown("**Tech Stack**: Streamlit + Groq API")
