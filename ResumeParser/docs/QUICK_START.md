# Quick Start Guide

## 🚀 Get Started in 5 Minutes

> **Prerequisites**: Python 3.8+, Neo4j Desktop installed

### 1. Install & Run
```bash
pip install -r requirements.txt
python main.py
```

### 2. Open Browser
Go to: http://localhost:8501

### 3. Configure & Parse
1. **Select LLM provider** (OpenAI, Anthropic, or Google)
2. **Enter API key** for your chosen provider
3. **Configure Neo4j** connection (URI: `neo4j://localhost:7687`, Username: `neo4j`)
4. **Upload and parse resumes!**

## 🔧 Troubleshooting

### Neo4j Connection Issues
- Make sure Neo4j Desktop is running
- Check the correct port in Neo4j Desktop Details tab
- Try different URI formats: `neo4j://localhost:7687`, `bolt://localhost:7687`

### API Key Issues
- Get OpenAI key: https://platform.openai.com/api-keys
- Get Anthropic key: https://console.anthropic.com/
- Get Google key: https://makersuite.google.com/app/apikey

### Common Errors
- **Import errors**: Make sure you're in the project root directory
- **Port already in use**: Stop other Streamlit instances or change port
- **File upload issues**: Check file format (PDF, DOCX, TXT only)

## 📊 Viewing Your Knowledge Graph

1. Open Neo4j Browser (click "Open" next to your database)
2. Run queries to explore your data:
   ```cypher
   MATCH (n) RETURN n LIMIT 25
   ```
3. See common skills between resumes:
   ```cypher
   MATCH (s:Skill)<-[:HAS_SKILL]-(r:Resume)
   WITH s, collect(r.name) as resumes
   WHERE size(resumes) > 1
   RETURN s.name as Skill, resumes
   ```
