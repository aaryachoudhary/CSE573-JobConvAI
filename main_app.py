"""
Main Application
Integrates Resume Parser and Job Parser for intelligent job matching
"""

import streamlit as st
import os
from typing import List, Dict, Any
import sys

# Add both modules to path
sys.path.append('ResumeParser')
sys.path.append('JobParser')

from ResumeParser.src.app import ResumeParserApp
from JobParser.job_parser import JobParser
from JobParser.job_apis import create_job_manager
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class ConvAgentApp:
    """Main application combining resume and job parsing"""
    
    def __init__(self):
        self.resume_parser = ResumeParserApp()
        self.job_parser = JobParser(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        self.job_api_manager = create_job_manager()
    
    def run(self):
        """Run the main application"""
        st.set_page_config(
            page_title="ConvAgent - Intelligent Job Matching",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 ConvAgent - Intelligent Job Matching")
        st.markdown("**AI-powered resume analysis and job matching platform**")
        
        # Sidebar for navigation
        st.sidebar.title("Navigation")
        app_mode = st.sidebar.selectbox(
            "Choose your action",
            ["Resume Analysis", "Job Search", "Job Matching", "Analytics Dashboard"]
        )
        
        if app_mode == "Resume Analysis":
            self.resume_analysis_page()
        elif app_mode == "Job Search":
            self.job_search_page()
        elif app_mode == "Job Matching":
            self.job_matching_page()
        elif app_mode == "Analytics Dashboard":
            self.analytics_dashboard_page()
    
    def resume_analysis_page(self):
        """Resume analysis page"""
        st.header("📄 Resume Analysis")
        st.markdown("Upload and analyze resumes to extract skills, experience, and qualifications")
        
        # Use the existing resume parser functionality
        self.resume_parser.run_resume_analysis()
    
    def job_search_page(self):
        """Job search and fetching page"""
        st.header("🔍 Job Search")
        st.markdown("Search and fetch job postings from various APIs")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_query = st.text_input("Job Title/Keywords", placeholder="e.g., Python Developer, Data Scientist")
            location = st.text_input("Location (optional)", placeholder="e.g., New York, Remote")
            limit = st.slider("Number of jobs to fetch", 10, 100, 50)
        
        with col2:
            st.markdown("**Available APIs:**")
            for api in self.job_api_manager.get_available_apis():
                st.markdown(f"✅ {api.title()}")
        
        if st.button("Search Jobs", type="primary"):
            if job_query:
                with st.spinner("Fetching jobs..."):
                    jobs = self.job_parser.fetch_and_parse_jobs(job_query, location, limit)
                
                if jobs:
                    st.success(f"Found {len(jobs)} jobs!")
                    
                    # Save to database option
                    if st.button("Save Jobs to Database"):
                        self.job_parser.save_jobs_to_neo4j(jobs)
                        st.success("Jobs saved to database!")
                    
                    # Display jobs
                    self.display_jobs(jobs)
                else:
                    st.warning("No jobs found. Try different keywords.")
            else:
                st.error("Please enter a job query")
    
    def job_matching_page(self):
        """Job matching based on resume skills"""
        st.header("🎯 Job Matching")
        st.markdown("Find the best job matches based on your resume skills")
        
        # Get resume skills from database
        resume_skills = self.get_resume_skills()
        
        if resume_skills:
            st.markdown(f"**Found {len(resume_skills)} skills in your resume:**")
            st.markdown(", ".join(resume_skills[:10]) + ("..." if len(resume_skills) > 10 else ""))
            
            if st.button("Find Job Matches", type="primary"):
                with st.spinner("Finding job matches..."):
                    matches = self.job_parser.get_job_matches_for_resume(resume_skills, 20)
                
                if matches:
                    st.success(f"Found {len(matches)} job matches!")
                    self.display_job_matches(matches)
                else:
                    st.warning("No job matches found. Try uploading more resumes or searching for jobs first.")
        else:
            st.warning("No resume skills found. Please upload and analyze resumes first.")
    
    def analytics_dashboard_page(self):
        """Analytics dashboard"""
        st.header("📊 Analytics Dashboard")
        st.markdown("Insights into job market trends and skill demand")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Skill Demand")
            skill_demand = self.get_skill_demand()
            if skill_demand:
                # Create a simple bar chart
                import pandas as pd
                df = pd.DataFrame(skill_demand[:10])
                st.bar_chart(df.set_index('skill')['demand'])
            else:
                st.info("No skill demand data available. Fetch some jobs first.")
        
        with col2:
            st.subheader("Database Statistics")
            stats = self.get_database_stats()
            for key, value in stats.items():
                st.metric(key, value)
    
    def display_jobs(self, jobs: List[Dict[str, Any]]):
        """Display job listings"""
        for i, job in enumerate(jobs):
            with st.expander(f"{job.title} at {job.company}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Location:** {job.location}")
                    st.markdown(f"**Employment Type:** {job.employment_type}")
                    st.markdown(f"**Experience Level:** {job.experience_level}")
                    if job.salary_min and job.salary_max:
                        st.markdown(f"**Salary:** ${job.salary_min:,} - ${job.salary_max:,} {job.salary_currency}")
                
                with col2:
                    st.markdown(f"**Source:** {job.source}")
                    if job.remote_allowed:
                        st.markdown("🌍 **Remote OK**")
                    if job.visa_sponsorship:
                        st.markdown("🛂 **Visa Sponsorship**")
                
                if job.skills:
                    st.markdown(f"**Skills:** {', '.join(job.skills[:10])}")
                
                if job.description:
                    st.markdown("**Description:**")
                    st.text(job.description[:500] + "..." if len(job.description) > 500 else job.description)
    
    def display_job_matches(self, matches: List[Dict[str, Any]]):
        """Display job matches with matching skills"""
        for i, match in enumerate(matches):
            job = match['j']
            matching_skills = match['matching_skills']
            skill_count = match['skill_count']
            
            with st.expander(f"🎯 {job['title']} at {job.get('company', 'Unknown')} ({skill_count} matching skills)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Location:** {job.get('location', 'Unknown')}")
                    st.markdown(f"**Employment Type:** {job.get('employment_type', 'Unknown')}")
                    st.markdown(f"**Experience Level:** {job.get('experience_level', 'Unknown')}")
                
                with col2:
                    st.markdown(f"**Match Score:** {skill_count} skills")
                    if job.get('url'):
                        st.markdown(f"[View Job]({job['url']})")
                
                st.markdown(f"**Matching Skills:** {', '.join(matching_skills)}")
                
                if job.get('description'):
                    st.markdown("**Description:**")
                    st.text(job['description'][:300] + "..." if len(job['description']) > 300 else job['description'])
    
    def get_resume_skills(self) -> List[str]:
        """Get all skills from resumes in the database"""
        try:
            with self.job_parser.neo4j_manager.driver.session() as session:
                result = session.run("""
                    MATCH (r:Resume)-[:HAS_SKILL]->(s:Skill)
                    RETURN collect(DISTINCT s.name) as skills
                """)
                record = result.single()
                return record['skills'] if record else []
        except Exception as e:
            st.error(f"Error fetching resume skills: {e}")
            return []
    
    def get_skill_demand(self) -> List[Dict[str, Any]]:
        """Get skill demand statistics"""
        try:
            return self.job_parser.neo4j_manager.get_skill_demand()
        except Exception as e:
            st.error(f"Error fetching skill demand: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            with self.job_parser.neo4j_manager.driver.session() as session:
                # Get counts for different node types
                stats = {}
                
                node_types = ['Resume', 'Job', 'Company', 'Skill', 'Position', 'Location']
                for node_type in node_types:
                    result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                    count = result.single()['count']
                    stats[node_type] = count
                
                return stats
        except Exception as e:
            st.error(f"Error fetching database stats: {e}")
            return {}

def main():
    """Main entry point"""
    app = ConvAgentApp()
    app.run()

if __name__ == "__main__":
    main()
