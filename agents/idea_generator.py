import os
import json
from typing import List
from dotenv import load_dotenv
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Set up the Groq-powered LLM
llm = ChatGroq(
    model="llama3-70b-8192",  # or "mixtral-8x7b-32768"
    temperature=0.9,
    groq_api_key=os.getenv('GROQ_API_KEY')
)

class IdeaGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_ideas(self, domain: str, n_ideas: int = 5) -> List[str]:
        template = (
            "Suggest {n_ideas} trending and highly relevant article or blog post titles "
            "related to the domain '{domain}'. Each title should be catchy and under 15 words. "
            "Return only a numbered list of titles without extra explanation."
        )

        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()

        try:
            result = chain.invoke({"domain": domain, "n_ideas": n_ideas})
            return [line.strip(" -") for line in result.strip().split("\n") if line.strip()]
        except Exception as e:
            print(f" Error generating ideas: {e}")
            return []

    def save_ideas_to_json(self, ideas: List[str], domain: str, filepath: str = "idea_generated.json"):
        idea_data = {
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "topic_ideas": ideas
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(idea_data, f, indent=4)
        print(f"\n Ideas saved to {filepath}")

# Example usage
if __name__ == "__main__":
    agent = IdeaGeneratorAgent(llm)
    domain = input("Enter a domain (e.g., AI, health, marketing): ")
    ideas = agent.generate_ideas(domain)

    print("\n Generated Ideas:\n")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea}")

    # Save the ideas to JSON
    if ideas:
        agent.save_ideas_to_json(ideas, domain)