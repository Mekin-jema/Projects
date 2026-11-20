"""
Production-Ready FastAPI + LangGraph Application

Wires together:
- Security pipeline (input sanitization, PII masking)
- Response caching
- Rate limiting (slowapi)
- LangGraph agent (with retries + fallback)
- Structured logging + metrics
- LangSmith tracing
- Health checks
"""


import truststore

# Must be called before making HTTPS requests
truststore.inject_into_ssl()
from contextlib import asynccontextmanager
import asyncio
import json

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from app.config import get_settings
from app.models import (
    ChatRequest, ChatResponse,
    HealthResponse, MetricsResponse, ErrorResponse,
    StreamingSSEEvent,
)
from app.security import SecurityPipeline
from app.cache import ResponseCache
from app.monitoring import get_logger, MetricsCollector, RequestTimer
from app.agent import ProductionAgent
from app.workflow import get_chatbot

load_dotenv()



# === Global instances (initialized in lifespan) ===
security: SecurityPipeline = None
cache: ResponseCache = None
metrics: MetricsCollector = None
agent: ProductionAgent = None
logger = get_logger()


# === Lifespan (startup/shutdown) ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize all components on startup, clean up on shutdown.
    This is the modern FastAPI pattern (replaces @app.on_event).
    """
    global security, cache, metrics, agent

    settings = get_settings()

    logger.info("Starting production API...", extra={"extra_data": {
        "environment": settings.app_env,
        "primary_model": settings.primary_model,
        # "tracing_enabled": settings.langsmith_tracing_v2,
    }})

    # Initialize components
    security = SecurityPipeline()
    cache = ResponseCache(ttl_seconds=settings.cache_ttl_seconds)
    metrics = MetricsCollector()
    agent = ProductionAgent()

    logger.info("All components initialized. Ready to serve requests.")

    yield  # App is running

    # Shutdown
    logger.info("Shutting down...", extra={"extra_data": metrics.summary})
    
    
    # === Rate Limiter Setup ===
limiter = Limiter(key_func=get_remote_address)

# === FastAPI App ===
app = FastAPI(
    title="Production LangGraph API",
    description="A production-ready chat API with security, caching, and observability.",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter


# === Exception Handlers ===

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning("Rate limit exceeded", extra={"extra_data": {
        "client_ip": get_remote_address(request),
    }})
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please slow down.",
        },
    )

# =============================================
# ENDPOINTS
# =============================================

@app.post("/chat", response_model=ChatResponse)
@limiter.limit(get_settings().rate_limit)
# @traceable(name="chat_endpoint")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint.

    Flow:
    1. Security check (injection + PII masking)
    2. Cache lookup
    3. LangGraph agent invoke (if cache miss)
    4. Output validation
    5. Cache store
    6. Return response
    """

#     '''
#     class RequestTimer:
#     def __enter__(self):
#         print("Timer started")
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         print("Timer stopped")

 
#   '''
#    with RequestTimer() as timer:
#     print("Processing request...")
#    '''
    #              User Request
    #                   |
    #                   v
    #           RequestTimer START
    #                   |
    #                   v
    #           Security Check
    #                   |
    #       +-----------+-----------+
    #       |                       |
    #    Blocked                Allowed
    #       |                       |
    #    Return               Cache Lookup
    #                               |
    #                  +------------+------------+
    #                  |                         |
    #               Cache Hit               Cache Miss
    #                  |                         |
    #              Return              LangGraph Agent
    #                                          |
    #                                          v
    #                                   LLM + Retrieval
    #                                          |
    #                                          v
    #                                 Output Validation
    #                                          |
    #                                          v
    #                                    Save Cache
    #                                          |
    #                                          v
    #                               RequestTimer END

    with RequestTimer() as timer:
        security_notes = []

        # ---- Step 1: Security Check ----
        is_allowed, cleaned_message, notes = security.check_input(body.message)
        security_notes.extend(notes)

        if not is_allowed:
            logger.warning("Request blocked by security", extra={"extra_data": {
                "reason": notes,
                "thread_id": body.thread_id,
            }})
            metrics.record_request(latency_ms=0, error=True)
            raise HTTPException(
                status_code=400,
                detail="Your message was blocked by our security filters."
            )

        # ---- Step 2: Cache Lookup ----
        cached_response = cache.get(cleaned_message) # what is the clean messsage looks like 
        if cached_response is not None:
            metrics.record_request(latency_ms=0, cache_hit=True)
            logger.info("Cache hit", extra={"extra_data": {
                "thread_id": body.thread_id,
            }})
            return ChatResponse(
                response=cached_response,
                thread_id=body.thread_id,
                model_used="cache",
                cached=True,
                processing_time_ms=0,
            )

        # ---- Step 3: Invoke LangGraph Agent ----
        try:
            result = agent.invoke(cleaned_message, thread_id=body.thread_id)
        except Exception as e:
            logger.error(f"Agent invocation failed: {e}", extra={"extra_data": {
                "thread_id": body.thread_id,
                "error": str(e),
            }})
            metrics.record_request(latency_ms=0, error=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your request."
            )

        response_text = result["response"]
        model_used = result["model_used"]

        # ---- Step 4: Output Validation ----
        validated_response, output_warnings = security.check_output(response_text)
        security_notes.extend(output_warnings)

        # ---- Step 5: Cache Store ----
        cache.set(cleaned_message, validated_response)

    # ---- Step 6: Log & Record Metrics ----
    input_tokens = int(len(cleaned_message.split()) * 1.3)
    output_tokens = int(len(validated_response.split()) * 1.3)

    metrics.record_request(
        latency_ms=timer.elapsed_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_hit=False,
    )

    if security_notes:
        logger.info("Security notes", extra={"extra_data": {
            "notes": security_notes,
            "thread_id": body.thread_id,
        }})

    logger.info("Request completed", extra={"extra_data": {
        "thread_id": body.thread_id,
        "model_used": model_used,
        "latency_ms": round(timer.elapsed_ms, 2),
    }})

    return ChatResponse(
        response=validated_response,
        thread_id=body.thread_id,
        model_used=model_used,
        cached=False,
        processing_time_ms=round(timer.elapsed_ms, 2),
        security_notes=security_notes,
    )


