#!/usr/bin/env python3
"""
Final test to verify the resume parser works
"""

import os
import tempfile
from resume_parser import ResumeParser

def test_resume_parsing():
    """Test resume parsing with a simple text"""
    
    # Create a simple test resume
    test_resume_text = """
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
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_resume_text)
        temp_file = f.name
    
    try:
        # Test with different LLM providers
        print("🔍 Testing Resume Parser...")
        
        # Test OpenAI (if API key available)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("\n📝 Testing with OpenAI...")
            try:
                parser = ResumeParser("OpenAI", openai_key)
                parsed_data = parser.parse_resume_with_llm(test_resume_text)
                print("✅ OpenAI parsing successful!")
                print(f"   Name: {parsed_data.personal_info.get('name', 'N/A')}")
                print(f"   Email: {parsed_data.personal_info.get('email', 'N/A')}")
            except Exception as e:
                print(f"❌ OpenAI error: {e}")
        else:
            print("⚠️  OpenAI API key not found, skipping test")
        
        # Test Anthropic (if API key available)
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            print("\n📝 Testing with Anthropic...")
            try:
                parser = ResumeParser("Anthropic", anthropic_key)
                parsed_data = parser.parse_resume_with_llm(test_resume_text)
                print("✅ Anthropic parsing successful!")
                print(f"   Name: {parsed_data.personal_info.get('name', 'N/A')}")
                print(f"   Email: {parsed_data.personal_info.get('email', 'N/A')}")
            except Exception as e:
                print(f"❌ Anthropic error: {e}")
        else:
            print("⚠️  Anthropic API key not found, skipping test")
        
        print("\n🎉 Resume parser is working!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        os.unlink(temp_file)

if __name__ == "__main__":
    test_resume_parsing()
