import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io
import base64
from PIL import Image

# PDF support
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    st.warning("⚠️ pypdf not installed. Run: pip install pypdf")

# DOCX support
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("⚠️ python-docx not installed. Run: pip install python-docx")

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(
    page_title="AI README Generator",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .upload-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📝 AI README Generator</h1>
    <p>Upload your project files and generate professional README files instantly</p>
</div>
""", unsafe_allow_html=True)

# File extract functions
def extract_text_from_pdf(pdf_file):
    if not PYPDF_AVAILABLE:
        st.error("PDF processing not available. Install: pip install pypdf")
        return ""
    try:
        pdf_reader = pypdf.PdfReader(pdf_file)
        return "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(docx_file):
    if not DOCX_AVAILABLE:
        st.error("DOCX processing not available. Install: pip install python-docx")
        return ""
    try:
        doc = Document(docx_file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

def process_image(image_file):
    try:
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"[Image uploaded: {image_file.name}, Size: {image.size}]"
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return ""

# Upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.subheader("📁 Upload Project Files")
st.markdown("Upload any combination of files to generate your README:")

col1, col2 = st.columns(2)

with col1:
    allowed_types = ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'png', 'jpg', 'jpeg']
    if PYPDF_AVAILABLE:
        allowed_types.append('pdf')
    if DOCX_AVAILABLE:
        allowed_types.append('docx')

    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=allowed_types,
        help="Supported: Text, code, " +
             (", PDFs" if PYPDF_AVAILABLE else "") +
             (", Word docs" if DOCX_AVAILABLE else "") +
             ", and images"
    )

with col2:
    manual_input = st.text_area(
        "Or paste project description",
        placeholder="Describe your project, its features, and how to use it...",
        height=150
    )

st.markdown('</div>', unsafe_allow_html=True)

# Extract content
extracted_content = ""
if uploaded_files:
    st.subheader("📋 Processing Files...")
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'pdf' and PYPDF_AVAILABLE:
            content = extract_text_from_pdf(uploaded_file)
        elif file_extension == 'docx' and DOCX_AVAILABLE:
            content = extract_text_from_docx(uploaded_file)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            content = process_image(uploaded_file)
        else:
            try:
                content = uploaded_file.read().decode("utf-8", errors="ignore")
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {e}")
                content = ""

        extracted_content += f"\n--- Content from {uploaded_file.name} ---\n{content}\n"

    if extracted_content:
        with st.expander("📄 View Extracted Content"):
            st.text_area("Extracted content:", extracted_content, height=200)

# Form for extra details
st.subheader("⚙️ Additional Details (Optional)")
with st.form("readme_form"):
    col1, col2 = st.columns(2)
    with col1:
        project_title = st.text_input("Project Title", placeholder="Auto-detected from files")
        github_username = st.text_input("GitHub Username", placeholder="your-username")
        license_type = st.selectbox("License", ["MIT", "Apache 2.0", "GPL v3", "BSD", "Other"])
    with col2:
        repo_name = st.text_input("Repository Name", placeholder="project-name")
        tech_stack = st.text_input("Tech Stack", placeholder="Python, JavaScript, React...")
        contact_email = st.text_input("Contact Email", placeholder="your.email@example.com")

    generate = st.form_submit_button("🚀 Generate Professional README")

# README generation
if generate and (extracted_content or manual_input):
    all_content = f"{extracted_content}\n{manual_input}".strip()
    if not all_content:
        st.error("Please upload files or provide project description.")
        st.stop()

    prompt = f"""
    You are an expert technical writer specializing in GitHub README files.
    Analyze the following project content and generate a professional README.md.

    PROJECT CONTENT:
    {all_content}
    

    ADDITIONAL INFO:
    - Project Title: {project_title or "Auto-detect"}
    - Tech Stack: {tech_stack or "Auto-detect"}
    - License: {license_type}
    - GitHub: https://github.com/{github_username}/{repo_name} (if provided)
    - Contact: {contact_email}

    The README must include:
    1. Title with emojis
    2. Badges
    3. Description
    4. Table of contents
    5. Features with emojis
    6. Installation (with code blocks)
    7. Usage examples
    8. API docs (if any)
    9. Contributing guide
    10. License section
    11. Contact info
    12. Acknowledgments
    """

    with st.spinner("🤖 Generating your professional README..."):
        try:
            response = model.generate_content(prompt)
            readme_content = response.text
        except Exception as e:
            st.error(f"❌ Error generating README: {e}")
            st.stop()

    st.success("✅ README generated successfully!")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📄 Your Professional README.md")
        st.code(readme_content, language='markdown')
    with col2:
        st.subheader("📥 Download")
        st.download_button(
            label="Download README.md",
            data=readme_content,
            file_name="README.md",
            mime="text/markdown"
        )

elif generate:
    st.error("Please upload files or provide project description.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>AI Powered README File Generator for Github Projects  |   Built with Streamlit & Google Gemini</p>
</div>
""", unsafe_allow_html=True)
