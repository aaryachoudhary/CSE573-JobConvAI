#!/usr/bin/env python3
"""
Test Neo4j connection and create test data
"""

from neo4j_manager import Neo4jManager

def test_neo4j():
    """Test Neo4j connection and create test data"""
    
    print("🔍 Testing Neo4j Connection...")
    
    # Get connection details
    uri = input("Enter Neo4j URI (default: neo4j://localhost:7687): ").strip()
    if not uri:
        uri = "neo4j://localhost:7687"
    
    username = input("Enter username (default: neo4j): ").strip()
    if not username:
        username = "neo4j"
    
    password = input("Enter password: ")
    
    try:
        # Test connection
        print("  Testing connection...")
        manager = Neo4jManager(uri, username, password)
        
        # Create a simple test node
        print("  Creating test node...")
        with manager.driver.session() as session:
            session.run("CREATE (n:Test {name: 'Hello Neo4j', created: datetime()})")
            print("  ✅ Test node created!")
            
            # Query the test node
            result = session.run("MATCH (n:Test) RETURN n.name as name, n.created as created")
            record = result.single()
            if record:
                print(f"  ✅ Test node found: {record['name']} at {record['created']}")
            
            # Count all nodes
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            count = result.single()['total_nodes']
            print(f"  📊 Total nodes in database: {count}")
            
            # List node types
            result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
            print("  📋 Node types in database:")
            for record in result:
                print(f"    {record['labels']}: {record['count']}")
        
        manager.close()
        print("✅ Neo4j connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

if __name__ == "__main__":
    test_neo4j()
