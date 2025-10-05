# Project Structure

```
ConvAgent/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── config.py              # Configuration settings
├── PROJECT_STRUCTURE.md   # This file
│
├── src/                   # Source code
│   ├── __init__.py
│   ├── app.py            # Streamlit web application
│   ├── resume_parser.py  # Resume parsing logic
│   ├── resume_schema.py  # Pydantic data models
│   └── neo4j_manager.py  # Neo4j database operations
│
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_anthropic_parser.py  # Test Anthropic resume parsing
│   ├── test_final.py             # Comprehensive system test
│   └── test_neo4j_connection.py  # Test Neo4j connection
│
└── docs/                  # Documentation
    ├── README.md
    └── NEO4J_SETUP.md
```

## How to Run

### Option 1: Using main.py (Recommended)
```bash
python main.py
```

### Option 2: Direct Streamlit
```bash
streamlit run src/app.py
```

## Key Files

- **main.py**: Main entry point with proper path handling
- **src/app.py**: Streamlit web interface
- **src/resume_parser.py**: AI-powered resume parsing
- **src/resume_schema.py**: Data validation models
- **src/neo4j_manager.py**: Knowledge graph operations
- **tests/**: All test files for development
- **scripts/**: Utility scripts for setup
- **docs/**: Documentation and setup guides
