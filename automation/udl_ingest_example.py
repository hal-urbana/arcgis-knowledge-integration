"""
UDL Ingestion Example
Complete example showing how to set up UDL ingestion into Esri Knowledge
"""

import logging
import os
from typing import Dict, Any
from arcgis_knowledge_client import ArcGISKnowledgeClient
from udl_adapter import UDLAdapter, UDLConfig, UDLMessage
from transformer import Transformer, EsriKnowledgeEntity
from ingest_service import IngestService, IngestConfig


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_complete_workflow():
    """
    Complete example showing entire workflow
    """
    print("\n" + "=" * 70)
    print("UDL → Esri Knowledge Integration - Complete Example")
    print("=" * 70)

    # ============================================
    # STEP 1: Configure ArcGIS Knowledge Connection
    # ============================================
    print("\n[Step 1] Configuring ArcGIS Knowledge connection...")
    arcgis_config: Dict[str, Any] = {
        'portal_url': os.getenv('ARCGIS_PORTAL_URL', 'https://your-portal.arcgis.com'),
        'username': os.getenv('ARCGIS_USERNAME', 'your-username'),
        'password': os.getenv('ARCGIS_PASSWORD', 'your-password')
    }

    client = ArcGISKnowledgeClient(**arcgis_config)

    try:
        print("✓ Connected to ArcGIS Knowledge")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return

    # ============================================
    # STEP 2: Create Knowledge Graph
    # ============================================
    print("\n[Step 2] Creating knowledge graph...")
    kg_name = "UDL Demo Knowledge Graph"
    kg = client.create_knowledge_graph(
        title=kg_name,
        description="Knowledge graph populated from UDL"
    )
    print(f"✓ Created knowledge graph: {kg.id}")

    # ============================================
    # STEP 3: Configure UDL Connection
    # ============================================
    print("\n[Step 3] Configuring UDL connection...")
    udl_config = UDLConfig(
        host=os.getenv('UDL_HOST', 'localhost'),
        port=5672,
        username=os.getenv('UDL_USERNAME', 'guest'),
        password=os.getenv('UDL_PASSWORD', 'guest'),
        virtual_host='/',
        ssl_verify=False
    )
    print("✓ UDL configuration ready")

    # ============================================
    # STEP 4: Subscribe to UDL Topic
    # ============================================
    print("\n[Step 4] Subscribing to UDL topic...")
    topic = os.getenv('UDL_TOPIC', 'udl.demo-topic')
    adapter = UDLAdapter(udl_config)

    try:
        adapter.connect()
        adapter.subscribe_to_topic(topic, auto_ack=False)
        print(f"✓ Subscribed to topic: {topic}")
    except Exception as e:
        print(f"✗ UDL connection/setup failed: {e}")
        return

    # ============================================
    # STEP 5: Define Message Processing
    # ============================================
    print("\n[Step 5] Setting up message transformation...")

    def on_udl_message(message: UDLMessage) -> bool:
        """
        Process a message from UDL
        """
        try:
            # Transform to Esri Knowledge format
            transformer = Transformer(default_entity_type="Feature")
            entity = transformer.transform_message(message)

            if not transformer.validate_entity(entity):
                print(f"⚠ Invalid entity: {entity.name}")
                return False

            # Add to knowledge graph
            client.add_entity(kg_id=kg.id, entity=entity)

            print(f"✓ Ingested: {entity.name} ({entity.id})")
            return True

        except Exception as e:
            print(f"✗ Error processing: {e}")
            return False

    # ============================================
    # STEP 6: Start Ingestion
    # ============================================
    print("\n[Step 6] Starting ingestion...")
    print("Press Ctrl+C to stop\n")

    try:
        adapter.consume_messages(topic=topic, callback=on_udl_message)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        adapter.disconnect()
        print("✓ Ingestion complete")


def example_transform_single_message():
    """
    Example of transforming a single message
    """
    print("\n" + "=" * 70)
    print("UDL Message Transformation Example")
    print("=" * 70)

    # Sample UDL message
    sample_udl_message = UDLMessage(
        body={
            'name': 'Fire Station #42',
            'type': 'Facility',
            'location': {
                'x': -122.676,
                'y': 45.529,
                'spatialReference': {'wkid': 4326}
            },
            'status': 'Active',
            'capacity': 20,
            'last_updated': '2026-02-26T12:00:00Z'
        },
        properties={
            'contentType': 'application/geojson',
            'message_id': 'msg-12345'
        },
        headers={
            'contentType': 'application/geojson',
            'source': 'fire-services'
        }
    )

    # Transform
    transformer = Transformer(default_entity_type="Feature")
    entity = transformer.transform_message(sample_udl_message)

    print("\nOriginal UDL Message:")
    print(f"  Type: {sample_udl_message.body.get('type')}")
    print(f"  Name: {sample_udl_message.body.get('name')}")

    print("\nTransformed Esri Knowledge Entity:")
    print(f"  Type: {entity.type}")
    print(f"  Name: {entity.name}")
    print(f"  Attributes: {list(entity.attributes.keys())}")
    print(f"  Has geometry: {'location' in entity.attributes}")


def example_list_entities():
    """
    Example to list entities in a knowledge graph
    """
    print("\n" + "=" * 70)
    print("List Entities Example")
    print("=" * 70)

    arcgis_config = {
        'portal_url': os.getenv('ARCGIS_PORTAL_URL'),
        'username': os.getenv('ARCGIS_USERNAME'),
        'password': os.getenv('ARCGIS_PASSWORD')
    }

    client = ArcGISKnowledgeClient(**arcgis_config)

    kg_name = input("Enter knowledge graph name to query: ")
    kg_id = input("Enter knowledge graph id: ")

    print(f"\nFetching entities from {kg_name}...")

    try:
        entities = client.list_entities(kg_id)

        print(f"\n✓ Found {len(entities)} entities:")

        for i, entity in enumerate(entities[:10], 1):  # Show first 10
            print(f"\n  [{i}] {entity.name} (Type: {entity.type})")
            if entity.properties:
                print(f"      Properties: {list(entity.properties.keys())}")

        if len(entities) > 10:
            print(f"\n  ... and {len(entities) - 10} more")

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    import sys

    print("\nUDL Ingestion Examples")
    print("Choose an example:")
    print("1. Complete workflow (connect UDL → ingest → Esri Knowledge)")
    print("2. Message transformation only")
    print("3. List entities in a knowledge graph")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        example_complete_workflow()
    elif choice == "2":
        example_transform_single_message()
    elif choice == "3":
        example_list_entities()
    else:
        print("Invalid choice. Running complete workflow...")
        example_complete_workflow()

    print("\nDone!")