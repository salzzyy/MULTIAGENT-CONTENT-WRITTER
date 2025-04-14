import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from agents.idea_generator import IdeaGeneratorAgent
from agents.researcher import read_topic_from_json, research_topic, save_summary_to_json
from agents.writer import determine_tone, write_article

load_dotenv()

def run_content_pipeline(domain: str, n_ideas: int = 5, idea_index: int = 1, output_dir: str = "./output"):
    """
    Executes the full content generation pipeline: idea generation -> research -> writing.
    
    Args:
        domain (str): The domain for idea generation (e.g., "marketing").
        n_ideas (int): Number of ideas to generate.
        idea_index (int): Index of the idea to research and write about (1-based, default: 1).
        output_dir (str): Directory to save JSON outputs.
    
    Returns:
        str: The generated article text.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize LLM
    llm = ChatGroq(model="llama3-70b-8192", groq_api_key=os.getenv("GROQ_API_KEY"))
    
    # Step 1: Generate Ideas
    idea_agent = IdeaGeneratorAgent(llm)
    ideas = idea_agent.generate_ideas(domain, n_ideas)
    if not ideas:
        raise ValueError("No ideas generated.")
    
    idea_file = f"{output_dir}/idea_generated.json"
    idea_agent.save_ideas_to_json(ideas, domain, idea_file)
    print(f"Generated {len(ideas)} ideas.")
    
    # Step 2: Research Topic
    topic = read_topic_from_json(idea_file)
    if not topic:
        raise ValueError("No valid topic found.")
    
    summary = research_topic(topic)
    if not summary:
        raise ValueError("Research failed.")
    
    summary_file = f"{output_dir}/research_summary.json"
    save_summary_to_json(summary, topic, summary_file)
    print(f"Researched topic: {topic}")
    
    # Step 3: Write Article
    article = write_article(summary, topic)
    if not article:
        raise ValueError("Article generation failed.")
    
    return article