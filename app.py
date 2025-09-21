import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit UI
st.set_page_config(page_title="Professional README Generator", page_icon="📝")
st.title("📝 AI-Powered Professional README Generator")
st.markdown("Generate well-defined and professional README files for your Github projects using Google Gemini.")

# User Input
with st.form("readme_form"):
    project_title = st.text_input("🚀 Project Title", placeholder="Example: AI README Generator")
    short_desc = st.text_area("🧾 Project Description")
    features = st.text_area("✨ Features (one per line)")
    installation = st.text_area("⚙️ Installation Instructions")
    usage = st.text_area("🖥️ Usage Examples")
    contributing = st.text_area("🤝 Contributing Guidelines")
    license = st.text_input("📜 License", value="MIT")
    github_username = st.text_input("👤 GitHub Username")
    repo_name = st.text_input("📁 Repository Name")
    generate = st.form_submit_button("Generate Professional README")

if generate:
    # Gemini Prompt
    prompt = f"""
    You are an expert technical writer. Generate a **GitHub-quality professional README.md** file for the following project in markdown format with perfect section titles, emojis, bullet points, badges, links, and code blocks. Format it like top open-source repos.

    Project Title: {project_title}
    Description: {short_desc}
    Features:
    {features}
    Installation Steps:
    {installation}
    Usage Instructions:
    {usage}
    Contributing Guidelines:
    {contributing}
    License: {license}
    GitHub Repository: https://github.com/{github_username}/{repo_name}

    Include the following:
    - A big title with emojis
    - Badges (placeholders for now)
    - Description section
    - Table of Contents
    - Features in bullet list
    - Installation with code blocks
    - Usage with examples
    - Contributing
    - License
    - Footer with GitHub link and author credit
    """

    with st.spinner("🚧 Generating your README.md..."):
        try:
            response = model.generate_content(prompt)
            readme_content = response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            st.error(f"❌ Gemini API error: {e}")
            st.stop()

    # Display Result
    st.subheader("📄 Preview Your README.md")
    st.code(readme_content, language='markdown')

    # Download Option
    st.download_button(
        label="📥 Download README.md",
        data=readme_content,
        file_name="README.md",
        mime="text/markdown"
    )
