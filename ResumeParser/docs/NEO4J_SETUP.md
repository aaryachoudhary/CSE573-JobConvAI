# Neo4j Desktop Setup Guide

## Step 1: Neo4j Desktop Configuration

1. **Open Neo4j Desktop**
2. **Create/Open your project** (kgdb)
3. **Start your database** (neo4j)
4. **Get connection details:**
   - Click on your database (neo4j)
   - Go to "Details" tab
   - Note the following information:
     - **Bolt URL**: Usually `neo4j://localhost:7687` (default)
     - **Username**: Usually `neo4j`
     - **Password**: The password you set when creating the database

## Step 2: Test Connection

You can test your connection using the Streamlit app:

1. **Start the app**: `python main.py`
2. **In the sidebar**:
   - Enter your Neo4j URI (e.g., `neo4j://localhost:7687`)
   - Enter your username (usually `neo4j`)
   - Enter your password
   - Click "Test Neo4j Connection"

## Step 3: Common Issues & Solutions

### Issue: "No connection could be made because the target machine actively refused it"
**Solutions:**
1. **Make sure Neo4j Desktop is running**
2. **Make sure your database is started** (not just the project)
3. **Check the correct port**: Neo4j Desktop might use a different port
4. **Try different URI formats**:
   - `neo4j://localhost:7687` (recommended)
   - `bolt://localhost:7687`
   - `bolt://127.0.0.1:7687`

### Issue: "Authentication failed"
**Solutions:**
1. **Check username**: Usually `neo4j`
2. **Check password**: The one you set during database creation
3. **Reset password** if needed in Neo4j Desktop

### Issue: "Database not found"
**Solutions:**
1. **Make sure database is started** in Neo4j Desktop
2. **Check database name** matches what you created

## Step 4: Verify Setup

Once connected, you should see:
- ✅ "Neo4j connection successful!" message
- Knowledge graph statistics in the main interface
- Ability to add resumes to the graph

## Alternative: Using Neo4j Browser

You can also verify your setup by:
1. **Opening Neo4j Browser** (click "Open" next to your database)
2. **Running a test query**: `MATCH (n) RETURN n LIMIT 5`
3. **This should return empty results initially** (no nodes yet)
