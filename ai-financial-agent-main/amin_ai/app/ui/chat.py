"""Chat logic and streaming."""

import asyncio
import time
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from app.workflow import get_chatbot
from app.monitoring import get_logger, RequestTimer
from app.cache import ResponseCache
from app.security import SecurityPipeline


logger = get_logger("streamlit-ui")


async def stream_chatbot_response(
    user_message: HumanMessage,
    thread_id: str,
):
    """
    Stream events from LangGraph chatbot.
    
    Yields:
        str: Text chunks from the LLM response.
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "askx_streamlit_chat",
    }
    
    status_holder = {"box": None}
    
    async with get_chatbot() as chatbot:
        async for event in chatbot.astream_events(
            {"messages": [user_message]},
            config=config,
            version="v2",
        ):
            event_type = event.get("event")
            event_name = event.get("name", "")
            data = event.get("data", {})
            
            # Tool start
            if event_type == "on_tool_start":
                tool_name = event_name or "tool"
                
                if status_holder["box"] is None:
                    status_holder["box"] = st.status(
                        f"🔧 Using `{tool_name}`...",
                        expanded=True,
                    )
                else:
                    status_holder["box"].update(
                        label=f"🔧 Using `{tool_name}`...",
                        state="running",
                        expanded=True,
                    )
            
            # Tool end
            elif event_type == "on_tool_end":
                if status_holder["box"] is not None:
                    status_holder["box"].update(
                        label="✅ Tool finished",
                        state="complete",
                        expanded=False,
                    )
            
            # Model stream
            elif event_type == "on_chat_model_stream":
                chunk = data.get("chunk")
                
                if chunk is None:
                    continue
                
                content = getattr(chunk, "content", "")
                
                # String content
                if isinstance(content, str) and content:
                    yield content
                
                # Content blocks
                elif isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        
                        block_type = block.get("type")
                        
                        if block_type == "text":
                            text = block.get("text", "")
                            if text:
                                yield text
    
    # Close tool status
    if status_holder["box"] is not None:
        status_holder["box"].update(
            label="✅ Completed",
            state="complete",
            expanded=False,
        )


def handle_chat_message(
    prompt: str,
    uploaded_files: list,
    security: SecurityPipeline,
    cache: ResponseCache,
    metrics,
):
    """
    Process user message and generate response.
    
    Returns:
        tuple: (response_text, model_used, cache_hit)
    """
    
    # Rate limiting
    now = time.monotonic()
    if now - st.session_state.last_request_at < 1:
        st.warning(
            "Please wait a moment before "
            "sending another message."
        )
        st.stop()
    
    st.session_state.last_request_at = now
    
    # Security check
    is_allowed, cleaned_message, security_notes = security.check_input(prompt)
    
    if not is_allowed:
        metrics.record_request(latency_ms=0, error=True)
        logger.warning("UI request blocked by security")
        st.error(
            "Your message was blocked "
            "by our security filters."
        )
        st.stop()
    
    # Add to session
    user_message = HumanMessage(content=cleaned_message)
    st.session_state.messages.append(user_message)
    
    # Display user message
    from app.ui.messages import render_user_message
    render_user_message(cleaned_message, uploaded_files if uploaded_files else None)
    
    # Generate response
    with st.chat_message("assistant", avatar="✨"):
        status_holder = {"box": None}
        response_text = ""
        model_used = "cache"
        
        with RequestTimer() as timer:
            # Check cache
            cached_response = cache.get(cleaned_message)
            
            if cached_response is not None:
                # Cache hit
                response_text = st.write_stream(
                    (char for char in cached_response)
                )
            else:
                # Cache miss - stream from LangGraph
                model_used = "stream"
                
                response_text = st.write_stream(
                    stream_chatbot_response(
                        user_message,
                        st.session_state.thread_id,
                    )
                )
                
                # Save to cache
                if response_text:
                    cache.set(cleaned_message, response_text)
            
            # Security output check
            response_text, output_warnings = security.check_output(response_text)
            security_notes.extend(output_warnings)
        
        # Record metrics
        metrics.record_request(
            latency_ms=timer.elapsed_ms,
            input_tokens=int(len(cleaned_message.split()) * 1.3),
            output_tokens=int(len(response_text.split()) * 1.3),
            cache_hit=(cached_response is not None),
        )
        
        # Log
        logger.info(
            "UI request completed",
            extra={
                "extra_data": {
                    "thread_id": st.session_state.thread_id,
                    "model_used": model_used,
                    "cache_hit": cached_response is not None,
                    "latency_ms": round(timer.elapsed_ms, 2),
                }
            },
        )
        
        # Save assistant message
        last_message = AIMessage(content=response_text)
        st.session_state.messages.append(last_message)
        
        # Security notice
        if security_notes:
            st.caption(
                "🛡️ Security filters applied "
                "to this exchange."
            )
    
    return response_text, model_used, cached_response is not None
