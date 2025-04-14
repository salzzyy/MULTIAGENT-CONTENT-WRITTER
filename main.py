import os
from dotenv import load_dotenv
from workflows.content_pipeline import run_content_pipeline

load_dotenv()

def main():
    print("=== Content Writing Pipeline ===")
    domain = input("Enter a domain (e.g., AI, marketing): ").strip()
    n_ideas = int(input("Enter number of ideas to generate (default 5): ") or 5)
    
    try:
        article = run_content_pipeline(domain, n_ideas=n_ideas)
        print("\n Final Article Preview:\n")
        print(article[:500] + "..." if len(article) > 500 else article)
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    main()