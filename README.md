# ArcGIS Knowledge Integration

A comprehensive toolkit for integrating with Esri's ArcGIS Knowledge platform - an enterprise knowledge graph tool built for ArcGIS Enterprise.

## Overview

This repository provides demo projects, knowledge graph samples, and automation utilities for working with ArcGIS Knowledge.

## 🎯 What's Included

### 1. Demo / Integration Project (`demo/`)
- Sample ArcGIS Pro projects demonstrating knowledge graph creation
- Integration patterns for connecting to ArcGIS Enterprise
- UI demo examples using Knowledge Studio

### 2. Knowledge Graph Samples (`samples/`)
- Example knowledge graph schemas and templates
- Sample entities, relationships, and properties
- Pre-built knowledge graph scenarios (e.g., facility management, environmental monitoring)

### 3. Automation & API Integration (`automation/`)
- Python client for ArcGIS Knowledge REST API
- Batch operations scripts
- Webhook handlers for real-time updates
- Git hooks for knowledge graph versioning

### 4. Infrastructure & Setup (`scripts/`)
- Automated deployment scripts for ArcGIS Knowledge
- Configuration templates for Docker/Kubernetes
- Environment setup and dependency management

## 🚀 Quick Start

### Prerequisites
- ArcGIS Enterprise with ArcGIS Knowledge Server installed
- ArcGIS Pro (for desktop operations)
- Python 3.9+
- Docker (for containerized deployments)

### Installation

1. Clone this repository:
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
# Edit .env with your ArcGIS Enterprise credentials
```

## 📖 Usage Examples

### Python Client
```python
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient

client = ArcGISKnowledgeClient(
    portal_url="https://your-portal.arcgis.com",
    username="your-username",
    password="your-password"
)

# Create a new knowledge graph
kg = client.create_knowledge_graph(
    title="Facility Management KG",
    description="Knowledge graph for facility tracking"
)
```

### Knowledge Graph Schema
```python
from samples.factories import KnowledgeGraphFactory

kg_factory = KnowledgeGraphFactory(client)
kg = kg_factory.create_facility_management_graph()
```

## 📋 Project Structure

```
arcgis-knowledge-integration/
├── demo/                   # Demo projects
│   ├── pro_projects/       # ArcGIS Pro project files
│   ├── examples/           # Integration examples
│   └── README.md
├── samples/                # Knowledge graph samples
│   ├── templates/          # Schema templates
│   ├── scenarios/          # Scenario-based samples
│   └── README.md
├── automation/             # Automation scripts
│   ├── client/             # Python API client
│   ├── batch/              # Batch operations
│   ├── webhooks/           # Webhook handlers
│   └── README.md
├── scripts/                # Setup and deployment
│   ├── setup.sh           # Automated setup
│   ├── deploy.sh          # Deployment script
│   └── README.md
├── tests/                  # Unit tests
├── docs/                   # Additional documentation
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image
└── Makefile               # Build automation
```

## 🔧 ArcGIS Knowledge Setup

For detailed setup instructions, see:
- [Esri Documentation](https://enterprise.arcgis.com/en/server/latest/manage/install-arcgis-knowledge/)
- [Knowledge Studio Guide](https://enterprise.arcgis.com/en/knowledge/latest/knowledge-studio/get-started-with-knowledge-studio.htm)

## 📚 Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## 📄 License

[Your License Here]

## 🤝 Support

For ArcGIS Knowledge support, contact Esri Support or check:
- [Esri Knowledge Base](https://support.esri.com/en-us/knowledge-base)
- [ArcGIS Community](https://community.esri.com/)

## 🔗 Related Resources

- [ArcGIS Enterprise Documentation](https://enterprise.arcgis.com/)
- [ArcGIS Pro Help](https://pro.arcgis.com/en/pro-app/latest/help/)
- [Esri Developer Portal](https://developers.arcgis.com/)

---

**Repository owner:** hal-urbana
**Created:** 2026-02-26
**Status:** Active Development