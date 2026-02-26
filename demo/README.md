# Demo & Integration Project

This directory contains demo projects and integration examples for ArcGIS Knowledge.

## 📁 Structure

### pro_projects/
ArcGIS Pro project files (.aprx) and resources for desktop-based knowledge graph operations.

### examples/
Python and web-based integration examples showing how to connect to ArcGIS Knowledge.

## 🎯 Demo Scenarios

1. **Create Knowledge Graph**: Tutorial creating a knowledge graph from ArcGIS Pro
2. **Entity Integration**: Connecting entities across spatial and non-spatial datasets
3. **Relationship Creation**: Building entity relationships

## 📚 Example Python Scripts

```python
# examples/create_knowledge_graph.py
"""
Demo: Create a knowledge graph using ArcGIS Knowledge API
"""
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient

# Initialize client
client = ArcGISKnowledgeClient(
    portal_url="https://your-portal.arcgis.com",
    username="your-username",
    password="your-password"
)

# Create knowledge graph
kg = client.create_knowledge_graph(
    title="Demo Knowledge Graph",
    description="Sample knowledge graph for demonstration"
)

print(f"Created knowledge graph: {kg['name']}")

# Add sample entities
entities = [
    {
        "name": "Facility A",
        "type": "Facility",
        "properties": {
            "location": "Building 1",
            "capacity": 100,
            "status": "active"
        }
    },
    {
        "name": "Facility B",
        "type": "Facility",
        "properties": {
            "location": "Building 2",
            "capacity": 75,
            "status": "operational"
        }
    }
]

for entity in entities:
    client.add_entity(kg['id'], entity)

print("Entities added successfully")
```

## 🌐 Web Demo Examples

See `web_examples/` for Angular/React or Flask web applications demonstrating Knowledge Studio integration.

## 🚀 Running the Demos

1. Set up your ArcGIS Enterprise connection in `.env`
2. Run Python examples:
```bash
python examples/create_knowledge_graph.py
```

## 📖 Next Steps

After reviewing demos, check out `samples/` for knowledge graph templates and `automation/` for production-ready integration patterns.