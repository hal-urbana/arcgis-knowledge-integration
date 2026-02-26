# Automation & API Integration

This directory contains Python automation tools and API integration code for working with ArcGIS Knowledge.

## 📁 Structure

### client/
The main ArcGIS Knowledge API client (arcgis_knowledge_client.py) for all client-side operations.

### batch/
Batch operation scripts for processing multiple knowledge graphs or entities at scale.

### webhooks/
Webhook handlers for real-time updates and event-driven workflows.

## 🌐 Python Client

The `ArcGISKnowledgeClient` class provides a full-featured Python API for:

- Authentication with ArcGIS Enterprise
- Creating and managing knowledge graphs
- Adding entities and relationships
- Listing and querying entities
- Batch operations
- Cleanup operations

### Basic Usage

```python
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient

# Initialize client with credentials
client = ArcGISKnowledgeClient(
    portal_url="https://your-portal.arcgis.com",
    username="your-username",
    password="your-password"
)

# Create a knowledge graph
kg = client.create_knowledge_graph(
    title="My Facility Knowledge Graph",
    description="Knowledge graph for facility management"
)

# Add entities
entity = Entity(
    name="Facility-A",
    type_="Facility",
    properties={
        "address": "123 Main St",
        "capacity": 100
    }
)
client.add_entity(kg['id'], entity)

# Create relationships
client.add_relationship(
    kg['id'],
    facility_id,
    equipment_id,
    "located_at"
)
```

## 📦 Batch Operations

See `batch/` for scripts that handle large-scale operations.

## ⚡ Webhooks

See `webhooks/` for real-time event handlers.

## 🔐 Security

- Always use HTTPS in production
- Never hardcode credentials
- Use environment variables or secrets management
- Rotate tokens when needed

## 🔧 Testing

The client includes built-in testing capabilities. See `tests/` for integration tests.

## 📝 API Reference

See docstrings in `arcgis_knowledge_client.py` for complete API documentation.