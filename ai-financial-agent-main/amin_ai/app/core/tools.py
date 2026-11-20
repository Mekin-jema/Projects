"""Tool definitions for the chatbot agent."""

import truststore
import os
import math
import requests
from typing import Any
from langchain_core.tools import tool
from  truststore  import inject_into_ssl
inject_into_ssl()

try:
    from langchain_tavily import TavilySearch
    TAVILY_AVAILABLE = True
except ModuleNotFoundError:
    TAVILY_AVAILABLE = False

from app.rag.retriever import get_retriever


# ============================================================================
# RAG Tool
# ============================================================================

@tool
def rag_tool(query: str) -> str:
    """
    Retrieve relevant information from the PDF document.

    Use this tool when the user asks factual or conceptual questions
    that may be answered using the stored PDF documents.

    Args:
        query: The question or search query used to retrieve PDF content.
    """
    retriever = get_retriever()
    documents = retriever.invoke(query)

    if not documents:
        return "No relevant information was found in the PDF."

    formatted_documents = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page", "Unknown page")

        formatted_documents.append(
            f"Document {index}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content: {document.page_content}"
        )

    return "\n\n".join(formatted_documents)


# ============================================================================
# Web Search Tool
# ============================================================================


def _safe_tavily_search(query: str) -> str:
    """Run a Tavily search and turn API errors into a user-safe string."""
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return (
            "Web search is unavailable because the TAVILY_API_KEY environment "
            "variable is missing."
        )

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)
        result = client.search(
            query,
            max_results=5,
            topic="general",
            search_depth="advanced",
        )
        return str(result)

    except Exception as error:
        error_name = type(error).__name__
        message = str(error).lower()

        if "forbidden" in message or "403" in message or "unauthorized" in message:
            return (
                "Web search is blocked or the Tavily API key is invalid. "
                "Please check the TAVILY_API_KEY configuration."
            )

        if "api key" in message or "key" in message:
            return "Web search failed because the Tavily API key is invalid or missing."

        return f"Web search failed with {error_name}: {error}"


if TAVILY_AVAILABLE:
    @tool
    def search_tool(query: str) -> str:
        """Search the web for current or time-sensitive information."""
        try:
            return str(TavilySearch(
                max_results=5,
                topic="general",
                search_depth="advanced"
            ).invoke({"query": query}))
        except Exception as error:
            return _safe_tavily_search(query)
else:
    @tool
    def search_tool(query: str) -> str:
        """Search the web for current or otherwise time-sensitive information."""
        return _safe_tavily_search(query)


# ============================================================================
# Calculator Tool
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10 * 5
    """
    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"


# ============================================================================
# Stock Price Tool
# ============================================================================

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=9MZO2JUBR7IFNTOI"
    r = requests.get(url)
    return r.json()


# ============================================================================
# Weather Tool
# ============================================================================

@tool
def get_current_weather(location: str) -> str:
    """
    Get the current real-time weather for a given city or location.

    Args:
        location: City or location name, for example:
                  "Dhaka", "London, UK", or "New York, US".

    Returns:
        A formatted current weather report.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return (
            "Weather API key is missing. "
            "Set the OPENWEATHER_API_KEY environment variable."
        )

    try:
        # Step 1: Convert the location name into latitude and longitude
        geocoding_url = "https://api.openweathermap.org/geo/1.0/direct"

        geocoding_params = {
            "q": location,
            "limit": 1,
            "appid": api_key,
        }

        geo_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10,
        )
        geo_response.raise_for_status()

        locations: list[dict[str, Any]] = geo_response.json()

        if not locations:
            return f"Could not find the location: {location}"

        latitude = locations[0]["lat"]
        longitude = locations[0]["lon"]
        resolved_name = locations[0].get("name", location)
        country = locations[0].get("country", "")
        state = locations[0].get("state", "")

        # Step 2: Get current weather using latitude and longitude
        weather_url = "https://api.openweathermap.org/data/2.5/weather"

        weather_params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )
        weather_response.raise_for_status()

        weather_data = weather_response.json()

        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        description = weather_data["weather"][0]["description"]
        wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
        visibility_meters = weather_data.get("visibility")

        visibility_km = (
            round(visibility_meters / 1000, 1)
            if visibility_meters is not None
            else "N/A"
        )

        location_parts = [resolved_name]

        if state:
            location_parts.append(state)

        if country:
            location_parts.append(country)

        display_location = ", ".join(location_parts)

        return (
            f"Current weather in {display_location}:\n"
            f"- Condition: {description.title()}\n"
            f"- Temperature: {temperature}°C\n"
            f"- Feels like: {feels_like}°C\n"
            f"- Humidity: {humidity}%\n"
            f"- Pressure: {pressure} hPa\n"
            f"- Wind speed: {wind_speed} m/s\n"
            f"- Visibility: {visibility_km} km"
        )

    except requests.Timeout:
        return "The weather service request timed out. Please try again."

    except requests.HTTPError as error:
        status_code = error.response.status_code if error.response else "unknown"

        if status_code == 401:
            return "The OpenWeather API key is invalid or inactive."

        return f"Weather API returned an HTTP error: {status_code}"

    except requests.RequestException as error:
        return f"Could not connect to the weather service: {error}"

    except (KeyError, TypeError, ValueError) as error:
        return f"Unexpected weather API response: {error}"


# ============================================================================
# Tool List
# ============================================================================

tools = [search_tool, calculator, get_stock_price, get_current_weather, rag_tool]
