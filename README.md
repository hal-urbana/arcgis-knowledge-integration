# ArcGIS Knowledge Integration

A comprehensive toolkit for integrating with Esri's ArcGIS Knowledge platform, featuring both direct API integration and UDL (Unified Data Library) message broker ingestion.

**Repository:** https://github.com/hal-urbana/arcgis-knowledge-integration
**Created:** 2026-02-26
**Status:** Active Development

## 🎯 What's Included

### 1. Python API Client (`automation/arcgis_knowledge_client.py`)
- Full-featured client for ArcGIS Knowledge REST API
- Authentication with ArcGIS Enterprise via OAuth2
- CRUD operations for knowledge graphs, entities, and relationships
- Data models: Entity, Relationship, KnowledgeGraph
- Batch operation support with async capabilities
- Comprehensive error handling and logging

### 2. UDL Ingestion Pipeline (`automation/`)
A complete pipeline for real-time data movement from UDL message broker to ArcGIS Knowledge:

| Component | Description |
|-----------|-------------|
| `udl_adapter.py` | UDL message broker adapter (TLS, topic subscription, connection management) |
| `transformer.py` | Data transformation layer (UDL ↦ Knowledge entity mapping) |
| `ingest_service.py` | Core ingestion service with batching, backpressure, retry logic |
| `udl_ingest_example.py` | Complete workflow demonstration |
| `udl_ingest_demo.py` | Configuration examples and demo scripts |

### 3. Knowledge Graph Samples (`samples/`)
- Facility management example with entities, relationships, and templates
- Entity types: Facilities, Equipment, Maintenance Tasks
- Relationship patterns and schemas
- `samples/facility_management.py` - Complete end-to-end example

### 4. Demo Projects (`demo/`)
- `demo/udl_ingest_demo.py` - UDL ingestion demonstration
- Integration examples for working with ArcGIS Knowledge

### 5. Infrastructure & Setup (`scripts/`)
- `scripts/setup.sh` - Automated dependency setup
- `scripts/deploy.sh` - Docker/Kubernetes deployment
- Plus requirements.txt, Dockerfile, .env.example, Makefile, and test suite

## 🚀 Quick Start

### Prerequisites
- ArcGIS Enterprise with ArcGIS Knowledge Server (10.9+)
- Python 3.9+
- Docker (for container deployments)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hal-urbana/arcgis-knowledge-integration.git
cd arcgis-knowledge-integration
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your ArcGIS Enterprise credentials:
# - AGS_PORTAL_URL
# - AGS_USERNAME
# - AGS_PASSWORD or AGS_TOKEN
# - (Optional) UDL configuration settings
```

## 📖 Usage

### Python Client - Basic Usage
```python
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient

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
entity = {
    "name": "Facility-A",
    "type_": "Facility",
    "properties": {
        "address": "123 Main St",
        "capacity": 100
    }
}
client.add_entity(kg['id'], entity)

# Create relationships
client.add_relationship(
    kg['id'],
    facility_id,
    equipment_id,
    "located_at"
)
```

### UDL Ingestion Pipeline

The UDL → ArcGIS Knowledge pipeline enables real-time data ingestion:

```python
from automation.ingest_service import create_ingest_service_from_config

service = create_ingest_service_from_config(
    udl_host='udl.example.com',
    udl_topic='udl.some-topic',
    arcgis_url='https://portal.example.com',
    arcgis_username='user',
    arcgis_password='password',
    knowledge_graph_name='UDL Ingested Data'
)

# Service auto-manages connection, batching, and error handling
# View statistics and status at any time
```

For detailed examples:
- See `automation/udl_ingest_example.py` for complete workflow
- See `demo/udl_ingest_demo.py` for configuration demos

### Knowledge Graph Samples

```python
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient
from samples.facility_management import create_facility_management_graph

client = ArcGISKnowledgeClient(
    portal_url="https://your-portal.arcgis.com",
    username="your-username",
    password="your-password"
)

# Create and populate a facility management knowledge graph
kg = create_facility_management_graph(client)
print(f"Created {kg.name} with {len(kg.entities)} entities")
```

## 📋 Directory Structure

```
arcgis-knowledge-integration/
├── README.md                      # This file
├── STRUCTURE.md                   # Detailed repository structure
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker image definition
├── Makefile                       # Build automation
├── requirements.txt               # Python dependencies

├── automation/                    # API client & UDL pipeline
│   ├── arcgis_knowledge_client.py # Main API client
│   ├── udl_adapter.py            # Message broker adapter
│   ├── transformer.py            # Data transformation layer
│   ├── ingest_service.py         # Ingestion orchestration
│   ├── udl_ingest_example.py     # Integration example
│   └── udl_ingest_demo.py        # Demo scripts
├── demo/                         # Demo projects
│   ├── udl_ingest_demo.py        # UDL ingestion demo
│   └── README.md                 # Demo documentation
├── samples/                      # Knowledge graph samples
│   ├── facility_management.py    # Facility management example
│   └── README.md                 # Samples documentation
├── scripts/                      # Setup & deployment
│   ├── setup.sh                  # Environment setup
│   └── deploy.sh                 # Deployment script
└── tests/                        # Unit tests
    └── test_arcgis_knowledge_client.py
```

## 🔧 UDL Pipeline Architecture

See `STRUCTURE.md` for design documentation:
- Data flow from UDL message broker → Transformer → ArcGIS Knowledge
- Connection pooling and backpressure handling
- Retry logic and error recovery
- Statistics and monitoring

**Related documentation:** `../../udl-esri-pipeline-design.md`

## 📚 UDL Components Deep Dive

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| **UDLAdapter** | Connects to UDL topic and processes messages | TLS authentication, topic subscription, health monitoring |
| **Transformer** | Maps UDL payload to Knowledge entity format | Schema validation, transformation rules |
| **IngestService** | Orchestrates ingestion workflow | Batching, retry, backpressure, statistics |

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest tests/ --cov=automation --cov-report=html
```

## 📅 Project Deliverables

✓ Python API client with OAuth2 authentication
✓ UDL → ArcGIS Knowledge ingestion pipeline (4 components)
✓ Knowledge graph sample (facility management)
✓ Demo projects and examples
✓ Automation scripts (setup, deploy)
✓ Docker and Makefile support
✓ Test suite

## 🔐 Security Best Practices

- Always use HTTPS in production environments
- Never hardcode credentials; use `.env` or secrets management
- Rotate OAuth tokens regularly
- Enable TLS for UDL connections
- Use Python virtual environments for development

## 📖 Contributing

Contributions welcome! See `CONTRIBUTING.md` for guidelines.

## 📄 License

[License TBD]

## 🤝 Support

For ArcGIS Knowledge support, contact Esri or see:
- [Esri Knowledge Base](https://support.esri.com/en-us/knowledge-base)
- [ArcGIS Community](https://community.esri.com/)

## 🔗 Related Resources

- [Esri ArcGIS Knowledge Documentation](https://enterprise.arcgis.com/en/server/latest/manage/manage-arcgis-knowledge/)
- [Knowledge Studio Guide](https://enterprise.arcgis.com/en/knowledge/latest/knowledge-studio/get-started-with-knowledge-studio.htm)
- [Esri Developer Portal](https://developers.arcgis.com/)

---

**Repository owner:** hal-urbana
**Created:** 2026-02-26
**Status:** Production-Ready Core | Testing Required for UDL Integration