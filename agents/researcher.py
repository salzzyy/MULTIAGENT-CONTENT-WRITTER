import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools.tavily_search.tool import TavilySearchResults

load_dotenv()

# Set up the LLM
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.7,
    groq_api_key=os.getenv('GROQ_API_KEY')
)

# Set up Tavily search tool
search_tool = TavilySearchResults()
tools = [
    Tool(
        name="Search",
        func=search_tool.run,
        description="Useful for answering questions by searching the web"
    )
]

# Initialize the researcher agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def read_topic_from_json(filepath: str) -> str:
    if not os.path.exists(filepath):
        print(f" {filepath} not found. Please generate idea first.")
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"JSON loaded: {data}")  # DEBUG LINE
        topic_ideas = data.get("topic_ideas", [])
        if len(topic_ideas) > 1:  # Ensuring there's more than 1 idea
            topic = topic_ideas[1].split(". ", 1)[-1].strip()  # Option 2 as you wanted
            print(f"Selected topic: {topic}")  # DEBUG LINE
            return topic
        else:
            print("No valid ideas found in JSON.")
            return ""

def research_topic(topic: str) -> str:
    query = f"Do detailed research on the topic: '{topic}'. Summarize recent and relevant info in bullet points."
    try:
        response = agent.run(query)  # Using run() instead of invoke() to ensure proper output
        print(f"Research result:\n{response}")  # DEBUG LINE
        return response
    except Exception as e:
        print(f"Error researching topic: {e}")
        return ""

def save_summary_to_json(summary: str, topic: str, filepath: str = "research_summary.json"):
    summary_data = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "summary": summary.strip()
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)
    print(f"\nResearch summary saved to {filepath}")

if __name__ == "__main__":
    topic = read_topic_from_json("idea_generated.json")
    if topic:
        print(f"Researching topic: {topic}")
        result = research_topic(topic)
        save_summary_to_json(result, topic)
    else:
        print("⚠️ No topic found.")
