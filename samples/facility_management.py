"""
Facility Management Knowledge Graph Samples

Complete demo scenario for creating a facility management knowledge graph
"""

from typing import List, Dict, Any
from automation.arcgis_knowledge_client import ArcGISKnowledgeClient, Entity, Relationship


class FacilityManagementSample:
    """Factory for creating facility management knowledge graph samples"""

    def __init__(self, client: ArcGISKnowledgeClient):
        self.client = client

    def create_facilities(
        self,
        count: int = 10,
        kg_id: str = None
    ) -> List[Entity]:
        """
        Create sample facilities

        Args:
            count: Number of facilities to create
            kg_id: Knowledge graph ID (defaults to current knowledge graph)

        Returns:
            List[Entity]: Created facility entities
        """
        facilities = []
        for i in range(1, count + 1):
            facility = Entity(
                name=f"Facility-{i:03d}",
                type_="Facility",
                properties={
                    "address": f"123 Enterprise Drive, Unit {i}",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94105",
                    "capacity": random.randint(50, 500),
                    "occupancy": random.randint(20, 450),
                    "status": random.choice(["active", "operational", "inactive"]),
                    "floor_count": random.randint(3, 10),
                    "construction_year": random.randint(1990, 2020)
                }
            )
            facilities.append(self.client.add_entity(kg_id, facility))

        return facilities

    def create_equipment(
        self,
        facilities: List[Entity],
        count_per_facility: int = 3,
        kg_id: str = None
    ) -> List[Entity]:
        """
        Create sample equipment for each facility

        Args:
            facilities: List of facility entities
            count_per_facility: Number of equipment items per facility
            kg_id: Knowledge graph ID

        Returns:
            List[Entity]: Created equipment entities
        """
        equipment_list = []
        equipment_types = ["HVAC System", "Server Rack", "Sensor", "Security Camera", "Network Switch", "Generator"]

        for facility in facilities:
            for i in range(count_per_facility):
                # Determine location within facility
                floor = random.randint(1, facility.properties.get('floor_count', 5))
                location = f"Floor {floor}, Room {random.randint(1, 10)}"

                equipment = Entity(
                    name=f"{facility.name}-{equipment_types[i % len(equipment_types)]}-{i+1}",
                    type_="Equipment",
                    properties={
                        "model": f"EQ-{random.randint(1000, 9999)}",
                        "location": location,
                        "installation_date": random_date(start_year=2005),
                        "operational_hours": round(random.uniform(0, 50000), 2),
                        "maintenance_due_date": random_date(start_year=2026),
                        "status": random.choice(["operational", "maintenance", "error"])
                    }
                )
                equipment_list.append(self.client.add_entity(kg_id, equipment))

        return equipment_list

    def create_maintenance_tasks(
        self,
        equipment: List[Entity],
        count: int = 10,
        kg_id: str = None
    ) -> List[Entity]:
        """
        Create sample maintenance tasks

        Args:
            equipment: List of equipment entities
            count: Number of maintenance tasks to create
            kg_id: Knowledge graph ID

        Returns:
            List[Entity]: Created maintenance task entities
        """
        maintenance_types = ["Routine Inspection", "Preventive Maintenance", "Emergency Repair", "Software Update"]
        priorities = ["low", "medium", "high", "critical"]

        tasks = []
        for i in range(count):
            equipment_item = random.choice(equipment)

            task = Entity(
                name=f"Maintenance-Task-{i+1}",
                type_="Maintenance",
                properties={
                    "task_type": random.choice(maintenance_types),
                    "description": f"Schedule and perform maintenance for {equipment_item.name}",
                    "scheduled_date": random_date(start_year=2026),
                    "completed_date": random.choice([None, random_date(start_year=2026)]),
                    "priority": random.choice(priorities),
                    "technician": f"TCH-0{i+1:02d}",
                    "status": random.choice(["pending", "in_progress", "completed", "cancelled"])
                }
            )
            tasks.append(self.client.add_entity(kg_id, task))

        return tasks

    def create_relationships(
        self,
        facilities: List[Entity],
        equipment: List[Entity],
        tasks: List[Entity],
        kg_id: str = None
    ) -> List[Relationship]:
        """
        Create relationships between entities

        Args:
            facilities: List of facility entities
            equipment: List of equipment entities
            tasks: List of maintenance task entities
            kg_id: Knowledge graph ID

        Returns:
            List[Relationship]: Created relationships
        """
        relationships = []

        # Equipment located at facilities
        for eq in equipment:
            # Find which facility it's in
            location = eq.properties.get('location', '')
            if 'Floor' in location or 'Room' in location:
                facility = random.choice(facilities)
                rel = self.client.add_relationship(
                    kg_id,
                    facility.id,
                    eq.id,
                    "located_at",
                    {
                        "floor": int(location.split('Floor')[1].split(',')[0]) if 'Floor' in location else 1
                    }
                )
                relationships.append(rel)

        # Equipment requires maintenance
        for task in tasks[:len(equipment) * 2]:  # Limit to avoid over-relating
            equipment_item = random.choice(equipment)
            rel = self.client.add_relationship(
                kg_id,
                equipment_item.id,
                task.id,
                "requires_maintenance",
                task.properties.copy()
            )
            relationships.append(rel)

        return relationships

    def create_complete_facility_graph(
        self,
        facility_count: int = 10,
        equipment_per_facility: int = 3,
        maintenance_count: int = 10
    ) -> KnowledgeGraph:
        """
        Create a complete facility management knowledge graph

        Args:
            facility_count: Number of facilities
            equipment_per_facility: Equipment per facility
            maintenance_count: Maintenance tasks

        Returns:
            KnowledgeGraph: Complete knowledge graph
        """
        kg = self.create_facilities(facility_count, kg_id=None)
        print(f"Created {len(kg)} facilities")

        equipment = self.create_equipment(kg, equipment_per_facility, kg_id=None)
        print(f"Created {len(equipment)} equipment items")

        tasks = self.create_maintenance_tasks(equipment, maintenance_count, kg_id=None)
        print(f"Created {len(tasks)} maintenance tasks")

        relationships = self.create_relationships(kg, equipment, tasks, kg_id=None)
        print(f"Created {len(relationships)} relationships")

        return kg


def random_date(start_year: int = 2000) -> str:
    """Generate a random date string"""
    import random
    import datetime
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(2026, 12, 31)
    delta = datetime.timedelta(days=random.randint(0, (end_date - start_date).days))
    return (start_date + delta).isoformat()


def create_facility_management_graph(
    client: ArcGISKnowledgeClient,
    facility_count: int = 10,
    equipment_per_facility: int = 3,
    maintenance_count: int = 10
) -> KnowledgeGraph:
    """
    Convenience function to create a complete facility management knowledge graph

    Args:
        client: ArcGIS Knowledge client
        facility_count: Number of facilities to create
        equipment_per_facility: Equipment items per facility
        maintenance_count: Maintenance tasks

    Returns:
        KnowledgeGraph: Complete knowledge graph
    """
    sample = FacilityManagementSample(client)
    return sample.create_complete_facility_graph(
        facility_count=facility_count,
        equipment_per_facility=equipment_per_facility,
        maintenance_count=maintenance_count
    )


if __name__ == "__main__":
    # Example usage
    from automation.arcgis_knowledge_client import ArcGISKnowledgeClient

    client = ArcGISKnowledgeClient(
        portal_url="https://your-portal.arcgis.com",
        username="your-username",
        password="your-password"
    )

    kg = create_facility_management_graph(client)
    print(f"\n✓ Created {kg.name} with {len(kg.entities)} entities and {len(kg.relationships)} relationships")