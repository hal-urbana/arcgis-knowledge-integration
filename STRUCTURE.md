# ArcGIS Knowledge Integration - Repository Structure

```
arcgis-knowledge-integration/
├── README.md                    # Main project documentation
├── STRUCTURE.md                 # This file - repository structure overview
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Docker image definition
├── Makefile                     # Build automation commands
├── requirements.txt             # Python dependencies

├── demo/                        # Demo and integration projects
│   ├── README.md               # Demo documentation
│   └── examples/               # Example scripts
│       └── create_knowledge_graph.py  # Quick start knowledge graph demo

├── samples/                     # Knowledge graph samples
│   ├── README.md              # Samples documentation
│   └── facility_management.py # Facility management sample demo

├── automation/                  # Automation and API integration
│   ├── README.md              # Automation documentation
│   └── arcgis_knowledge_client.py  # Main API client

├── scripts/                     # Setup and deployment scripts
│   ├── setup.sh               # Environment setup script
│   └── deploy.sh              # Deployment script

└── tests/                       # Unit tests
    └── test_arcgis_knowledge_client.py  # Client unit tests
```

## Project Deliverables

✓ **Demo/Integration Project:**
- Quick start demo to create knowledge graphs with sample entities
- Example usage scripts

✓ **Knowledge Graph Samples:**
- Complete facility management sample with entities
- Relationship patterns and templates

✓ **Automation & API Integration:**
- Full-featured Python client for ArcGIS Knowledge API
- Authentication, CRUD operations, batch operations
- Data models: Entity, Relationship, KnowledgeGraph

✓ **Repository Structure:**
- Comprehensive setup and deployment scripts
- Docker container configuration
- Test suite
- Documentation and examples

## Setup Instructions

```bash
# Clone the repository
git clone https://github.com/hal-urbana/arcgis-knowledge-integration.git
cd arcgis-knowledge-integration

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your ArcGIS Enterprise credentials

# Run setup script (optional, can use pip install directly)
./scripts/setup.sh

# Run the demo
python -m demo.examples.create_knowledge_graph
```