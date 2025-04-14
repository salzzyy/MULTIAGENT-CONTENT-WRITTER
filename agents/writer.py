import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def determine_tone(research_summary):
    if "FDA" in research_summary or "Medicare" in research_summary or "WHO" in research_summary:
        return "Professional: write like a polished article from The Economist or Harvard Business Review."
    elif "infections" in research_summary or "RSV" in research_summary or "disease" in research_summary:
        return "Empowering Feminine Voice: strong yet graceful, inspiring and articulate like Annalise Keating."
    elif "nomination" in research_summary or "debate" in research_summary:
        return "Bold & Witty: make it sassy, punchy, with strong opinions and confidence."
    elif "vaccine" in research_summary or "healthcare" in research_summary:
        return "Conversational: write like you're talking to a friend, engaging, casual but informative."
    else:
        return "Storytelling: write in a narrative tone that captures emotions and paints vivid scenarios."

def write_article(research_summary: str, topic: str = "Generated Article", output_dir: str = "./output") -> str:
    """
    Generate an article based on the research summary and save it to article_output.json.
    
    Args:
        research_summary (str): The research summary to base the article on.
        topic (str): The topic of the article (default: "Generated Article").
        output_dir (str): Directory to save the article JSON (default: "./output").
    
    Returns:
        str: The generated article text.
    """
    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory confirmed: {os.path.abspath(output_dir)}")
    except Exception as e:
        print(f" Error creating output directory {output_dir}: {e}")
        return ""

    # Initialize Groq client
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Determine tone
    chosen_tone = determine_tone(research_summary)
    print(f"\n Automatically chosen tone: {chosen_tone}\n")
    
    # Confirm summary
    print(f"Summary provided:\n{research_summary}")
    print("Summary is assumed correct. Proceeding with article generation...\n")
    
    print(" Generating article...\n")
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert article writer. Your job is to take research bullet points and convert them into a beautiful article in the following style: {chosen_tone}",
                },
                {
                    "role": "user",
                    "content": f"Write an article based on the following research:\n\n{research_summary}",
                }
            ],
            temperature=0.7,
        )
        
        article = response.choices[0].message.content
        print("Final Written Article:\n")
        print(article)
        
        # Save the article to JSON
        article_file = os.path.join(output_dir, "article_output.json")
        article_data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "article": article.strip()
        }
        
        try:
            print(f"Attempting to save article to: {os.path.abspath(article_file)}")
            with open(article_file, "w", encoding="utf-8") as f:
                json.dump(article_data, f, indent=4)
            print(f"\n Article successfully saved to {article_file}")
        except PermissionError as e:
            print(f" Permission error saving {article_file}: {e}")
            return article
        except OSError as e:
            print(f"File system error saving {article_file}: {e}")
            return article
        except Exception as e:
            print(f" Unexpected error saving {article_file}: {e}")
            return article
        
        return article
        
    except Exception as e:
        print(f" Error generating article: {e}")
        return ""

if __name__ == "__main__":
    # For testing: read summary and generate article
    research_summary_file = "./output/research_summary.json"
    try:
        with open(research_summary_file, "r", encoding="utf-8") as f:
            research_data = json.load(f)
            research_summary = research_data.get("summary", "")
            topic = research_data.get("topic", "Generated Article")
            if not research_summary:
                raise ValueError("No research summary found in the JSON file.")
        write_article(research_summary, topic)
    except FileNotFoundError:
        print(f"{research_summary_file} not found.")
    except json.JSONDecodeError:
        print(f" Error decoding {research_summary_file}.")
    except Exception as e:
        print(f" Error: {e}")