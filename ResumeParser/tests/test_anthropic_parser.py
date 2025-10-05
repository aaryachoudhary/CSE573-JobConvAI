#!/usr/bin/env python3
"""
Test the resume parser with Anthropic
"""

from resume_parser import ResumeParser

def test_anthropic_parser():
    """Test resume parsing with Anthropic"""
    
    # Simple test resume text
    test_resume = """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2020-2024
    
    EXPERIENCE
    Software Engineer
    Tech Company Inc., 2022-2024
    Developed web applications using Python and JavaScript
    
    SKILLS
    Python, JavaScript, React, Node.js, SQL
    """
    
    try:
        print("🔍 Testing Resume Parser with Anthropic...")
        
        # Get API key
        api_key = input("Enter your Anthropic API key: ")
        
        # Create parser
        parser = ResumeParser("Anthropic", api_key)
        
        # Test text extraction (this should work)
        print("✅ Parser created successfully!")
        
        # Test parsing (this might fail if API key is invalid)
        print("📝 Testing resume parsing...")
        parsed_data = parser.parse_resume_with_llm(test_resume)
        
        print("✅ Resume parsing successful!")
        print(f"   Name: {parsed_data.personal_info.get('name', 'N/A')}")
        print(f"   Email: {parsed_data.personal_info.get('email', 'N/A')}")
        print(f"   Education count: {len(parsed_data.education)}")
        print(f"   Experience count: {len(parsed_data.experience)}")
        print(f"   Skills count: {len(parsed_data.skills)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_anthropic_parser()
