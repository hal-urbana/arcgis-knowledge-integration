"""
ArcGIS Knowledge API Client
Python client for interacting with ArcGIS Knowledge REST API
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Entity:
    """Represents a knowledge graph entity"""
    name: str
    type_: str
    properties: Dict[str, any]
    id: Optional[str] = None


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: Dict[str, any] = None


@dataclass
class KnowledgeGraph:
    """Represents a knowledge graph"""
    id: str
    name: str
    description: str
    entities: List[Entity] = None
    relationships: List[Relationship] = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.relationships is None:
            self.relationships = []


class ArcGISKnowledgeClient:
    """
    Client for ArcGIS Knowledge API
    """

    def __init__(
        self,
        portal_url: str,
        username: str,
        password: str,
        verify_ssl: bool = True
    ):
        """
        Initialize client with ArcGIS Enterprise credentials

        Args:
            portal_url: ArcGIS Enterprise portal URL
            username: Portal username
            password: Portal password
            verify_ssl: Whether to verify SSL certificates
        """
        self.portal_url = portal_url
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self._auth_token = None
        self._headers = {}

    def _authenticate(self) -> bool:
        """
        Authenticate with the portal and get access token

        Returns:
            bool: Authentication success
        """
        auth_url = f"{self.portal_url}/sharing/rest/token"
        params = {
            'username': self.username,
            'password': self.password,
            'client': 'requestip',
            'f': 'json'
        }

        response = requests.get(auth_url, params=params, verify=self.verify_ssl)
        data = response.json()

        if data.get('token'):
            self._auth_token = data['token']
            self._headers = {
                'Authorization': f'OAuth {self._auth_token}',
                'Referer': self.portal_url
            }
            return True

        return False

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self._auth_token:
            if not self._authenticate():
                raise ValueError("Authentication failed")

        return self._headers

    def create_knowledge_graph(
        self,
        title: str,
        description: str = "",
        tags: List[str] = None
    ) -> KnowledgeGraph:
        """
        Create a new knowledge graph

        Args:
            title: Knowledge graph title
            description: Knowledge graph description
            tags: List of tags

        Returns:
            KnowledgeGraph: Created knowledge graph
        """
        headers = self._get_headers()

        # Create knowledge graph on the portal
        endpoint = f"{self.portal_url}/sharing/rest/user/createKnowledge"
        params = {
            'title': title,
            'description': description,
            'tags': ','.join(tags) if tags else '',
            'f': 'json'
        }

        response = requests.post(endpoint, params=params, headers=headers, verify=self.verify_ssl)
        data = response.json()

        if data.get('knowledgeId'):
            return KnowledgeGraph(
                id=data['knowledgeId'],
                name=title,
                description=description
            )

        raise ValueError(f"Failed to create knowledge graph: {data}")

    def add_entity(self, kg_id: str, entity: Entity) -> Entity:
        """
        Add an entity to a knowledge graph

        Args:
            kg_id: Knowledge graph ID
            entity: Entity to add

        Returns:
            Entity: Added entity with updated ID
        """
        headers = self._get_headers()

        endpoint = f"{self.portal_url}/sharing/rest/users/" \
                   f"{self.username}/knowledge/{kg_id}/entities"

        params = {
            'f': 'json'
        }

        payload = {
            'name': entity.name,
            'type': entity.type_,
            'properties': entity.properties
        }

        response = requests.post(endpoint, params=params, json=payload, headers=headers, verify=self.verify_ssl)
        data = response.json()

        if data.get('entityId'):
            entity.id = data['entityId']
            return entity

        raise ValueError(f"Failed to add entity: {data}")

    def add_relationship(
        self,
        kg_id: str,
        source_entity_id: str,
        target_entity_id: str,
        rel_type: str,
        properties: Dict[str, any] = None
    ) -> Relationship:
        """
        Create a relationship between two entities

        Args:
            kg_id: Knowledge graph ID
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            rel_type: Type of relationship
            properties: Optional relationship properties

        Returns:
            Relationship: Created relationship
        """
        headers = self._get_headers()

        endpoint = f"{self.portal_url}/sharing/rest/users/" \
                   f"{self.username}/knowledge/{kg_id}/relationships"

        params = {
            'f': 'json'
        }

        payload = {
            'sourceEntity': source_entity_id,
            'targetEntity': target_entity_id,
            'relationshipType': rel_type,
            'properties': properties or {}
        }

        response = requests.post(endpoint, params=params, json=payload, headers=headers, verify=self.verify_ssl)
        data = response.json()

        if data.get('relationshipId'):
            return Relationship(
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                relationship_type=rel_type,
                properties=properties
            )

        raise ValueError(f"Failed to add relationship: {data}")

    def list_entities(self, kg_id: str) -> List[Entity]:
        """
        List all entities in a knowledge graph

        Args:
            kg_id: Knowledge graph ID

        Returns:
            List[Entity]: List of entities
        """
        headers = self._get_headers()

        endpoint = f"{self.portal_url}/sharing/rest/users/" \
                   f"{self.username}/knowledge/{kg_id}/entities"

        params = {
            'f': 'json'
        }

        response = requests.get(endpoint, params=params, headers=headers, verify=self.verify_ssl)
        data = response.json()

        entities = []
        if data.get('entities'):
            for ent_data in data['entities']:
                entities.append(Entity(
                    id=ent_data.get('id'),
                    name=ent_data.get('name'),
                    type_=ent_data.get('type'),
                    properties=ent_data.get('properties', {})
                ))

        return entities

    def delete_knowledge_graph(self, kg_id: str) -> bool:
        """
        Delete a knowledge graph

        Args:
            kg_id: Knowledge graph ID

        Returns:
            bool: Deletion success
        """
        headers = self._get_headers()

        endpoint = f"{self.portal_url}/sharing/rest/users/" \
                   f"{self.username}/knowledge/{kg_id}"

        params = {
            'f': 'json'
        }

        response = requests.delete(endpoint, params=params, headers=headers, verify=self.verify_ssl)
        data = response.json()

        return data.get('success', False)

    def get_knowledge_graph(self, kg_id: str) -> KnowledgeGraph:
        """
        Get details about a knowledge graph

        Args:
            kg_id: Knowledge graph ID

        Returns:
            KnowledgeGraph: Knowledge graph details
        """
        entities = self.list_entities(kg_id)

        return KnowledgeGraph(
            id=kg_id,
            name="",  # Will be populated from API
            description="",
            entities=entities
        )