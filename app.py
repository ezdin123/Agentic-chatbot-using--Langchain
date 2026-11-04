import os

import certifi
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI


# ==========================================
# STREAMLIT PAGE CONFIG (must be first st call)
# ==========================================
st.set_page_config(page_title="Agentic AI Assistant", page_icon="🤖", layout="centered")

# ==========================================
# LOAD ENV VARIABLES
# ==========================================
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

st.title("🤖 Agentic AI Assistant")
st.markdown("Search + Weather AI Agent using LangChain")

missing = [
    k for k, v in {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "TAVILY_API_KEY": TAVILY_API_KEY,
        "WEATHERSTACK_API_KEY": WEATHERSTACK_API_KEY,
    }.items() if not v
]
if missing:
    st.error("Missing in .env: " + ", ".join(missing))
    st.stop()


# ==========================================
# WEATHER TOOL
# ==========================================
@tool
def get_weather_data(city: str) -> str:
    """Fetch current weather information for a city."""
    try:
        resp = requests.get(
            "http://api.weatherstack.com/current",
            params={"access_key": WEATHERSTACK_API_KEY, "query": city},
            timeout=10,
        )
        data = resp.json()
    except requests.RequestException as e:
        return f"Weather service error: {e}"

    if "current" not in data:
        return f"Could not fetch weather data for {city}"

    cur = data["current"]
    return (
        f"City: {city}\n"
        f"Temperature: {cur['temperature']}°C\n"
        f"Weather: {cur['weather_descriptions'][0]}\n"
        f"Humidity: {cur['humidity']}%"
    )


# ==========================================
# LLM + TOOLS + AGENT (built once, cached across reruns)
# ==========================================
@st.cache_resource(show_spinner="Starting agent...")
def build_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    tools = [TavilySearchResults(max_results=2), get_weather_data]
    return create_agent(model=llm, tools=tools)


agent = build_agent()

# ==========================================
# UI INPUT
# ==========================================
user_query = st.text_input(
    "Enter your query:",
    placeholder="Example: Find the capital of Texas and then find its current weather.",
)

# ==========================================
# RUN AGENT
# ==========================================
if st.button("Run Agent"):

    if user_query:

        with st.spinner("Agent is thinking..."):

            try:
                response = agent.invoke(
                    {"messages": [{"role": "user", "content": user_query}]}
                )

                st.success("Response Generated")

                st.markdown("## Final Response")
                st.write(response["messages"][-1].content)

            except Exception as e:
                st.error(f"Error: {str(e)}")

    else:
        st.warning("Please enter a query")