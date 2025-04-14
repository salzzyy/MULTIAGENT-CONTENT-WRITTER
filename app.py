import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from workflows.content_pipeline import run_content_pipeline
from agents.researcher import read_topic_from_json, research_topic, save_summary_to_json
from agents.writer import write_article

load_dotenv()

# Streamlit app configuration
st.set_page_config(page_title="Content Writing Pipeline", page_icon="📝", layout="wide")

def main():
    st.title("📝 Multi-Agent Content Writing Pipeline")
    st.markdown("Generate ideas, research topics, and write articles with AI-powered agents.")

    # Initialize session state
    if "ideas" not in st.session_state:
        st.session_state.ideas = []
    if "selected_idea" not in st.session_state:
        st.session_state.selected_idea = None
    if "research_summary" not in st.session_state:
        st.session_state.research_summary = ""
    if "article" not in st.session_state:
        st.session_state.article = ""

    # Input form
    with st.form(key="input_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            domain = st.text_input("Enter a domain (e.g., AI, marketing)", value="AI")
        with col2:
            n_ideas = st.number_input("Number of ideas to generate", min_value=1, max_value=10, value=5, step=1)
        submit_button = st.form_submit_button("Generate Ideas")

    if submit_button and domain:
        with st.spinner("Generating ideas..."):
            try:
                # Clear previous outputs
                st.session_state.ideas = []
                st.session_state.selected_idea = None
                st.session_state.research_summary = ""
                st.session_state.article = ""

                # Run idea generation via pipeline
                article = run_content_pipeline(domain, n_ideas=n_ideas, idea_index=1, output_dir="./output")
                # Read generated ideas
                idea_file = "./output/idea_generated.json"
                if os.path.exists(idea_file):
                    with open(idea_file, "r", encoding="utf-8") as f:
                        idea_data = json.load(f)
                        st.session_state.ideas = idea_data.get("topic_ideas", [])
                    st.success(f"Generated {len(st.session_state.ideas)} ideas!")
                else:
                    st.error("Failed to generate ideas. Check output/idea_generated.json.")
            except Exception as e:
                st.error(f"Error generating ideas: {e}")

    # Display ideas and allow selection
    if st.session_state.ideas:
        st.subheader("Generated Ideas")
        selected_idea = st.selectbox(
            "Select an idea to research:",
            options=st.session_state.ideas,
            index=0 if not st.session_state.selected_idea else st.session_state.ideas.index(st.session_state.selected_idea)
        )
        if st.button("Research Selected Idea") and selected_idea:
            with st.spinner("Researching topic..."):
                try:
                    st.session_state.selected_idea = selected_idea
                    st.session_state.research_summary = research_topic(selected_idea)
                    if st.session_state.research_summary:
                        save_summary_to_json(st.session_state.research_summary, selected_idea, "./output/research_summary.json")
                        st.success("Research completed!")
                    else:
                        st.error("Research failed.")
                except Exception as e:
                    st.error(f"Error researching topic: {e}")

    # Display research summary
    if st.session_state.research_summary:
        st.subheader("Research Summary")
        st.text_area("Summary", st.session_state.research_summary, height=200, disabled=True)
        if st.button("Generate Article"):
            with st.spinner("Writing article..."):
                try:
                    st.session_state.article = write_article(
                        st.session_state.research_summary,
                        topic=st.session_state.selected_idea,
                        output_dir="./output"
                    )
                    if st.session_state.article:
                        st.success("Article generated!")
                    else:
                        st.error("Article generation failed.")
                except Exception as e:
                    st.error(f"Error generating article: {e}")

    # Display article
    if st.session_state.article:
        st.subheader("Generated Article")
        st.markdown(st.session_state.article)

    # Download JSON files
    st.subheader("Download Outputs")
    for file_name in ["idea_generated.json", "research_summary.json", "article_output.json"]:
        file_path = os.path.join("./output", file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            st.download_button(
                label=f"Download {file_name}",
                data=file_content,
                file_name=file_name,
                mime="application/json"
            )
        else:
            st.write(f"{file_name} not yet generated.")

if __name__ == "__main__":
    main()