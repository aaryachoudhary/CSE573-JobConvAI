import os
import json
import re
import requests
from typing import Optional, Dict, Any
import PyPDF2
from docx import Document
try:
    from .resume_schema import ResumeData
except ImportError:
    from resume_schema import ResumeData
import openai
import google.generativeai as genai

class ResumeParser:
    def __init__(self, llm_provider: str, api_key: str):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize the selected LLM provider"""
        if self.llm_provider == "OpenAI":
            openai.api_key = self.api_key
        elif self.llm_provider == "Anthropic":
            # Anthropic uses direct API calls, no setup needed
            pass
        elif self.llm_provider == "Google":
            genai.configure(api_key=self.api_key)
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.doc', '.docx']:
            return self._extract_from_docx(file_path)
        elif file_extension == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def parse_resume_with_llm(self, raw_text: str) -> ResumeData:
        """Parse resume text using the selected LLM"""
        prompt = self._create_parsing_prompt(raw_text)
        
        if self.llm_provider == "OpenAI":
            response = self._call_openai(prompt)
        elif self.llm_provider == "Anthropic":
            response = self._call_anthropic(prompt)
        elif self.llm_provider == "Google":
            response = self._call_google(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        return self._parse_llm_response(response)
    
    def _create_parsing_prompt(self, raw_text: str) -> str:
        """Create a detailed prompt for resume parsing"""
        return f"""
You are an expert resume parser. Parse the following resume text and extract structured information.

Resume Text:
{raw_text}

Please extract the following information and return it as a JSON object following this exact schema:

{{
    "personal_info": {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "phone number",
        "address": "full address",
        "linkedin": "LinkedIn profile URL if available",
        "github": "GitHub profile URL if available"
    }},
    "summary": "Professional summary or objective statement",
    "education": [
        {{
            "institute": "University/College Name",
            "degree": "Degree Type (Bachelor's, Master's, etc.)",
            "major": ["Major Field 1", "Major Field 2"],
            "dates": {{
                "from_date": "YYYY-MM",
                "to_date": "YYYY-MM or Present"
            }},
            "courses": ["Course 1", "Course 2"],
            "gpa": "GPA if mentioned"
        }}
    ],
    "experience": [
        {{
            "position": "Job Title",
            "company": "Company Name",
            "dates": {{
                "from_date": "YYYY-MM",
                "to_date": "YYYY-MM or Present"
            }},
            "description": "Detailed job description and responsibilities",
            "skills_used": ["Skill 1", "Skill 2"],
            "location": "Work location if mentioned"
        }}
    ],
    "skills": [
        {{
            "name": "Skill Name",
            "category": "Technical/Soft/Language",
            "proficiency": "Beginner/Intermediate/Advanced if mentioned"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["Tech 1", "Tech 2"],
            "dates": {{
                "from_date": "YYYY-MM",
                "to_date": "YYYY-MM"
            }},
            "url": "Project URL if available"
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "YYYY-MM",
            "expiry": "YYYY-MM if applicable"
        }}
    ],
    "languages": ["Language 1", "Language 2"],
    "achievements": ["Achievement 1", "Achievement 2"]
}}

Important instructions:
1. Extract ALL information from the resume text
2. If a field is not present, use an empty array [] - NEVER use null values in arrays
3. For dates, use YYYY-MM format or "Present" for current positions
4. Be thorough in extracting skills, especially technical skills
5. Include all work experiences, even if brief
6. Extract all educational qualifications
7. For arrays (languages, achievements, skills, etc.), only include actual values - skip empty or missing items
8. Return ONLY the JSON object, no additional text or formatting
"""
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API using direct HTTP requests"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4000,
            "temperature": 0,
            "system": (
                "You are a resume parser. Return valid JSON only—no prose. "
                "If information is missing, use null. Follow the exact schema provided."
            ),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        }

        try:
            resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
            resp.raise_for_status()
            
            response_data = resp.json()
            text = response_data.get("content", [{"text": ""}])[0].get("text", "")
            
            # Attempt to isolate a JSON object/array
            json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if not json_match:
                return text.strip()

            json_str = json_match.group(0)
            try:
                # Try to parse as JSON to validate
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                # Clean up the JSON string
                cleaned = json_str.replace("\n", " ").replace("\t", " ")
                cleaned = re.sub(r",\s*}", "}", cleaned)
                cleaned = re.sub(r",\s*]", "]", cleaned)
                try:
                    json.loads(cleaned)
                    return cleaned
                except Exception:
                    return text.strip()
                    
        except requests.exceptions.RequestException as e:
            raise Exception(f"Anthropic API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def _call_google(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")
    
    def _parse_llm_response(self, response: str) -> ResumeData:
        """Parse LLM response and create ResumeData object"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Parse JSON
            data = json.loads(response)
            
            # Create ResumeData object
            return ResumeData(**data)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create ResumeData object: {str(e)}")
