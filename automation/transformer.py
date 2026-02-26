"""
Transformation Layer
Maps UDL messages to Esri Knowledge format
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import uuid


logger = logging.getLogger(__name__)


@dataclass
class EsriKnowledgeEntity:
    """Represents an entity in Esri Knowledge"""
    name: str
    type: str
    attributes: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class EsriKnowledgeRelationship:
    """Represents a relationship in Esri Knowledge"""
    source_entity: str
    target_entity: str
    relationship_type: str
    attributes: Dict[str, Any]


class TransformationError(Exception):
    """Base class for transformation errors"""
    pass


class Transformer:
    """
    Transforms UDL messages into Esri Knowledge format
    """

    def __init__(self, default_entity_type: str = "Feature"):
        """
        Initialize transformer with default entity type

        Args:
            default_entity_type: Default entity type for unknown message types
        """
        self.default_entity_type = default_entity_type

    def transform_message(
        self,
        udl_message
    ) -> Optional[EsriKnowledgeEntity]:
        """
        Transform a UDL message to Esri Knowledge entity

        Args:
            udl_message: UDLMessage object to transform

        Returns:
            EsriKnowledgeEntity or None if transformation fails
        """
        try:
            body = udl_message.body
            headers = udl_message.headers
            properties = udl_message.properties

            # Determine entity type from message metadata or body
            entity_type = self._determine_entity_type(
                body, headers, properties
            )

            # Create entity attributes from message content
            attributes = self._create_attributes(body, headers, properties)

            # Generate entity ID if not provided
            entity_id = attributes.get('id') or attributes.get('objectId') or str(uuid.uuid4())

            # Create Esri Knowledge entity
            return EsriKnowledgeEntity(
                name=attributes.get('name', entity_id),
                type=entity_type,
                attributes=attributes,
                id=entity_id
            )

        except Exception as e:
            logger.error(f"Failed to transform message: {e}")
            logger.debug(f"Raw message: {udl_message}")
            raise TransformationError(f"Transformation failed: {e}")

    def _determine_entity_type(
        self,
        body: Dict[str, Any],
        headers: Dict[str, Any],
        properties: Dict[str, Any]
    ) -> str:
        """
        Determine entity type from message metadata or body

        Args:
            body: Message body
            headers: Message headers
            properties: Message properties

        Returns:
            str: Entity type
        """
        # Check headers first
        if 'contentType' in headers:
            content_type = headers['contentType']
            # Map known content types
            content_type_map = {
                'application/geo+json': 'Feature',
                'application/geojson': 'Feature',
                'application/json': 'Feature',
                'application/vnd.geo+json': 'Feature'
            }
            if content_type in content_type_map:
                return content_type_map[content_type]

        # Check body
        if 'type' in body:
            return body['type']

        # Check properties
        if 'type' in properties:
            return properties['type']

        # Check headers for entity type indication
        if 'entityType' in headers:
            return headers['entityType']

        # Default to configured default
        return self.default_entity_type

    def _create_attributes(
        self,
        body: Dict[str, Any],
        headers: Dict[str, Any],
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create attributes dict from message content

        Args:
            body: Message body
            headers: Message headers
            properties: Message properties

        Returns:
            Dict[str, Any]: Entity attributes
        """
        attributes = {}

        # Extract id/objectId from body
        id_fields = ['id', 'ObjectId', 'objectId', 'objectid', 'object_id']
        for field in id_fields:
            if field in body:
                attributes['id'] = body[field]
                break

        # Extract name/title from body
        name_fields = ['name', 'title', 'Title', 'Name', 'name_field']
        for field in name_fields:
            if field in body:
                attributes['name'] = body[field]
                break

        # Extract location/crs if present
        if 'location' in body:
            attributes['location'] = body['location']

        if 'crs' in body:
            attributes['crs'] = body['crs']

        if 'geometry' in body:
            attributes['geometry'] = body['geometry']

        # Process all top-level fields as attributes
        for key, value in body.items():
            # Skip fields that have their own semantic meaning
            if key in ['id', 'name', 'type', 'location', 'crs', 'geometry']:
                continue

            # Skip metadata fields
            if key in ['metadata', 'meta', '_meta', 'original_headers']:
                continue

            # Convert to string for attributes if needed
            # UDL may send complex objects as strings
            if isinstance(value, dict):
                attributes[key] = str(value)
            elif isinstance(value, list):
                attributes[key] = str(value)
            else:
                attributes[key] = value

        # Add metadata to attributes
        if headers:
            attributes['_headers'] = {k: str(v) for k, v in headers.items()}

        if properties:
            attributes['_properties'] = {k: str(v) for k, v in properties.items()}

        return attributes

    def enrich_entity(
        self,
        entity: EsriKnowledgeEntity,
        enrichment_data: Optional[Dict[str, Any]] = None
    ) -> EsriKnowledgeEntity:
        """
        Enrich entity with additional data

        Args:
            entity: Entity to enrich
            enrichment_data: Additional data to add

        Returns:
            EsriKnowledgeEntity: Enriched entity
        """
        if enrichment_data:
            entity.attributes.update(enrichment_data)

        return entity

    def validate_entity(self, entity: EsriKnowledgeEntity) -> bool:
        """
        Validate entity before submission

        Args:
            entity: Entity to validate

        Returns:
            bool: Valid or not
        """
        # Must have at least name or id
        if not entity.attributes.get('name') and not entity.attributes.get('id'):
            logger.error(f"Entity missing name and id: {entity}")
            return False

        return True