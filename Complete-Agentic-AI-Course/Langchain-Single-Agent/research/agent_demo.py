import os

import certifi
import requests
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI


os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")


@tool
def get_weather_data(city: str) -> str:
    """Fetch current weather information for a city."""
    if not WEATHERSTACK_API_KEY:
        return "Missing WEATHERSTACK_API_KEY environment variable."

    url = (
        "https://api.weatherstack.com/current?"
        f"access_key={WEATHERSTACK_API_KEY}&query={city}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "current" not in data:
        return f"Could not fetch weather data for {city}"

    return (
        f"City: {city}\n"
        f"Temperature: {data['current']['temperature']}°C\n"
        f"Weather: {data['current']['weather_descriptions'][0]}\n"
        f"Humidity: {data['current']['humidity']}%"
    )


def main() -> None:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is missing. Add it to your .env file.")
    if not WEATHERSTACK_API_KEY:
        raise ValueError("WEATHERSTACK_API_KEY is missing. Add it to your .env file.")

    search_tool = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=2)

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=OPENAI_API_KEY,
    )

    prompt = hub.pull("hwchase17/react")
    tools = [search_tool, get_weather_data]

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )

    response = agent_executor.invoke({
        "input": (
            "Find the capital of India and then find its current weather."
        )
    })

    print(response["output"])


if __name__ == "__main__":
    main()
