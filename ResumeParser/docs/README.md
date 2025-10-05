# Resume Parser & Knowledge Graph Builder

A comprehensive system for parsing resumes using AI and building a knowledge graph in Neo4j. This application allows you to upload resumes in various formats, extract structured information using different LLM providers, and store the data in a Neo4j knowledge graph for advanced querying and analysis.

## Features

- **Multi-format Resume Support**: PDF, DOCX, and TXT files
- **Multiple LLM Providers**: OpenAI, Anthropic, Google
- **Structured Data Extraction**: Education, experience, skills, projects
- **Neo4j Knowledge Graph**: Automatic node and relationship creation
- **Real-time Parsing**: Instant feedback and visualization

## Quick Start

See [QUICK_START.md](QUICK_START.md) for a 5-minute setup guide.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ConvAgent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Neo4j database:**
   - Install [Neo4j Desktop](https://neo4j.com/download/)
   - Create a new database
   - Note connection details (URI, username, password)

## Usage

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Open your browser:** http://localhost:8501

3. **Configure and parse:**
   - Select LLM provider and enter API key
   - Configure Neo4j connection
   - Upload and parse resumes

## Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Neo4j Setup](NEO4J_SETUP.md)** - Detailed Neo4j configuration
- **[Project Structure](../PROJECT_STRUCTURE.md)** - Code organization

## API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google**: https://makersuite.google.com/app/apikey

## License

This project is licensed under the MIT License.
