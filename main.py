import os
import certifi
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langsmith import Client
from langchain.agents import create_agent
import requests
from langchain.tools import tool


#===========================
#LOAD ENVIRONMENT VARIABLES
#===========================
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")

search_tool = TavilySearchResults(max_results=3)
response =search_tool.invoke("what is the AI new model released by OpenAI in 2026?")


@tool
def get_weather_data(city: str) -> str:
    """
    Fetches weather data for a given city using the Weatherstack API.

    Args:
        city (str): The name of the city to fetch weather data for.

    Returns:
        str: The weather data for the specified city.
    """
    # Implementation for fetching weather data
    url = f"http://api.weatherstack.com/current?access_key={WEATHERSTACK_API_KEY}&query={city}"
    response = requests.get(url)
    data = response.json()
    if "current" not in data:
        return "Weather data not available."

    return (
         f"City: {city}\n"
         f"Temperature: {data['current']['temperature']}°C\n"
         f"Weather: {data['current']['weather_descriptions'][0]}\n"
         f"Humidity: {data['current']['humidity']}%"
    )

##============================
##LLM
#===========================
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0,
    api_key=OPENAI_API_KEY
    )
response = llm.invoke("Tell me a joke about AI")


#prompt
client = Client()
prompt = client.pull_prompt("hwchase17/react",dangerously_pull_public_prompt=True)

#============================
#Tools
#===========================
tools = [search_tool, get_weather_data]


#============================
# CREATE AGENT
#===========================
agent = create_agent(
    model=llm,
    tools=tools

  )

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Find the capital of Texas and then find its current weather."
            }
        ]
    }
)


print("\n========================")
print("FINAL OUTPUT")
print("========================\n")
print(result["messages"][-1].content)
