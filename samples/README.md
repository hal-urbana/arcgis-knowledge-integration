# Knowledge Graph Samples

This directory contains knowledge graph templates, schemas, and sample scenarios for ArcGIS Knowledge.

## 📁 Structure

### templates/
Reusable knowledge graph schema templates and patterns.

### scenarios/
Complete example scenarios with sample data and entities.

## 🏗️ Knowledge Graph Templates

### 1. Facility Management Template
A template for tracking facilities, equipment, and maintenance activities.

### 2. Environmental Monitoring Template
Template for monitoring environmental conditions, sensors, and alerts.

### 3. Supply Chain Template
Template for tracking supply chain entities and relationships.

## 📊 Sample Scenarios

### Scenario: Facility Management
```python
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient
from samples.facility_management import create_facility_management_graph

# Initialize client
client = ArcGISKnowledgeClient(
    portal_url="https://your-portal.arcgis.com",
    username="your-username",
    password="your-password"
)

# Create and populate facility management knowledge graph
kg = create_facility_management_graph(client)
print(f"Created {kg.name} with {len(kg.entities)} entities")
```

## 📖 How to Use Samples

1. Choose a template from `templates/`
2. Copy to your project
3. Customize based on your use case
4. Use the provided Python scripts to populate the knowledge graph

## 🔧 Example Schema

```python
# templates/facility_management_template.py
"""
Template: Facility Management Knowledge Graph

Schema:
- Facility: Buildings, locations
- Equipment: Machines, devices
- Maintenance: Tasks, repairs
- Staff: Employees, operators
"""

FACILITY_TYPES = [
    "Building",
    "Room",
    "Zone",
    "Area"
]

EQUIPMENT_TYPES = [
    "Machine",
    "Sensor",
    "Controller",
    "Device"
]

MAINTENANCE_TYPES = [
    "Routine",
    "Emergency",
    "Preventive"
]

# Entity definitions
FACILITY_ENTITY = {
    "name": "Facility",
    "type": "Facility",
    "properties": {
        "address": str,
        "capacity": int,
        "occupancy": int,
        "status": "active|inactive|under_construction"
    }
}

EQUIPMENT_ENTITY = {
    "name": "Equipment",
    "type": "Equipment",
    "properties": {
        "model": str,
        "location": str,
        "maintenance_date": date,
        "operational_hours": float
    }
}

RELATIONSHIPS = [
    {
        "type": "located_at",
        "schema": {
            "source": "Facility",
            "target": "Equipment",
            "properties": {
                "floor": int,
                "room": str
            }
        }
    },
    {
        "type": "requires_maintenance",
        "schema": {
            "source": "Equipment",
            "target": "Maintenance",
            "properties": {
                "priority": "low|medium|high",
                "scheduled_date": date
            }
        }
    }
]
```