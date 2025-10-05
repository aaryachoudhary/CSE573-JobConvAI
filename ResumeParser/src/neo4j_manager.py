from neo4j import GraphDatabase
from typing import List, Dict, Any
from resume_schema import ResumeData, Education, Experience, Skill, Project, Certification
import json

class Neo4jManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
    
    def create_resume_node(self, resume_data: ResumeData, resume_id: str) -> None:
        """Create a resume node and all related nodes in Neo4j"""
        with self.driver.session() as session:
            # Create the main resume node
            session.run("""
                CREATE (r:Resume {
                    id: $resume_id,
                    name: $name,
                    email: $email,
                    phone: $phone,
                    summary: $summary
                })
            """, 
            resume_id=resume_id,
            name=resume_data.personal_info.get('name', ''),
            email=resume_data.personal_info.get('email', ''),
            phone=resume_data.personal_info.get('phone', ''),
            summary=resume_data.summary or ''
            )
            
            # Create education nodes and relationships
            self._create_education_nodes(session, resume_data.education, resume_id)
            
            # Create experience nodes and relationships
            self._create_experience_nodes(session, resume_data.experience, resume_id)
            
            # Create skill nodes and relationships
            self._create_skill_nodes(session, resume_data.skills, resume_id)
            
            # Create project nodes and relationships
            self._create_project_nodes(session, resume_data.projects, resume_id)
            
            # Create certification nodes and relationships
            self._create_certification_nodes(session, resume_data.certifications, resume_id)
            
            # Create language nodes and relationships
            self._create_language_nodes(session, resume_data.languages, resume_id)
    
    def _create_education_nodes(self, session, education_list: List[Education], resume_id: str):
        """Create education nodes and relationships"""
        for i, edu in enumerate(education_list):
            # Create institute and degree nodes, then create relationships
            session.run("""
                MERGE (i:Institute {name: $institute_name})
                ON CREATE SET i.type = 'Educational'
                WITH i
                MERGE (d:Degree {name: $degree_name})
                WITH i, d
                MATCH (r:Resume {id: $resume_id})
                CREATE (r)-[:HAS_EDUCATION {
                    from_date: $from_date,
                    to_date: $to_date,
                    gpa: $gpa
                }]->(i)
                CREATE (i)-[:OFFERS]->(d)
            """, 
            resume_id=resume_id,
            institute_name=edu.institute,
            degree_name=edu.degree,
            from_date=edu.dates.from_date,
            to_date=edu.dates.to_date,
            gpa=edu.gpa
            )
            
            # Create major nodes and relationships
            for major in edu.major:
                session.run("""
                    MERGE (m:Major {name: $major_name})
                    WITH m
                    MATCH (i:Institute {name: $institute_name})
                    CREATE (i)-[:HAS_MAJOR]->(m)
                """, major_name=major, institute_name=edu.institute)
            
            # Create course nodes and relationships
            for course in edu.courses:
                session.run("""
                    MERGE (c:Course {name: $course_name})
                    WITH c
                    MATCH (i:Institute {name: $institute_name})
                    CREATE (i)-[:OFFERS_COURSE]->(c)
                """, course_name=course, institute_name=edu.institute)
    
    def _create_experience_nodes(self, session, experience_list: List[Experience], resume_id: str):
        """Create experience nodes and relationships"""
        for i, exp in enumerate(experience_list):
            # Create company and position nodes, then create relationships
            session.run("""
                MERGE (c:Company {name: $company_name})
                ON CREATE SET c.type = 'Organization'
                WITH c
                MERGE (p:Position {name: $position_name})
                WITH c, p
                MATCH (r:Resume {id: $resume_id})
                CREATE (r)-[:HAS_EXPERIENCE {
                    from_date: $from_date,
                    to_date: $to_date,
                    description: $description,
                    location: $location
                }]->(c)
                CREATE (c)-[:HAS_POSITION]->(p)
            """, 
            resume_id=resume_id,
            company_name=exp.company,
            position_name=exp.position,
            from_date=exp.dates.from_date,
            to_date=exp.dates.to_date,
            description=exp.description,
            location=exp.location
            )
            
            # Create skill relationships for this experience
            for skill in exp.skills_used:
                session.run("""
                    MERGE (s:Skill {name: $skill_name})
                    WITH s
                    MATCH (c:Company {name: $company_name})
                    MATCH (p:Position {name: $position_name})
                    CREATE (p)-[:REQUIRES_SKILL]->(s)
                    CREATE (c)-[:USES_SKILL]->(s)
                """, skill_name=skill, company_name=exp.company, position_name=exp.position)
    
    def _create_skill_nodes(self, session, skill_list: List[Skill], resume_id: str):
        """Create skill nodes and relationships"""
        for skill in skill_list:
            session.run("""
                MERGE (s:Skill {name: $skill_name})
                ON CREATE SET s.category = $category, s.proficiency = $proficiency
                ON MATCH SET s.category = COALESCE(s.category, $category)
                WITH s
                MATCH (r:Resume {id: $resume_id})
                MERGE (r)-[:HAS_SKILL]->(s)
            """, 
            resume_id=resume_id,
            skill_name=skill.name,
            category=skill.category,
            proficiency=skill.proficiency
            )
    
    def _create_project_nodes(self, session, project_list: List[Project], resume_id: str):
        """Create project nodes and relationships"""
        for project in project_list:
            session.run("""
                CREATE (p:Project {
                    name: $project_name,
                    description: $description,
                    url: $url
                })
                WITH p
                MATCH (r:Resume {id: $resume_id})
                CREATE (r)-[:HAS_PROJECT]->(p)
            """, 
            resume_id=resume_id,
            project_name=project.name,
            description=project.description,
            url=project.url
            )
            
            # Create technology relationships
            for tech in project.technologies:
                session.run("""
                    MERGE (t:Technology {name: $tech_name})
                    WITH t
                    MATCH (p:Project {name: $project_name})
                    CREATE (p)-[:USES_TECHNOLOGY]->(t)
                """, tech_name=tech, project_name=project.name)
    
    def _create_certification_nodes(self, session, cert_list: List[Certification], resume_id: str):
        """Create certification nodes and relationships"""
        for cert in cert_list:
            session.run("""
                MERGE (c:Certification {name: $cert_name})
                ON CREATE SET c.issuer = $issuer, c.date = $date, c.expiry = $expiry
                WITH c
                MATCH (r:Resume {id: $resume_id})
                CREATE (r)-[:HAS_CERTIFICATION]->(c)
            """, 
            resume_id=resume_id,
            cert_name=cert.name,
            issuer=cert.issuer,
            date=cert.date,
            expiry=cert.expiry
            )
    
    def _create_language_nodes(self, session, language_list: List[str], resume_id: str):
        """Create language nodes and relationships"""
        for language in language_list:
            session.run("""
                MERGE (l:Language {name: $language_name})
                WITH l
                MATCH (r:Resume {id: $resume_id})
                CREATE (r)-[:SPEAKS_LANGUAGE]->(l)
            """, resume_id=resume_id, language_name=language)
    
    def get_resume_summary(self, resume_id: str) -> Dict[str, Any]:
        """Get a summary of a resume from Neo4j"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Resume {id: $resume_id})
                OPTIONAL MATCH (r)-[:HAS_EDUCATION]->(i:Institute)
                OPTIONAL MATCH (r)-[:HAS_EXPERIENCE]->(c:Company)
                OPTIONAL MATCH (r)-[:HAS_SKILL]->(s:Skill)
                RETURN r, collect(DISTINCT i.name) as institutes, 
                       collect(DISTINCT c.name) as companies,
                       collect(DISTINCT s.name) as skills
            """, resume_id=resume_id)
            
            record = result.single()
            if record:
                return {
                    'resume': dict(record['r']),
                    'institutes': record['institutes'],
                    'companies': record['companies'],
                    'skills': record['skills']
                }
            return {}
    
    def get_all_resumes(self) -> List[Dict[str, Any]]:
        """Get all resumes in the database"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Resume)
                RETURN r.id as id, r.name as name, r.email as email
            """)
            
            return [dict(record) for record in result]
