#!/usr/bin/env python3
"""
Quick start demo: Create a knowledge graph with sample entities
"""

import os
from dotenv import load_dotenv
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient, Entity


def main():
    """Main execution function"""

    # Load environment variables
    load_dotenv()

    portal_url = os.getenv('ARCGIS_PORTAL_URL')
    username = os.getenv('ARCGIS_USERNAME')
    password = os.getenv('ARCGIS_PASSWORD')

    if not all([portal_url, username, password]):
        print("❌ Error: Missing environment variables")
        print("Please set the following in your .env file:")
        print("  ARCGIS_PORTAL_URL")
        print("  ARCGIS_USERNAME")
        print("  ARCGIS_PASSWORD")
        return

    print("🚀 Initializing ArcGIS Knowledge client...")
    client = ArcGISKnowledgeClient(
        portal_url=portal_url,
        username=username,
        password=password,
        verify_ssl=False
    )

    # Authenticate
    print("🔐 Authenticating with ArcGIS Enterprise...")
    if not client._authenticate():
        print("❌ Authentication failed. Please check your credentials.")
        return

    print("✓ Authentication successful")

    # Create knowledge graph
    print("\n📊 Creating knowledge graph...")
    kg = client.create_knowledge_graph(
        title="Demo Knowledge Graph",
        description="Quick start demo with ArcGIS Knowledge"
    )

    if not kg or not kg.get('id'):
        print("❌ Failed to create knowledge graph")
        return

    print(f"✓ Created knowledge graph: {kg['name']} (ID: {kg['id']})")

    # Add sample entities
    print("\n🏷️  Adding sample entities...")

    # Facility entities
    facilities = [
        Entity(
            name=f"Facility-{i}",
            type_="Facility",
            properties={
                "address": f"123 Enterprise St, Unit {i}",
                "city": "San Francisco",
                "state": "CA",
                "floor_count": 5
            }
        )
        for i in range(1, 4)
    ]

    equipment = [
        Entity(
            name=f"Equipment-{i}",
            type_="Equipment",
            properties={
                "model": f"EQ-200{i}",
                "location": f"Floor {((i % 3) + 1)}, Room {(i % 10)}"
            }
        )
        for i in range(1, 6)
    ]

    tasks = [
        Entity(
            name=f"Maintenance-Task-{i}",
            type_="Maintenance",
            properties={
                "priority": "high" if i % 2 else "medium",
                "status": "pending",
                "description": f"Routine inspection for equipment-{i}"
            }
        )
        for i in range(1, 4)
    ]

    # Add all entities
    for facility in facilities:
        client.add_entity(kg['id'], facility)
    print(f"✓ Added {len(facilities)} facilities")

    for equipment_item in equipment:
        client.add_entity(kg['id'], equipment_item)
    print(f"✓ Added {len(equipment)} equipment items")

    for task in tasks:
        client.add_entity(kg['id'], task)
    print(f"✓ Added {len(tasks)} maintenance tasks")

    # Add relationships
    print("\n🔗 Creating relationships...")
    relationships = 0

    for eq in equipment[:3]:  # First 3 equipment items
        if eq.id:  # Only if successfully added
            facility = facilities[eq.id[-1] if len(eq.id) == 7 else 0]
            rel = client.add_relationship(
                kg['id'],
                facility.id,
                eq.id,
                "located_at"
            )
            relationships += 1

    # Equipment to maintenance relationships
    for i, task in enumerate(tasks[:2]):
        if task.id and i < len(equipment):
            rel = client.add_relationship(
                kg['id'],
                equipment[i].id,
                task.id,
                "requires_maintenance",
                task.properties
            )
            relationships += 1

    print(f"✓ Created {relationships} relationships")

    # Display summary
    print("\n" + "="*50)
    print("✅ Demo completed successfully!")
    print("="*50)
    print(f"Knowledge Graph: {kg['name']}")
    print(f"Total Entities: {len(facilities) + len(equipment) + len(tasks)}")
    print(f"Total Relationships: {relationships}")
    print("\n✓ You can now explore this knowledge graph in ArcGIS Knowledge Studio!")

    # List all entities
    print("\n📋 All entities:")
    all_entities = client.list_entities(kg['id'])
    for entity in all_entities:
        print(f"  - {entity.name} ({entity.type_})")
        if entity.properties:
            keys = list(entity.properties.keys())
            print(f"    Properties: {', '.join(keys)}")


if __name__ == "__main__":
    main()