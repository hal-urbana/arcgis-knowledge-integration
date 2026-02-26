"""
Unit tests for ArcGISKnowledgeClient
"""

import unittest
from unittest.mock import Mock, patch, call
from automation.arcgis_knowledge_client import (
    ArcGISKnowledgeClient,
    Entity,
    Relationship,
    KnowledgeGraph
)


class TestArcGISKnowledgeClient(unittest.TestCase):
    """Test cases for ArcGISKnowledgeClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = ArcGISKnowledgeClient(
            portal_url="https://test.arcgis.com",
            username="testuser",
            password="testpass",
            verify_ssl=False
        )

    def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.portal_url, "https://test.arcgis.com")
        self.assertEqual(self.client.username, "testuser")
        self.assertEqual(self.client.password, "testpass")
        self.assertTrue(self.client.verify_ssl)

    @patch('automation.arcgis_knowledge_client.requests.get')
    def test_authenticate_success(self, mock_get):
        """Test successful authentication"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {'token': 'test-token-123'}
        mock_get.return_value = mock_response

        result = self.client._authenticate()

        self.assertTrue(result)
        self.assertEqual(self.client._auth_token, 'test-token-123')
        mock_get.assert_called_once()

    @patch('automation.arcgis_knowledge_client.requests.get')
    def test_authenticate_failure(self, mock_get):
        """Test failed authentication"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {'error': 'Invalid credentials'}
        mock_get.return_value = mock_response

        result = self.client._authenticate()

        self.assertFalse(result)
        self.assertIsNone(self.client._auth_token)

    def test_get_headers_with_auth(self):
        """Test headers generation with authentication"""
        self.client._auth_token = 'test-token'
        headers = self.client._get_headers()

        self.assertEqual(headers['Authorization'], 'OAuth test-token')
        self.assertEqual(headers['Referer'], 'https://test.arcgis.com')

    def test_get_headers_triggers_auth(self):
        """Test that headers generation triggers authentication"""
        with patch.object(self.client, '_authenticate', return_value=True):
            with patch.object(self.client, '_get_headers'):
                headers = self.client._get_headers()

                self.client._authenticate.assert_called_once()

    def test_create_entity(self):
        """Test entity creation"""
        entity = Entity(
            name="Test Entity",
            type_="TestType",
            properties={"key": "value"}
        )

        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.type_, "TestType")
        self.assertEqual(entity.properties, {"key": "value})
        self.assertIsNone(entity.id)

    def test_relationship_creation(self):
        """Test relationship creation"""
        rel = Relationship(
            source_entity_id="src-123",
            target_entity_id="tgt-456",
            relationship_type="test_rel"
        )

        self.assertEqual(rel.source_entity_id, "src-123")
        self.assertEqual(rel.target_entity_id, "tgt-456")
        self.assertEqual(rel.relationship_type, "test_rel")
        self.assertIsNone(rel.properties)

    def test_knowledge_graph(self):
        """Test KnowledgeGraph creation"""
        kg = KnowledgeGraph(
            id="kg-123",
            name="TestKG",
            description="Test description"
        )

        self.assertEqual(kg.id, "kg-123")
        self.assertEqual(kg.name, "TestKG")
        self.assertEqual(kg.description, "Test description")
        self.assertEqual(len(kg.entities), 0)

    def test_knowledge_graph_with_data(self):
        """Test KnowledgeGraph with entities and relationships"""
        kg = KnowledgeGraph(
            id="kg-123",
            name="TestKG",
            description="Test"
        )

        kg.entities.append(Entity("E1", "Type1", {}))
        kg.relationships.append(Relationship("E1", "E2", "related"))

        self.assertEqual(len(kg.entities), 1)
        self.assertEqual(len(kg.relationships), 1)


if __name__ == '__main__':
    unittest.main()