@app.post("/chat/stream")
@limiter.limit(get_settings().rate_limit)
async def chat_stream(request: Request, body: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    
    Streams the LangGraph agent response with text deltas and tool calls
    in SSE format for real-time client updates.
    """
    
    security_notes = []

    # ---- Step 1: Security Check ----
    is_allowed, cleaned_message, notes = security.check_input(body.message)
    security_notes.extend(notes)

    if not is_allowed:
        logger.warning("Request blocked by security (stream)", extra={"extra_data": {
            "reason": notes,
            "thread_id": body.thread_id,
        }})
        metrics.record_request(latency_ms=0, error=True)
        raise HTTPException(
            status_code=400,
            detail="Your message was blocked by our security filters."
        )

    # ---- Step 2: Check cache ----
    cached_response = cache.get(cleaned_message)
    if cached_response is not None:
        async def cached_generator():
            yield f"data: {json.dumps({'type': 'message-start', 'content': {'role': 'assistant'}})}\n\n"
            yield f"data: {json.dumps({'type': 'text-delta', 'content': cached_response})}\n\n"
            yield f"data: {json.dumps({'type': 'message-end', 'content': {}})}\n\n"

        return StreamingResponse(
            cached_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    async def stream_generator():
        """Generate SSE events from the LangGraph agent stream."""
        
        try:
            # Get the compiled chatbot graph
            async with get_chatbot() as chatbot:
                
                # Stream events from the agent
                message_content = []
                
                async for event in chatbot.astream_events(
                    {"messages": [{"type": "human", "content": cleaned_message}]},
                    config={"configurable": {"thread_id": body.thread_id}},
                    version="v2"
                ):
                    # Extract event type and data
                    event_type = event.get("event", "")
                    
                    # Text streaming from the LLM
                    if event_type == "on_chat_model_stream":
                        chunk = event.get("data", {}).get("chunk", {})
                        if chunk and hasattr(chunk, "content") and chunk.content:
                            message_content.append(chunk.content)
                            yield f"data: {json.dumps({'type': 'text-delta', 'content': chunk.content})}\n\n"
                    
                    # Tool calls
                    elif event_type == "on_tool_start":
                        metadata = event.get("data", {}).get("metadata", {})
                        tool_input = event.get("data", {}).get("input", {})
                        yield f"data: {json.dumps({
                            'type': 'tool-call',
                            'tool_name': metadata.get("name", "unknown"),
                            'tool_input': tool_input
                        })}\n\n"
                    
                    # Tool results
                    elif event_type == "on_tool_end":
                        metadata = event.get("data", {}).get("metadata", {})
                        result = event.get("data", {}).get("output", "")
                        yield f"data: {json.dumps({
                            'type': 'tool-result',
                            'tool_name': metadata.get("name", "unknown"),
                            'tool_result': str(result)
                        })}\n\n"
                
                # Send completion event
                yield f"data: {json.dumps({'type': 'message-end', 'content': {}})}\n\n"
                
                # Cache the response
                full_response = "".join(message_content)
                if full_response:
                    cache.set(cleaned_message, full_response)
                    
        except Exception as e:
            logger.error(f"Stream generation failed: {e}", extra={"extra_data": {
                "thread_id": body.thread_id,
                "error": str(e),
            }})
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


    
    
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check for Docker/Kubernetes."""
    settings = get_settings()

    checks = {
        "agent": agent is not None,
        "security": security is not None,
        "cache": cache is not None,
    }

    all_healthy = all(checks.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        environment=settings.app_env,
        checks=checks,
    )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Metrics for monitoring dashboards."""
    summary = metrics.summary
    return MetricsResponse(**summary)


@app.get("/cache/stats")
async def cache_stats():
    """Cache performance statistics."""
    return cache.stats