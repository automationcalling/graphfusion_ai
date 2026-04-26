"""
Streamlit UI for GraphFusion_AI Chat Interface with LLM Integration.

To run:
  streamlit run src/ui/app.py

Environment variables required:
  - API_URL: URL of GraphFusion API (default: http://localhost:8000)
  - AZURE_OPENAI_API_KEY: Azure OpenAI API key
  - AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint
"""

from __future__ import annotations

import streamlit as st
import requests
import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")


def fetch_response(query: str) -> dict[str, Any] | None:
    """
    Fetch response from GraphFusion API.
    
    Args:
        query: User query
    
    Returns:
        Response dict with answer, sources, and reasoning_type, or None if error
    """
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"query": query},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to API at {API_URL}")
        return None
    except Exception as e:
        st.error(f"Error fetching response: {str(e)}")
        return None


def format_sources(sources: list[dict[str, Any]]) -> str:
    """Format sources for display."""
    if not sources:
        return "No sources found"
    
    formatted = []
    for source in sources:
        source_id = source.get("id", "Unknown")
        score = source.get("score", 0)
        formatted.append(f"- {source_id} (confidence: {score:.2%})")
    
    return "\n".join(formatted)


def get_reasoning_emoji(reasoning_type: str) -> str:
    """Get emoji for reasoning type."""
    emoji_map = {
        "semantic": "🔍",
        "relationship": "🔗",
        "hybrid": "⚡",
        "error": "❌",
    }
    return emoji_map.get(reasoning_type.lower(), "❓")


def main():
    st.set_page_config(page_title="GraphFusion_AI", layout="wide", initial_sidebar_state="expanded")
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.write(f"**API URL**: {API_URL}")

        # Test API connection
        if st.button("Test API Connection"):
            try:
                response = requests.get(f"{API_URL}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API is healthy")
                    data = response.json()
                    if data.get("llm") == "healthy":
                        st.success("✅ LLM integration active")
                    else:
                        st.warning("⚠️ LLM not available")
                else:
                    st.error("❌ API error")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

        st.markdown("---")

        # Document Upload Section
        st.subheader("📤 Upload Document")
        st.markdown("Ingest documents into the knowledge base")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "docx", "doc", "pptx", "ppt", "xlsx", "xls"],
            help="Supported formats: PDF, Word, PowerPoint, Excel, Text",
        )

        if st.button("📥 Ingest Document", disabled=uploaded_file is None):
            if uploaded_file is not None:
                with st.spinner("🔄 Ingesting document..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        response = requests.post(f"{API_URL}/upload", files=files, timeout=300)

                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Ingestion successful!")
                            st.json({
                                "Filename": result.get("filename"),
                                "Format": result.get("format"),
                                "Chunks": result.get("chunk_count"),
                                "Entities": result.get("entity_count"),
                                "Relationships": result.get("relationship_count"),
                            })
                            logger.info(f"UI ingestion result: {result}")
                        else:
                            error_detail = response.json().get("detail", "Unknown error")
                            st.error(f"❌ Ingestion failed: {error_detail}")
                    except requests.exceptions.ConnectionError:
                        st.error(f"Cannot connect to API at {API_URL}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        st.markdown("---")
        st.markdown("""
        ### About GraphFusion_AI
        A hybrid retrieval system combining:
        - **Vector Retrieval** 🔍: Semantic search
        - **Graph Retrieval** 🔗: Relationship reasoning
        - **Hybrid Retrieval** ⚡: Fused context
        """)
    
    # Main content
    st.title("🚀 GraphFusion_AI Chat Interface")
    
    st.markdown("""
    Ask questions and get AI-generated answers powered by:
    - Azure OpenAI LLM for answer generation
    - Intent detection for intelligent routing
    - Hybrid retrieval combining semantic and relationship context
    """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(content)
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    if isinstance(content, dict):
                        # LLM-generated response
                        answer = content.get("answer", "No answer available")
                        reasoning_type = content.get("reasoning_type", "unknown")
                        sources = content.get("sources", [])
                        
                        # Display answer
                        st.markdown(f"**Answer:**\n\n{answer}")
                        
                        # Display reasoning type with emoji
                        emoji = get_reasoning_emoji(reasoning_type)
                        st.markdown(f"\n**Reasoning Type**: {emoji} {reasoning_type.capitalize()}")
                        
                        # Display sources
                        if sources:
                            with st.expander("📚 View Sources", expanded=False):
                                st.markdown(format_sources(sources))
                    else:
                        st.write(content)
    
    # Chat input
    st.markdown("---")
    user_input = st.chat_input("💬 Ask me anything...", key="user_input")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        # Fetch response from API
        with st.spinner("🤔 Thinking..."):
            response = fetch_response(user_input)
        
        if response:
            # Add assistant message to history
            assistant_content = {
                "answer": response.get("answer", "No answer available"),
                "reasoning_type": response.get("reasoning_type", "unknown"),
                "sources": response.get("sources", []),
            }
            st.session_state.messages.append({"role": "assistant", "content": assistant_content})
            
            # Display assistant response
            with st.chat_message("assistant", avatar="🤖"):
                # Display answer
                st.markdown(f"**Answer:**\n\n{assistant_content['answer']}")
                
                # Display reasoning type
                emoji = get_reasoning_emoji(assistant_content["reasoning_type"])
                st.markdown(f"\n**Reasoning Type**: {emoji} {assistant_content['reasoning_type'].capitalize()}")
                
                # Display sources
                if assistant_content["sources"]:
                    with st.expander("📚 View Sources", expanded=False):
                        st.markdown(format_sources(assistant_content["sources"]))
        else:
            st.error("Failed to get response from API")


if __name__ == "__main__":
    main()
