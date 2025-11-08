"""Main application file for the chat interface."""

import streamlit as st
import logging
import sys
import requests
import os
from pathlib import Path

# Configure Streamlit page first
st.set_page_config(
    page_title="Chat Bot UI",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Import utility functions
try:
    from utils import (
        initialize_session_state,
        add_message,
        get_chat_history,
        clear_chat_history,
    )

    logger.info("Successfully imported utils")
except Exception as e:
    logger.error(f"Error importing utils: {e}")
    raise

# Backend API URL (read from environment so one root .env can control it)
base = os.getenv("LOCAL_CHAT_API_BASE_URL", "http://localhost:8000").rstrip("/")
endpoint = os.getenv("LOCAL_CHAT_API_ENDPOINT", "/api/chat")
BACKEND_URL = f"{base}{endpoint}"


def backend_chat(prompt: str, history: list):
    """Send chat request to backend DigitalOcean-powered API."""
    try:
        payload = {"messages": history + [{"role": "user", "content": prompt}]}

        logger.info(f"Sending request to backend: {payload}")

        resp = requests.post(BACKEND_URL, json=payload, timeout=60)

        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "No response from backend.")
        else:
            logger.error(f"Backend error {resp.status_code}: {resp.text}")
            return f"Backend error: {resp.text}"

    except Exception as e:
        logger.error(f"Error contacting backend: {e}")
        return "Unable to reach backend. Please try again."


def setup_sidebar():
    """Setup the sidebar with controls."""
    with st.sidebar:
        st.title("Chat Bot Settings")

        # Always connected (we removed Azure)
        st.success("🟢 Connected to Backend API")

        st.markdown("---")

        # System Message Configuration
        st.subheader("🎯 AI Behavior")

        if "custom_system_message" not in st.session_state:
            st.session_state.custom_system_message = "You are a helpful AI assistant. Provide clear, concise, and helpful responses."

        new_system_message = st.text_area(
            "System Message:",
            value=st.session_state.custom_system_message,
            height=120,
        )

        if new_system_message != st.session_state.custom_system_message:
            st.session_state.custom_system_message = new_system_message
            st.success("✅ System message updated!")

        st.markdown("---")

        if st.button("Clear Chat"):
            clear_chat_history()

        st.markdown("---")
        st.markdown(
            """
        ### About
        This is an AI chat interface powered by:
        - DigitalOcean Inference API (via backend)
        - Streamlit
        - Python
        """
        )


def display_chat_history():
    """Display the chat history."""
    for message in get_chat_history():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input():
    """Handle user input and generate response."""
    if prompt := st.chat_input("What's on your mind?"):
        add_message("user", prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = get_chat_history()
                response = backend_chat(prompt, history)
                st.markdown(response)
                add_message("assistant", response)


def main():
    """Main application function."""
    try:
        logger.info("Starting main application")

        st.title("🤖 AI Chat Assistant")
        st.write("Initializing...")

        initialize_session_state()
        setup_sidebar()

        st.title("🤖 AI Chat Assistant")
        st.markdown("*Powered by DigitalOcean (via backend)*")
        st.markdown("---")

        display_chat_history()
        handle_user_input()

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        st.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        logger.info("Starting app")
        main()
    except Exception as e:
        logger.error(f"Application failed: {e}")
        st.error("Failed to start the application. Check logs.")
