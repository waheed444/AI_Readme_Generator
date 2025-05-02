
import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# System Prompt for Professional README Generation
MARKDOWN_PROMPT = """You are an expert at creating professional, GitHub-optimized README.md files.  
Generate a **clean, comprehensive, and polished** README.md file based on the provided project details, styled like a modern, professional README for a Python tool (e.g., UV). The output should be engaging, use emojis sparingly for visual appeal, and include code blocks for commands, similar to the UV README.

---

## **Task:**  
Create a GitHub README.md file with:  
✔ **Clear headings** (H1-H3) with relevant emojis (e.g., 🚀, 📋)  
✔ **Code blocks** for commands (e.g., `sh` for shell, `python` for scripts)  
✔ **Badges** for license, status, and GitHub stars (if URL provided)  
✔ **Table of Contents** for navigation  
✔ **Professional tone**, concise yet detailed, explaining all project aspects  
✔ **Emojis** for section headers and lists (e.g., ✅, 🔧)  

---

## **📌 Project Details:**  
{user_input}

---

## **📜 README Structure:**  
### 1️⃣ **Introduction**  
   - `#` Project title with emoji (e.g., 🚀)  
   - Engaging project description explaining purpose and value  

### 2️⃣ **Table of Contents**  
   - List all sections with clickable links (e.g., `[Why Use](#why-use)`)  

### 3️⃣ **Why Use {project_name}?**  
   - Explain key benefits and features  
   - Use bullet points with emojis (e.g., ✅)  

### 4️⃣ **Prerequisites**  
   - List requirements (e.g., software, versions, internet)  
   - Use bullet points  

### 5️⃣ **Installing {project_name}**  
   - Step-by-step installation instructions  
   - Include code blocks for commands (e.g., `pip install {project_name}`)  

### 6️⃣ **Core Commands and Use Cases**  
   - Group commands by functionality (e.g., Virtual Environment, Package Management)  
   - For each command:  
     - Command syntax in code block  
     - Use case description  
     - Example in code block  
   - Use subheadings for each group  

### 7️⃣ **Project Structure**  
   - Describe key files/folders in a tree-like code block  

### 8️⃣ **Contributing**  
   - Guidelines for contributions  
   - Link to GitHub issues/pull requests (if URL provided)  

### 9️⃣ **License**  
   - Specify license (e.g., MIT) with link  

### 10️⃣ **Connect**  
   - Links to socials (e.g., GitHub, LinkedIn, email) if provided  

---

## **🎨 Formatting Guidelines:**  
✔ Use emojis sparingly (e.g., 🚀 for title, ✅ for benefits)  
✔ Code blocks for all commands (e.g., ```sh\npip install {project_name}\n```)  
✔ Badges in Markdown (e.g., `![License](https://img.shields.io/badge/license-MIT-blue.svg)`)  
✔ Ensure readability for technical and non-technical users  
✔ Output **only the Markdown content**  

---

**💡 Output the README.md file directly**  
"""

# Streamlit UI Configuration
st.set_page_config(
    page_title="AI README Generator",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="auto"
)

# Custom CSS for Professional Look
st.markdown("""
<style>
.stTextInput>div>div>input {border-radius: 8px; padding: 10px; border: 1px solid #ccc;}
.stButton>button {background-color: #1e88e5; color: white; border-radius: 8px; padding: 12px; font-weight: bold;}
.stSpinner {color: #1e88e5;}
.stMarkdown {font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;}
h1 {color: #1e88e5;}
</style>
""", unsafe_allow_html=True)

# Main Application Logic
def main():
    st.title("📝 AI README Generator")
    st.markdown("Generate a professional GitHub README for your project, complete with code blocks, emojis, and comprehensive details.")

    # Input Collection
    user_input = st.text_area(
        "Enter your project details:",
        height=250,
        placeholder="""Provide details about your project:
- Project name
- Description (e.g., purpose, what it does)
- Why use it? (e.g., key benefits, features)
- Prerequisites (e.g., Python version, tools)
- Installation steps (e.g., commands)
- Core commands (e.g., command syntax, use cases, examples)
- Project structure (e.g., key files/folders)
- GitHub URL (optional)
- License (e.g., MIT)
- Status (e.g., Active, In Development)
- Social links (e.g., GitHub, LinkedIn, email)"""
    )

    # Generate README
    if st.button("Generate README", use_container_width=True):
        if not user_input.strip():
            st.error("Please provide project details.")
            return

        # Extract project name for prompt customization
        project_name_match = re.search(r"Project Name:\s*(.+)", user_input, re.IGNORECASE)
        project_name = project_name_match.group(1).strip() if project_name_match else "YourProject"

        with st.spinner("Crafting professional README..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(MARKDOWN_PROMPT.format(user_input=user_input, project_name=project_name))
                markdown_output = response.text

                # Preview and Download
                st.subheader("README Preview")
                st.markdown(markdown_output)
                st.code(markdown_output, language="markdown")

                st.download_button(
                    label="Download README.md",
                    data=markdown_output,
                    file_name="README.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                st.success("README generated successfully!")
            except Exception as e:
                st.error(f"Error generating README: {str(e)}")

if __name__ == "__main__":
    main()
