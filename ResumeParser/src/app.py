import streamlit as st
import os
import tempfile
import uuid
from datetime import datetime
try:
    from .resume_parser import ResumeParser
    from .neo4j_manager import Neo4jManager
    from .resume_schema import ResumeData
except ImportError:
    from resume_parser import ResumeParser
    from neo4j_manager import Neo4jManager
    from resume_schema import ResumeData
import json

# Page configuration
st.set_page_config(
    page_title="Resume Parser & Knowledge Graph Builder",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'parsed_resumes' not in st.session_state:
    st.session_state.parsed_resumes = []
if 'neo4j_connected' not in st.session_state:
    st.session_state.neo4j_connected = False

def main():
    st.title("📄 Resume Parser & Knowledge Graph Builder")
    st.markdown("Upload resumes, parse them with AI, and build a knowledge graph in Neo4j")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LLM Selection
        st.subheader("🤖 LLM Provider")
        llm_provider = st.selectbox(
            "Select LLM Provider",
            ["OpenAI", "Anthropic", "Google"],
            help="Choose the LLM provider for resume parsing"
        )
        
        # API Key Input
        st.subheader("🔑 API Key")
        api_key = st.text_input(
            "Enter API Key",
            type="password",
            help=f"Enter your {llm_provider} API key"
        )
        
        # Neo4j Configuration
        st.subheader("🗄️ Neo4j Database")
        neo4j_uri = st.text_input(
            "Neo4j URI",
            value="neo4j://localhost:7687",
            help="Neo4j database URI"
        )
        neo4j_user = st.text_input(
            "Username",
            value="neo4j",
            help="Neo4j username"
        )
        neo4j_password = st.text_input(
            "Password",
            type="password",
            help="Neo4j password"
        )
        
        # Test Neo4j Connection
        if st.button("Test Neo4j Connection"):
            try:
                neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
                neo4j_manager.close()
                st.success("✅ Neo4j connection successful!")
                st.session_state.neo4j_connected = True
            except Exception as e:
                st.error(f"❌ Neo4j connection failed: {str(e)}")
                st.session_state.neo4j_connected = False
                
                # Provide helpful guidance
                st.info("""
                **Troubleshooting Tips:**
                1. Make sure Neo4j Desktop is running
                2. Make sure your database (resumekg) is started
                3. Try these URI formats:
                   - `bolt://localhost:7687`
                   - `bolt://127.0.0.1:7687`
                   - `neo4j://localhost:7687`
                4. Check username (usually 'neo4j') and password
                5. See NEO4J_SETUP.md for detailed instructions
                """)
        
        # File Upload
        st.subheader("📁 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        # Parse Resume Button
        if st.button("🚀 Parse Resume", disabled=not (uploaded_file and api_key)):
            if uploaded_file and api_key:
                parse_resume(uploaded_file, llm_provider, api_key, neo4j_uri, neo4j_user, neo4j_password)
            else:
                st.error("Please upload a file and enter an API key")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Parsed Resumes")
        
        if st.session_state.parsed_resumes:
            for i, resume_data in enumerate(st.session_state.parsed_resumes):
                with st.expander(f"Resume {i+1}: {resume_data.get('name', 'Unknown')}"):
                    display_resume_data(resume_data)
        else:
            st.info("No resumes parsed yet. Upload a resume to get started!")
    
    with col2:
        st.header("📈 Knowledge Graph Stats")
        
        if st.session_state.neo4j_connected:
            try:
                neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
                resumes = neo4j_manager.get_all_resumes()
                neo4j_manager.close()
                
                st.metric("Total Resumes", len(resumes))
                
                if resumes:
                    st.subheader("Recent Resumes")
                    for resume in resumes[-5:]:  # Show last 5
                        st.write(f"• {resume['name']}")
            except Exception as e:
                st.error(f"Error connecting to Neo4j: {str(e)}")
        else:
            st.info("Connect to Neo4j to see statistics")

def parse_resume(uploaded_file, llm_provider, api_key, neo4j_uri, neo4j_user, neo4j_password):
    """Parse a resume and add it to the knowledge graph"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Initialize parser
        parser = ResumeParser(llm_provider, api_key)
        
        # Extract text
        with st.spinner("Extracting text from resume..."):
            raw_text = parser.extract_text_from_file(tmp_file_path)
        
        # Parse with LLM
        with st.spinner(f"Parsing resume with {llm_provider}..."):
            parsed_data = parser.parse_resume_with_llm(raw_text)
        
        # Convert to dictionary for display
        resume_dict = parsed_data.model_dump()
        resume_dict['id'] = str(uuid.uuid4())
        resume_dict['name'] = parsed_data.personal_info.get('name', 'Unknown')
        resume_dict['parsed_at'] = datetime.now().isoformat()
        
        # Add to session state
        st.session_state.parsed_resumes.append(resume_dict)
        
        # Add to Neo4j if connected
        if st.session_state.neo4j_connected:
            try:
                with st.spinner("Adding to Neo4j knowledge graph..."):
                    neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
                    neo4j_manager.create_resume_node(parsed_data, resume_dict['id'])
                    neo4j_manager.close()
                
                st.success("✅ Resume parsed and added to knowledge graph!")
            except Exception as e:
                st.error(f"❌ Failed to add to Neo4j: {str(e)}")
                st.success("✅ Resume parsed successfully!")
        else:
            st.success("✅ Resume parsed successfully!")
        
        # Display parsed data
        st.json(resume_dict)
        
    except Exception as e:
        st.error(f"❌ Error parsing resume: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

def display_resume_data(resume_data):
    """Display parsed resume data in a formatted way"""
    
    # Personal Information
    if resume_data.get('personal_info'):
        st.subheader("👤 Personal Information")
        personal_info = resume_data['personal_info']
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {personal_info.get('name', 'N/A')}")
            st.write(f"**Email:** {personal_info.get('email', 'N/A')}")
        
        with col2:
            st.write(f"**Phone:** {personal_info.get('phone', 'N/A')}")
            st.write(f"**Location:** {personal_info.get('address', 'N/A')}")
    
    # Summary
    if resume_data.get('summary'):
        st.subheader("📝 Summary")
        st.write(resume_data['summary'])
    
    # Education
    if resume_data.get('education'):
        st.subheader("🎓 Education")
        for edu in resume_data['education']:
            with st.container():
                st.write(f"**{edu.get('degree', 'N/A')} in {', '.join(edu.get('major', []))}**")
                st.write(f"*{edu.get('institute', 'N/A')}*")
                if edu.get('dates'):
                    dates = edu['dates']
                    st.write(f"📅 {dates.get('from_date', 'N/A')} - {dates.get('to_date', 'N/A')}")
                if edu.get('gpa'):
                    st.write(f"📊 GPA: {edu['gpa']}")
                st.write("---")
    
    # Experience
    if resume_data.get('experience'):
        st.subheader("💼 Experience")
        for exp in resume_data['experience']:
            with st.container():
                st.write(f"**{exp.get('position', 'N/A')}** at *{exp.get('company', 'N/A')}*")
                if exp.get('dates'):
                    dates = exp['dates']
                    st.write(f"📅 {dates.get('from_date', 'N/A')} - {dates.get('to_date', 'N/A')}")
                if exp.get('description'):
                    st.write(exp['description'])
                if exp.get('skills_used'):
                    st.write(f"**Skills:** {', '.join(exp['skills_used'])}")
                st.write("---")
    
    # Skills
    if resume_data.get('skills'):
        st.subheader("🛠️ Skills")
        skills_by_category = {}
        for skill in resume_data['skills']:
            category = skill.get('category', 'Other')
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill.get('name', ''))
        
        for category, skills in skills_by_category.items():
            st.write(f"**{category}:** {', '.join(skills)}")
    
    # Projects
    if resume_data.get('projects'):
        st.subheader("🚀 Projects")
        for project in resume_data['projects']:
            with st.container():
                st.write(f"**{project.get('name', 'N/A')}**")
                if project.get('description'):
                    st.write(project['description'])
                if project.get('technologies'):
                    st.write(f"**Technologies:** {', '.join(project['technologies'])}")
                st.write("---")

if __name__ == "__main__":
    main()
